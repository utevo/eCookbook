from django.urls import path

from users import views


app_name = 'users'

urlpatterns = [
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateAuthTokenView.as_view(), name='token'),
]
