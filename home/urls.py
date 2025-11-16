from django.urls import path
from .views import *
urlpatterns = [
    path('', home, name='home'),
    # path('aboutus/', aboutus, name='aboutus'),
    # path('contactus/', contactus, name='contactus'),
    # path('privacypolicy/', privacypolicy, name='privacypolicy'),
    # path('termsofservice/', termsofservice, name='termsofservice'),
    # path('refundpolicy/', refundpolicy, name='refundpolicy'),
]