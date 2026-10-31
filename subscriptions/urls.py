from django.urls import path
from .views import SubscriptionListAPIView, SubscriptionDetailAPIView, SubscriptionUseAPIView

urlpatterns = [
    path("", SubscriptionListAPIView.as_view(), name="subscription-list"),
    path("<int:pk>/", SubscriptionDetailAPIView.as_view(), name="subscription-detail"),
    path("<int:pk>/use/", SubscriptionUseAPIView.as_view(), name="subscription-use"),
]