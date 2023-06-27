from django.urls import path
from subWEB import views

urlpatterns=[
    path('main/',views.main),
    path('res/', views.res),
    path('test/', views.test)
]