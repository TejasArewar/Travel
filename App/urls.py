from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add-expense/', views.add_expense, name='add_expense'),
    path('edit-expense/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete-expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('create-itinerary/', views.create_itinerary, name='create_itinerary'),
    path('add-location/', views.add_location, name='add_location'),
    path('delete-itinerary/<int:itinerary_id>/', views.delete_itinerary, name='delete_itinerary'),
    path('delete-place/<int:itinerary_id>/<int:place_index>/', views.delete_place, name='delete_place'),
    path('get-itineraries/', views.get_locations, name='get_itineraries'),
    path('get-itinerary/<int:itinerary_id>/', views.get_itinerary, name='get_itinerary'),
    path('get-all-users/', views.get_all_users, name='get_all_users'),
    path('get-user-itineraries/<int:user_id>/', views.get_user_itineraries, name='get_user_itineraries'),
    path('', views.home, name='home'),
]

