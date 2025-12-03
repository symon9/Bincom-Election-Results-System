from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('polling-unit/', views.polling_unit_result, name='polling_unit_result'),
    path('lga-result/', views.lga_summed_result, name='lga_summed_result'),
    path('add-result/', views.add_polling_unit_result, name='add_polling_unit_result'),
    path('api/wards/<int:lga_id>/', views.get_wards, name='get_wards'),
    path('api/polling-units/<int:ward_id>/', views.get_polling_units, name='get_polling_units'),
]
