from django.urls import path
from core import views

urlpatterns = [
    #path('', views.index, name='index'),
    #path('login', views.login,include('social_django.urls', namespace='social')),
    path('login', views.login, name='login'),
    path('tos', views.tos, name="tos" ),
    path('tos-accepta', views.tos_accepta, name="tos" ),
    path('tos-refusa', views.tos_refusa, name="tos" ),
    # aquest path es on va redirect per defecte quan falla OAuth
    # TODO: explicitar redirect
    path('accounts/login/', views.login, name='login2'),
    path('logout', views.logout_view, name="logout"),
    path('', views.index ),
    path('perfil', views.perfil, name="perfil"),
]

