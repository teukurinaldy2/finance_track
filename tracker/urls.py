from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('reset/', views.reset_data, name='reset_data'),
    path('edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),

    # KATEGORI CRUD
    path('category/', views.category_list, name='category_list'),
    path('category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    # SALDO AWAL
    path('saldo-awal/', views.saldo_awal, name='saldo_awal'),

    # LAPORAN
    path('laporan/', views.laporan, name='laporan'),

]