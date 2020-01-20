from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.shortcuts import redirect
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone

from core.models import *

from django.template import Context
from django.template.loader import get_template
from django.template.loader_tags import BlockNode, ExtendsNode
from django.utils.html import strip_tags
#
# Utils 
##########################################
def _get_node(template, context=Context(), name='subject'):
    for node in template:
        if isinstance(node, BlockNode) and node.name == name:
            return node.render(context)
        elif isinstance(node, ExtendsNode):
            return _get_node(node.nodelist, context, name)
    raise Exception("Node '%s' could not be found in template." % name)
def get_tos_text():
    templ = get_template("tos.html")
    section = _get_node(templ.template,name="content")
    text = strip_tags(section)
    return text.strip()

#
# TOS (Termes d'ús)
##########################################
# Decorator util @accepta_tos
def accepta_tos(func):
	def wrapper(request):
		if request.user.is_anonymous or request.user.tos:
			return func(request)
		else:
			return render( request, 'tos.html', {} )
	return wrapper


#
# TOS VIEWS (Termes d'ús)
##########################################
@login_required
def tos(request):
	return render( request, 'tos.html', {} )

@login_required
def tos_accepta(request):
	# Deixem constància de l'acceptació
	msg = "L'usuari ha ACCEPTAT els termes d'ús el {}.\n".format(timezone.now())
	msg += get_tos_text()
	if not request.user.registre:
		request.user.registre = msg
	else:
		request.user.registre += msg
	request.user.tos = True
	request.user.data_notificacio_tos = timezone.now()
	# obrim accés al backend
	request.user.is_staff = True
	request.user.save()
	return render( request, 'index.html', {} )

@login_required
def tos_refusa(request):
	# Deixem constància del refús
	msg = "L'usuari ha REFUSAT els termes d'ús el {}.\n".format(timezone.now())
	if not request.user.registre:
		request.user.registre = msg
	else:
		request.user.registre += msg
	# tanquem accés al backend
	request.user.is_staff = False
	request.user.save()
	logout(request)
	return render( request, 'index.html', {} )

#
# VIEWS
##########################################

# Basic login and mainpage
def login(request):
	return render( request, 'login.html', {} )

def logout_view(request):
	logout(request)
	return redirect("/")

@accepta_tos
def index(request):
	return render( request, 'index.html', {} )

# Perfil
class PerfilForm(forms.ModelForm):
	class Meta:
		model = User
		#exclude = ('groups','permissions','is_staff','is_superuser','is_active',
		#	'password','last_login','date_joined')
		fields = ['first_name','last_name','username','email',
			'imatge','arxiu','descripcio',]

@login_required
@accepta_tos
def perfil(request):
	print("ID user="+str(request.user.id))
	form = None
	if request.method=="POST":
		form = PerfilForm( request.POST, request.FILES, instance=request.user)
		if form.is_valid():
			# TODO: flash message?
			form.save()
			return redirect("/")
	else:
		# GET: create form
		form = PerfilForm(instance=request.user)
	
	return render(request, 'perfil.html', {"form":form} )
