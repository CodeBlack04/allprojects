from django.urls import path
from . import views

app_name = 'bookmyhotel'

urlpatterns = [
    path('', views.hotel_list, name='hotels'),

    path('admin/', views.admin, name='admin'),

    path('add-user/', views.add_user, name='add-user'),
    
    path('<str:hotel_id>/', views.hotel_detail, name='hotel-detail'),

    path('<str:hotel_id>/submit-rating/', views.submit_rating, name='submit-rating'),

    path('rooms/<str:hotel_room_id>/', views.hotel_room_detail, name='hotel-room-detail'),

    path('rooms/<str:hotel_room_id>/book-room/', views.book_room, name='book-room'),

    path('create-room/<str:room_id>/', views.create_room, name='create-room'),

    path('edit-user/<str:id>/', views.edit_user, name='edit-user'),

    path('room/<str:room_id>/', views.room, name='room'),

    path('delete-room/<str:room_id>/', views.delete_room, name='delete-room'),
]