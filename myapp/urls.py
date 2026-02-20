from django.urls import path
from . import views as v

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', v.register_user, name='register-user'),
    path('api/income/', v.income_list_create, name='income-list-create'),
    path('api/income/<int:pk>/', v.income_detail),
    path('api/expense/', v.expense_list_create, name='expence-list-create'),
    path('api/expense/<int:pk>/', v.expense_detail),
    path('api/budget/', v.budget_view, name='budget'),
]
