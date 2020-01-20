from django.shortcuts import render
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.utils import timezone

from django_select2.forms import Select2Widget
from easy_select2 import Select2
# https://stackoverflow.com/questions/8022530/how-to-check-for-valid-email-address
from validate_email import validate_email
import re

from core.models import Centre, User, Cicle
from borsApp.models import Empresa, Titol, Oferta

# Create your views here.

from core.views import accepta_tos

class ConvidaProfesForm(forms.Form):
    centre = forms.ModelChoiceField( Centre.objects.none(), widget=Select2Widget )
    emails = forms.CharField( widget=forms.Textarea,
                            help_text="Un email per línia dels alumnes a convidar.")

ANYS_TITOLS = [ y for y in range(1990,timezone.now().year+2) ]
class ConvidaAlumnesForm(ConvidaProfesForm):
    # els alumnes cal afegir tb el centre per posar-los al títol adequat
    cicle = forms.ModelChoiceField( None, widget=Select2Widget(attrs={'width':'100'}) )
    finalitzat = forms.BooleanField( required=False,
                help_text="Marcar si els alumnes ja han finalitzat el cicle." )
    data_finalitzacio = forms.DateField( widget=forms.SelectDateWidget(years=ANYS_TITOLS),
                required=False, help_text="Data de graduació de l'alumne")


# Create your views here.
def index(request):
    return render(request, 'borsApp/index.html', {} )


def pot_convidar( usuari ):
    return usuari.es_admin_centre or usuari.is_superuser


# LIB
###############################################
def filtra_ofertes_alumne(alumne):
    # TODO: resoldre per subscripcions
    # HO RESOLEM PELS TÍTOLS DE L'ALUMNE
    # cicles que ha cursat l'alumne
    cicles = [ titol.cicle for titol in alumne.titols.filter(graduat=True) ]
    centres = [ titol.centre for titol in alumne.titols.all() ]
    # TODO:(revisar, eliminar) només de les empreses que estan adscrites al centre de l'alumne
    # TODO: distància en km...
    empreses = Empresa.objects.filter(adscripcio__in=centres)
    # qs final (ofertes)
    qs = Oferta.objects.filter(
                        cicles__in=cicles,           # cicles subscrits
                        activa=True,
                        empresa__in=empreses,        # empreses adscrites TODO: segur?/eliminar?
                        final__gte=timezone.now(),   # eliminem les caducades
                    )
    return qs.distinct()


@login_required
@accepta_tos
@user_passes_test( pot_convidar , login_url="/login" )
def convida_alumnes(request):
    if request.method=="POST":
        # dades form
        cicle = Cicle.objects.get(pk=request.POST["cicle"])
        centre = Centre.objects.get(pk=request.POST["centre"])
        finalitzat = False
        data_finalitzacio = None
        dia = request.POST.get("data_finalitzacio_day", None )
        print("DIA: "+dia)
        mes = request.POST.get("data_finalitzacio_month", None )
        anyo = request.POST.get("data_finalitzacio_year", None )
        if dia and mes and anyo:
            data_finalitzacio = "{}-{}-{}".format(anyo,mes.zfill(2),dia)
        print("DATA FINALITZACIO: {}".format(data_finalitzacio))
        if request.POST.get("finalitzat",False):
            finalitzat = True
        # emails
        emails = request.POST["emails"].split("\n")
        emails_ok = []
        emails_repetits = []
        emails_erronis = []
        # grup alumnes
        galumnes = Group.objects.get(name="alumnes")
        for email in emails:
            email = email.strip()
            #print("("+email+")")
            # comprovar si repetit
            users = User.objects.filter(email=email)
            if not validate_email(email):
                emails_erronis.append(email)
            elif users:
                usuari = users[0]
                # no cal crear usuari
                emails_repetits.append(email)
                # resetejem TOS
                usuari.is_staff = False
                usuari.tos = False
                usuari.data_notificacio_tos = None
                usuari.save()
                # creem titol si necessari
                if Titol.objects.filter(cicle=cicle,centre=centre,alumne=usuari).count()==0:
                    titol = Titol( cicle=cicle, centre=centre, graduat=finalitzat, 
                                alumne=usuari, data=data_finalitzacio )
                    titol.save()
                # afegim al grup alumnes
                galumnes.user_set.add(usuari)
            elif validate_email(email,check_mx=True):
                # crear usuari (al grup alumnes)
                user = User(username=email.replace("@","_"),email=email,is_staff=True,centre=centre)
                user.is_staff = False
                user.tos = False
                user.data_notificacio_tos = None
                user.save()
                emails_ok.append(email)
                # crear títol de l'alumne
                titol = Titol( cicle=cicle, centre=centre, graduat=finalitzat,
                                alumne=user, data=data_finalitzacio )
                titol.save()
                # afegir al grup alumnes
                galumnes.user_set.add(user)
            else:
                emails_erronis.append(email)
            # s'envia email d'invitació a l'alumne amb la comanda email_tos (CRON)
        return render(request,'borsApp/convida.html',
            {   "tipus": "alumnes",
                "cicle":cicle, "centre":centre,
                "emails_ok":emails_ok,
                "emails_repetits":emails_repetits,
                "emails_erronis":emails_erronis} )
    # GET: creem form per introduir emails d'invitació
    form = ConvidaAlumnesForm(request.GET)
    # TODO: arreglar initial, no va
    form.fields["data_finalitzacio"].initial = timezone.now()
    if request.user.is_superuser:
        form.fields["centre"].queryset = Centre.objects.all()
        form.fields["cicle"].queryset = Cicle.objects.all()
    else:
        # filtrem cicles dels centres implicats
        # TODO: selects encadenats
        centres = request.user.centres_admin.all()
        form.fields["centre"].queryset = centres
        form.fields["cicle"].queryset = Cicle.objects.filter(centres__in=centres)
        #request.user.centres_admin.all().cicles.all()
    return render(request, 'borsApp/convida.html', {"form":form,"tipus":"alumnes"} )

@login_required
@accepta_tos
@user_passes_test( pot_convidar, login_url="/login" )
def invitacions(request):
    return render(request, 'borsApp/invitacions.html')


@login_required
@accepta_tos
@user_passes_test( pot_convidar , login_url="/login" )
def convida_profes(request):
    if request.method=="POST":
        # dades form
        centre = Centre.objects.get(pk=request.POST["centre"])
        finalitzat = False
        if request.POST.get("finalitzat",False):
            finalitzat = True
        # emails
        emails = request.POST["emails"].split("\n")
        emails_ok = []
        emails_repetits = []
        emails_erronis = []
        # grup alumnes
        gprofes = Group.objects.get(name="profes")
        for email in emails:
            email = email.strip()
            #print("("+email+")")
            # comprovar si repetit
            users = User.objects.filter(email=email)
            if not validate_email(email):
                emails_erronis.append(email)
            elif users:
                usuari = users[0]
                # no cal crear usuari
                emails_repetits.append(email)
                # afegim al grup profes
                gprofes.user_set.add(usuari)
                # resetejem els permisos fins q accepti el TOS
                usuari.is_staff = False
                usuari.tos = False
                usuari.data_notificacio_tos = None
                usuari.save()
            elif validate_email(email,check_mx=True):
                # crear usuari (al grup profes)
                usuari = User(username=email.replace("@","_"),email=email,is_staff=True,centre=centre)
                usuari.save()
                emails_ok.append(email)
                # afegir al grup alumnes
                gprofes.user_set.add(usuari)
                # resetejem els permisos fins q accepti el TOS
                usuari.is_staff = False
                usuari.tos = False
                usuari.data_notificacio_tos = None
                usuari.save()
            else:
                emails_erronis.append(email)
            # TODO: enviar email al profe
        return render(request,'borsApp/convida.html',
            {   "tipus":"profes",
                "centre":centre,
                "emails_ok":emails_ok,
                "emails_repetits":emails_repetits,
                "emails_erronis":emails_erronis} )
    # GET: creem form per introduir emails d'invitació
    form = ConvidaProfesForm(request.GET)
    if request.user.is_superuser:
        form.fields["centre"].queryset = Centre.objects.all()
    else:
        centres = request.user.centres_admin.all()
        form.fields["centre"].queryset = centres
    return render(request, 'borsApp/convida.html', {"form":form,"tipus":"profes"} )
