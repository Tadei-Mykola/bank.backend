
from django.contrib import admin
from django.urls import path
from .views import get_all_users, get_all_banks, get_all_user_bank, add_user, get_csrf_token, delete_user, \
    delete_user_bank, add_bank_for_user, update_user, get_all_bank_users, delete_bank, add_bank, update_bank

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/users/', get_all_users, name='get-all-users'),
    path('users/banks/<int:user_id>', get_all_user_bank, name='get_all_user_bank'),
    path('users/newUser', add_user, name='add_user'),
    path('users/bank', add_bank_for_user, name='add_bank_for_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),
    path('users/bank/delete/<int:user_id>/<int:bank_id>/', delete_user_bank, name='delete_user_bank'),
    path('users/update/<int:user_id>', update_user, name='update_user'),
    path('bank/banks/', get_all_banks, name='get-all-banks'),
    path('bank/newBank', add_bank, name='add_bank'),
    path('bank/users/<int:id_bank>', get_all_bank_users, name='get_all_bank_users'),
    path('bank/delete/<int:id_bank>/', delete_bank, name='delete_bank'),
    path('bank/update/<int:id_bank>', update_bank, name='update_bank'),
    path('csrf-token/', get_csrf_token, name='get_csrf_token'),
]
