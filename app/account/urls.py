from django.urls import path
from django.contrib.auth import views as auth_views
from .views import AccountRegistrationView, client_list, client_detail, instagram_create, social_accounts_list

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='account/signin.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='home/index.html'), name='logout'),
    path('signup/', AccountRegistrationView.as_view(), name='signup'),
    path('workspaces/<slug:ws_slug>/clients/', client_list, name='clients'),
    path('workspaces/<slug:ws_slug>/clients/<int:pk>', client_detail, name='client-detail'),
    path('social-accounts', social_accounts_list, name='social-accounts'),
    path('<int:pk>/add-instagram', instagram_create, name='add-instagram'),
]
