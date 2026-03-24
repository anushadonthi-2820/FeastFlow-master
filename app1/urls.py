from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from app1.views import *

urlpatterns = [
    path("", render_home, name="home"),
    path("cart/<int:rid>", add_cart, name="cart"),
    path("single/<int:rid>", render_single, name="single"),
    path("userlogin", render_user_login, name="userlogin"),
    path("userreg", render_user_reg, name="userreg"),
    path("itemmreg", render_item_reg, name="itemreg"),
    path("logout", logout_user, name="logout"),
    path("showcart", render_show_cart, name="showcart"),
    path("emptycart", empty_cart, name="emptycart"),
    path("removeitem/<int:rid>", remove_item, name="removeitem"),
    path("order", render_order, name="order"),
    path("payment", render_payment, name="payment"),
    path("verify-payment", verify_payment, name="verify_payment"),
    path("ordered", render_ordered, name="ordered"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
