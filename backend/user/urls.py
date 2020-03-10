from django.urls import path

from user import views


app_name = 'user'

urlpatterns = [
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateAuthTokenView.as_view(), name='token'),
]
