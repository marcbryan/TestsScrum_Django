from django.urls import path
from . import views

urlpatterns = [
    path( '', views.index, name='index' ),
    path( 'convida_alumnes', views.convida_alumnes, name="convida_alumnes" ),
    path( 'convida_profes', views.convida_profes, name="convida_profes" ),
    path( 'invitacions', views.invitacions, name="invitacions" ),
]

