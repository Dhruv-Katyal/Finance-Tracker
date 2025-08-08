from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns= [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('', views.dashboard, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('transaction/',views.TransactionCreateView, name='transaction'),
    path('show/',views.TransactionListView, name='show'),
    path('goal/',views.GoalView, name='goal'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),

]