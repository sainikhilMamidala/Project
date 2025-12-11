from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('donor/', views.donor_dashboard, name='donor_dashboard'),
    path('receiver/', views.receiver_dashboard, name='receiver_dashboard'),
    path('donor/delete/<int:pk>/', views.donor_delete_donation, name='donor_delete_donation'),  # <-- add this
   # path('donor/restore/<int:pk>/', views.donor_restore_donation, name='donor_restore_donation'),
    path('claim/<int:pk>/', views.claim_donation, name='claim'),
    path('reject/<int:pk>/', views.reject_donation, name='reject'),
    #path('update/<int:pk>/', views.adjust_availability, name='adjust_availability'),
    path('logout/', views.logout_view, name='logout'),
     path('donor/login/', views.donor_login_view, name='donor_login'),      # <-- add this
    path('receiver/login/', views.receiver_login_view, name='receiver_login'),  # optional for receiver
    path('donor/signup/', views.donor_signup_view, name='donor_signup'),
    path('receiver/signup/', views.receiver_signup_view, name='receiver_signup'),
     path('donor/dashboard/', views.donor_dashboard, name='donor_dashboard'),
    path('receiver/dashboard/', views.receiver_dashboard, name='receiver_dashboard'),
    path('donation/delete/<int:pk>/', views.delete_donation, name='delete_donation'),
]
