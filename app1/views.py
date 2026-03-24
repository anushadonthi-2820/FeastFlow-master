import uuid

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from app1.models import Cart, Fooditem, Order


def get_user_cart_items(user):
    return Cart.objects.filter(user=user).select_related("item").order_by("id")


def get_cart_total(cart_items):
    return sum(cart_item.item.price * cart_item.quantity for cart_item in cart_items)


def get_razorpay_client():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        return None
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_orders_from_cart(user, pending_order, payment_method, payment_status, transaction_id, razorpay_order_id="", razorpay_signature=""):
    order_items = list(get_user_cart_items(user))
    created_order_ids = []

    for cart_item in order_items:
        order = Order.objects.create(
            usern=user,
            items=cart_item,
            item=cart_item.item,
            quantity=cart_item.quantity,
            price_at_purchase=cart_item.item.price,
            addr=pending_order["addr"],
            phno=pending_order["phno"],
            payment_method=payment_method,
            payment_status=payment_status,
            transaction_id=transaction_id,
            razorpay_order_id=razorpay_order_id,
            razorpay_signature=razorpay_signature,
        )
        created_order_ids.append(order.id)

    Cart.objects.filter(user=user).delete()
    return created_order_ids


def render_home(request):
    search_query = request.POST.get("ser")
    if search_query:
        all_items = Fooditem.objects.filter(itemname__icontains=search_query)
    else:
        all_items = Fooditem.objects.all()

    if request.method == "POST" and not search_query:
        items = request.POST.get("items")
        all_items = Fooditem.objects.filter(itemtype=items)

    return render(request, "home.html", {"all": all_items})


@login_required(login_url="userlogin")
def add_cart(request, rid):
    obj = get_object_or_404(Fooditem, id=rid)
    cart_item, created = Cart.objects.get_or_create(user=request.user, item=obj, defaults={"quantity": 1})
    if not created:
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"{cart_item.item.itemname} quantity updated in your cart :)")
    else:
        messages.success(request, f"{cart_item.item.itemname} successfully added to the cart :)")
    return redirect("home")


def render_item_reg(request):
    if request.method == "POST":
        itempic = request.FILES.get("itempic")
        itemname = request.POST.get("itemname")
        price = request.POST.get("price")
        itemtype = request.POST.get("itemtype")
        rating = request.POST.get("rating")
        availability = request.POST.get("availability")
        try:
            rating = float(rating)
        except (TypeError, ValueError):
            messages.error(request, "Please enter rating as a decimal number, for example 4.5.")
            return redirect("itemreg")
        obj = Fooditem(
            itempic=itempic,
            itemname=itemname,
            price=price,
            itemtype=itemtype,
            rating=rating,
            availability=availability,
        )
        obj.save()
        messages.success(request, f"{itemname} successfully added to the menu :) please add more")
        return redirect("itemreg")
    return render(request, "item_register.html")


def render_user_login(request):
    if request.method == "POST":
        uname = request.POST.get("uname")
        pword = request.POST.get("pword")
        obj = authenticate(username=uname, password=pword)
        if obj:
            login(request, obj)
            messages.success(request, "You are successfully logged in")
            return redirect("home")
        messages.error(request, "Please enter valid credentials")
        return redirect("userlogin")
    return render(request, "user_login.html")


def render_user_reg(request):
    if request.method == "POST":
        uname = request.POST.get("uname")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        emailid = request.POST.get("emailid")
        pword = request.POST.get("pword")
        cpword = request.POST.get("cpword")
        if User.objects.filter(username=uname).exists():
            messages.warning(request, f"@{uname} already exists :( please try another username")
            return redirect("userreg")
        if pword != cpword:
            messages.error(request, "The passswords don't match")
            return redirect("userreg")
        obj = User(username=uname, first_name=fname, last_name=lname, email=emailid)
        obj.set_password(pword)
        obj.save()
        messages.success(request, f"@{uname} successfully registered, please login to continue")
        return redirect("userlogin")
    return render(request, "user_register.html")


def render_single(request, rid):
    obj = get_object_or_404(Fooditem, id=rid)
    return render(request, "single.html", {"obj": obj})


def logout_user(request):
    if request.user.is_authenticated:
        request.session.pop("pending_order", None)
        request.session.pop("recent_order_ids", None)
        request.session.pop("razorpay_checkout", None)
    logout(request)
    return redirect("userlogin")


@login_required(login_url="userlogin")
def render_show_cart(request):
    all_items = list(get_user_cart_items(request.user))
    total = get_cart_total(all_items)
    return render(request, "cart.html", {"all": all_items, "total": total})


@login_required(login_url="userlogin")
def empty_cart(request):
    Cart.objects.filter(user=request.user).delete()
    request.session.pop("pending_order", None)
    request.session.pop("razorpay_checkout", None)
    return redirect("showcart")


@login_required(login_url="userlogin")
def remove_item(request, rid):
    obj = get_object_or_404(Cart, id=rid, user=request.user)
    if obj.quantity > 1:
        obj.quantity -= 1
        obj.save()
    else:
        obj.delete()
    return redirect("showcart")

@login_required(login_url="userlogin")
def render_order(request):
    order_items = list(get_user_cart_items(request.user))
    if not order_items:
        messages.warning(request, "Your cart is empty. Add items before checkout.")
        return redirect("showcart")

    if request.method == "POST":
        addr = (request.POST.get("addr") or "").strip()
        phno = (request.POST.get("phno") or "").strip()
        if not addr or not phno:
            messages.error(request, "Please enter both address and phone number.")
            return redirect("order")
        if not phno.isdigit() or len(phno) != 10:
            messages.error(request, "Please enter a valid 10 digit phone number.")
            return redirect("order")

        request.session["pending_order"] = {"addr": addr, "phno": phno}
        return redirect("payment")

    return render(
        request,
        "order.html",
        {"total": get_cart_total(order_items), "cart_items": order_items},
    )


@login_required(login_url="userlogin")
def render_payment(request):
    order_items = list(get_user_cart_items(request.user))
    pending_order = request.session.get("pending_order")

    if not order_items:
        messages.warning(request, "Your cart is empty. Add items before making a payment.")
        return redirect("showcart")
    if not pending_order:
        messages.warning(request, "Please enter your delivery details before payment.")
        return redirect("order")

    total = get_cart_total(order_items)
    total_paise = int(total * 100)
    checkout_data = request.session.get("razorpay_checkout")

    if request.method == "POST":
        transaction_id = f"FF-COD-{uuid.uuid4().hex[:10].upper()}"
        created_order_ids = create_orders_from_cart(
            request.user,
            pending_order,
            payment_method="cod",
            payment_status="pending",
            transaction_id=transaction_id,
        )
        request.session.pop("pending_order", None)
        request.session.pop("razorpay_checkout", None)
        request.session["recent_order_ids"] = created_order_ids
        messages.success(request, "Order placed successfully. Please pay on delivery.")
        return redirect("ordered")

    if not checkout_data or checkout_data.get("amount") != total_paise:
        client = get_razorpay_client()
        if client:
            try:
                razorpay_order = client.order.create(
                    {
                        "amount": total_paise,
                        "currency": "INR",
                        "payment_capture": 1,
                        "notes": {
                            "username": request.user.username,
                            "phone": pending_order["phno"],
                        },
                    }
                )
                checkout_data = {
                    "order_id": razorpay_order["id"],
                    "amount": total_paise,
                }
                request.session["razorpay_checkout"] = checkout_data
            except Exception:
                checkout_data = None
                request.session.pop("razorpay_checkout", None)
                messages.warning(request, "Razorpay order could not be created right now. You can still use cash on delivery.")
        else:
            checkout_data = None
            messages.warning(request, "Razorpay keys are not configured yet. Cash on delivery is available.")

    return render(
        request,
        "payment.html",
        {
            "cart_items": order_items,
            "total": total,
            "delivery": pending_order,
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": checkout_data["order_id"] if checkout_data else "",
            "razorpay_amount": checkout_data["amount"] if checkout_data else total_paise,
            "razorpay_ready": bool(checkout_data and settings.RAZORPAY_KEY_ID),
        },
    )


@login_required(login_url="userlogin")
@require_POST
def verify_payment(request):
    pending_order = request.session.get("pending_order")
    checkout_data = request.session.get("razorpay_checkout")
    order_items = list(get_user_cart_items(request.user))

    if not pending_order or not checkout_data or not order_items:
        messages.error(request, "Your payment session has expired. Please try again.")
        return redirect("payment")

    razorpay_order_id = request.POST.get("razorpay_order_id", "")
    razorpay_payment_id = request.POST.get("razorpay_payment_id", "")
    razorpay_signature = request.POST.get("razorpay_signature", "")

    if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
        messages.error(request, "Payment details were incomplete. Please try again.")
        return redirect("payment")

    if razorpay_order_id != checkout_data.get("order_id"):
        messages.error(request, "Payment order mismatch detected. Please try again.")
        return redirect("payment")

    client = get_razorpay_client()
    if not client:
        messages.error(request, "Razorpay is not configured on the server.")
        return redirect("payment")

    try:
        client.utility.verify_payment_signature(
            {
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            }
        )
    except Exception:
        messages.error(request, "Razorpay payment verification failed.")
        return redirect("payment")

    created_order_ids = create_orders_from_cart(
        request.user,
        pending_order,
        payment_method="online",
        payment_status="paid",
        transaction_id=razorpay_payment_id,
        razorpay_order_id=razorpay_order_id,
        razorpay_signature=razorpay_signature,
    )
    request.session.pop("pending_order", None)
    request.session.pop("razorpay_checkout", None)
    request.session["recent_order_ids"] = created_order_ids
    messages.success(request, "Razorpay payment verified and order placed successfully :D")
    return redirect("ordered")


@login_required(login_url="userlogin")
def render_ordered(request):
    order_ids = request.session.get("recent_order_ids", [])
    all_orders = list(
        Order.objects.filter(usern=request.user, id__in=order_ids).select_related("item").order_by("id")
    )
    if not all_orders:
        messages.warning(request, "No recent order found. Please place an order first.")
        return redirect("showcart")

    total = sum(order.price_at_purchase * order.quantity for order in all_orders)
    obj = all_orders[0]
    return render(request, "ordered.html", {"all": all_orders, "total": total, "obj": obj})
