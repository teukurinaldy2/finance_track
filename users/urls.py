from django import path
from .import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
]