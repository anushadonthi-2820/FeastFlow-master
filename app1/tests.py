from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from app1.models import Cart, Fooditem, Order


class CheckoutFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="secret123", email="alice@example.com")
        self.other_user = User.objects.create_user(username="bob", password="secret123")
        self.item = Fooditem.objects.create(
            itempic="images/test.png",
            itemname="Paneer Wrap",
            price=120,
            itemtype="veg",
            rating=4.5,
            availability=True,
        )

    def test_cart_is_user_specific(self):
        Cart.objects.create(user=self.user, item=self.item, quantity=2)
        Cart.objects.create(user=self.other_user, item=self.item, quantity=1)

        self.client.login(username="alice", password="secret123")
        response = self.client.get(reverse("showcart"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["all"]), 1)
        self.assertEqual(response.context["all"][0].quantity, 2)
        self.assertEqual(response.context["total"], 240)

    @override_settings(RAZORPAY_KEY_ID="test_key", RAZORPAY_KEY_SECRET="test_secret")
    @patch("app1.views.razorpay.Client")
    def test_payment_page_creates_razorpay_order(self, mock_client_class):
        Cart.objects.create(user=self.user, item=self.item, quantity=2)
        self.client.login(username="alice", password="secret123")
        session = self.client.session
        session["pending_order"] = {"addr": "221 Baker Street", "phno": "9876543210"}
        session.save()

        mock_client = Mock()
        mock_client.order.create.return_value = {"id": "order_test_123"}
        mock_client_class.return_value = mock_client

        response = self.client.get(reverse("payment"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["razorpay_ready"])
        self.assertEqual(response.context["razorpay_order_id"], "order_test_123")

    @override_settings(RAZORPAY_KEY_ID="test_key", RAZORPAY_KEY_SECRET="test_secret")
    @patch("app1.views.razorpay.Client")
    def test_verify_payment_creates_paid_order(self, mock_client_class):
        Cart.objects.create(user=self.user, item=self.item, quantity=2)
        self.client.login(username="alice", password="secret123")
        session = self.client.session
        session["pending_order"] = {"addr": "221 Baker Street", "phno": "9876543210"}
        session["razorpay_checkout"] = {"order_id": "order_test_123", "amount": 24000}
        session.save()

        mock_client = Mock()
        mock_client.utility.verify_payment_signature.return_value = None
        mock_client_class.return_value = mock_client

        response = self.client.post(
            reverse("verify_payment"),
            {
                "razorpay_order_id": "order_test_123",
                "razorpay_payment_id": "pay_test_456",
                "razorpay_signature": "signature_test_789",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "ordered.html")

        order = Order.objects.get(usern=self.user)
        self.assertEqual(order.payment_method, "online")
        self.assertEqual(order.payment_status, "paid")
        self.assertEqual(order.transaction_id, "pay_test_456")
        self.assertEqual(order.razorpay_order_id, "order_test_123")
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)

    def test_cash_on_delivery_creates_pending_order(self):
        Cart.objects.create(user=self.user, item=self.item, quantity=1)
        self.client.login(username="alice", password="secret123")
        session = self.client.session
        session["pending_order"] = {"addr": "221 Baker Street", "phno": "9876543210"}
        session.save()

        response = self.client.post(reverse("payment"), follow=True)

        self.assertEqual(response.status_code, 200)
        order = Order.objects.get(usern=self.user)
        self.assertEqual(order.payment_method, "cod")
        self.assertEqual(order.payment_status, "pending")

    def test_item_registration_accepts_float_rating(self):
        response = self.client.post(
            reverse("itemreg"),
            {
                "itempic": "",
                "itemname": "Mango Shake",
                "price": "99",
                "itemtype": "Drink",
                "rating": "4.7",
                "availability": "True",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Fooditem.objects.filter(itemname="Mango Shake", rating=4.7).exists())
