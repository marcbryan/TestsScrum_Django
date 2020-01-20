from django.contrib import admin

from django.contrib.gis.admin import OSMGeoAdmin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.db.models import Count
from django import forms

#from easy_select2 import select2_modelform

# Register your models here.

from core.models import *


class CatAdmin(admin.ModelAdmin):
    model = Categoria
    list_display = ('nom','pare','descripcio')
    search_fields = ('nom','pare__nom')
    ordering = ('pare','nom',)

class MPInline(admin.TabularInline):
    model = ModulProfessional
    extra = 0
    exclude = ('descripcio',)
class CicleAdmin(admin.ModelAdmin):
    list_display = ('codi','nom','familia')
    list_display_links = ('codi','nom',)
    ordering = ('familia','nom',)
    search_fields = ('grau','codi','nom','familia__nom','descripcio')
    inlines = ( MPInline, )

class CentreAdmin(OSMGeoAdmin):
    list_display = ('nom','poblacio','nadmins','noms_admins','nempreses','get_empreses')
    #ordering = ('nadmins','nom')
    search_fields = ('nom','direccio','poblacio','empreses__nom')
    filter_horizontal = ('admins','cicles',)
    readonly_fields = ('get_empreses',)
    def noms_admins(self,obj):
        res = ""
        for admin in obj.admins.all():
            res += admin.username+"<br>"
        return mark_safe(res)
    def nadmins(self,obj):
        return obj.admins.count()
    #te_admin.boolean = True
    nadmins.admin_order_field = "nadmins"
    def nempreses(self,obj):
        return obj.empreses.count()
    #nempreses.admin_order_field = "nempreses"
    def get_empreses(self,obj):
        res = ""
        for empresa in obj.empreses.all():
            res += empresa.nom+"<br>"
        return mark_safe(res)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(
                        nadmins=Count("admins"),
                        nempreses=Count("empreses"),
                    ).order_by("-nadmins","-nempreses","nom")
        if request.user.is_superuser:
            # super ho veu tot
            return qs
        elif request.user.es_admin_centre:
            # admin centre veu el seu centre i prou
            return qs.filter(admins__in=[request.user,])
        #ERROR: cap altre usuari pot veure Centres

# no cal select2_modelform pq amb django-admin-select2 ja funciona
#UFForm = select2_modelform(UnitatFormativa)
#MPForm = select2_modelform(ModulProfessional)
class UFInline(admin.TabularInline):
    model = UnitatFormativa
    extra = 0
    exclude = ('descripcio',)
class MPAdmin(admin.ModelAdmin):
    model = ModulProfessional
    #form = MPForm
    list_display = ('codi_cicle','numero','nom','cicle',)
    list_display_links = ('numero','nom',)
    ordering = ('cicle','numero')
    search_fields = ('cicle__codi','cicle__nom','nom')
    inlines = [ UFInline, ]
    def codi_cicle(self,obj):
        return obj.cicle.codi


from borsApp.admin import TitolInline, SubscripcioInline
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from borsApp.models import Empresa

class UserCreationFormExtended(UserCreationForm):
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        self.fields['empresa'] = forms.BooleanField(help_text="Marcar si l'usuari és administrador d'empresa")

#from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserChangeForm
#from django_select2.forms import Select2Widget
#UserForm = select2_modelform(User,attrs={'exclude':'password'})
# no cal select2_modelform pq amb django-admin-select2 ja funciona

PERMISOS_ONLY_SUPER = ['is_superuser','groups','is_staff','user_permissions']
PERMISOS_READ_ONLY = ['mostrar_imatge','last_login','date_joined','registre']

class MyUserAdmin(UserAdmin):
    save_on_top = True
    list_filter = ()
    #form = UserForm
    #add_form = UserCreationFormExtended
    fieldsets = UserAdmin.fieldsets + (
            ("Dades acadèmiques", {
                'fields': ('centre','imatge','mostrar_imatge','arxiu','descripcio','tos','data_notificacio_tos','registre'),
            }),
    )
    """add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2',)
        }),)"""
    #inlines = [ TitolInline, SubscripcioInline, ]
    inlines = [ TitolInline, ]
    readonly_fields = PERMISOS_READ_ONLY + PERMISOS_ONLY_SUPER
    def mostra_grups(self,obj):
        grups = ""
        for grup in obj.groups.all():
            grups += grup.name + "<br>"
        return mark_safe(grups)
    def mostra_centre(self,obj):
        if obj.centre:
            return obj.centre.nom
        return None
    def mostra_centres_admin(self,obj):
        centres = ""
        for centre in obj.centres_admin.all():
            centres += centre.nom + "<br>"
        return mark_safe(centres)
    def mostra_titols(self,obj):
        titols = ""
        for titol in obj.titols.all():
            titols += titol.cicle.nom + "<br>"
        return mark_safe(titols)
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        # reset ordering pq a get_queryset si no, dona un error en altres admins (equips...)
        self.ordering = ('username',)
        self.list_display += ('mostra_centres_admin','mostra_grups','mostra_centre','mostra_titols','tos','data_notificacio_tos','last_login')
        self.search_fields += ('centre__nom',)
        # anular els camps de nomes superusuari
    #def ncentres(self,obj):
    #   return obj.centres.count()
    #ncentres.admin_order_field = 'ncentres'
    def get_form(self,request,obj=None,**kwargs):
        if request.user.is_superuser:
            self.readonly_fields = PERMISOS_READ_ONLY
        else:
            self.readonly_fields = PERMISOS_READ_ONLY + PERMISOS_ONLY_SUPER
        return super().get_form(request,obj,**kwargs)
    def get_queryset(self,request):
        # Deshabilitem ordering ncentres per evitar error creuat
        # TODO: rehabilitar-ho
        """qs = super().get_queryset(request).annotate(
            ncentres=Count('centres_admin'))
        self.ordering = ('-ncentres','username')"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            # super ho veu tot
            return qs
        if request.user.es_admin_centre:
            # els usuaris (profes) admins de centre només poden veure els seus usuaris
            centres = request.user.centres_admin.all()
            # ...o els de les seves empreses
            empreses = Empresa.objects.filter(adscripcio__in=centres)#request.user.empreses.all()
            # TODO: afegir segons titols obtinguts?
            #qs = qs.filter(titols__centre__in=centres).distinct()
            qs = qs.filter(Q(centre__in=centres)|Q(empreses_admin__in=empreses)).distinct()
            return qs
        # TODO: profes, poden veure els seus alumnes
        if request.user.es_profe:
            # els profes poden veure els seus alumnes (scrum) però nomes read-only
            qs = qs.filter(centre=request.user.centre).distinct()
            return qs
        # la resta, alumnes i admins empresa, nomes es veuen a ells mateixos
        qs = qs.filter(id=request.user.id)
        return qs
    def save_model(self,request,obj,form,change):
        # si es superuser ho deixem tal qual
        if request.user.is_superuser:
            super().save_model(request,obj,form,change)
            return
        # si es admin centre cal associar l'usuari al centre de l'admin
        if request.user.es_admin_centre:
            # TODO: revisar que un usuari pot ser admin de 2 centres alhora
            obj.centre = request.user.centres_admin.first()
            # permisos d'alumne pel backend i frontend
            obj.save()
            galumnes = Group.objects.get(name="alumnes")
            obj.groups.add(galumnes)
            obj.is_staff = True
            obj.save()
            return
        # si no es admin_centre ni superuser no es guarda res
        # Donar error (cap usuari hauria d'arribar aqui)
        print("ERROR: en UserAdmin.save_model (usuari no autoritzat)")
        raise Exception("Usuari no autoritzat. Parlar amb l'administrdor.")


admin.site.register( ModulProfessional, MPAdmin )
#admin.site.register( UnitatFormativa )
admin.site.register( Categoria, CatAdmin )
admin.site.register( Cicle, CicleAdmin )
admin.site.register( Centre, CentreAdmin )
admin.site.register( User, MyUserAdmin )


admin.site.site_title = "Gestió portal integrat"
admin.site.site_header = mark_safe("Administració | <a href='/'>->Anar a inici<-</a>")

