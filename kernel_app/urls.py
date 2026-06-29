from django.urls import path
from kernel_app.views import *

urlpatterns = [
    path('registration', registration_page, name='registration'),
    path('login', login_page, name='login'),
    path('', main_page, name='main'),
    path('new', new_card_page, name='new'),
    path('card/<str:id>/', card_page, name='card_page'),
    path('logout', logout_page, name='logout')
]