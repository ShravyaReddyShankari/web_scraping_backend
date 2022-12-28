from django.urls import path
from .views import BestDealFinder

urlpatterns = [
    path('best-product-deal/', BestDealFinder.as_view()),
]