from django.urls import path
from . import views as v

urlpatterns = [
    path('api/register/', v.register_user, name='register-user'),
    path('api/income/', v.income_list_create, name='income-list-create'),
    path('api/expense/', v.expense_list_create, name='expence-list-create'),
    path('api/budget/', v.budget_view, name='budget'),

]
