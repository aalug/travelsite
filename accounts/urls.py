from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register-user'),
    path('my-account/', views.MyAccountRedirectView.as_view(), name='my-account'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>/', views.ActivateView.as_view(), name='activate'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password-validate/<uidb64>/<token>/', views.ResetPasswordValidateView.as_view(),
         name='reset-password-validate'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('subscribe-to-newsletter/', views.SubscribeToNewsletterView.as_view(), name='sub-newsletter'),
    path('newsletter/', views.SendNewsletterView.as_view(), name='newsletter'),
    path('about-us/', views.AboutUsView.as_view(), name='about-us'),
    path('messages-from-users/', views.MessagesFromUsersView.as_view(), name='messages-from-users'),

]

