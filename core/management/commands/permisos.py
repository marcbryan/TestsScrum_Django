from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

import logging

PERMISOS = {
    "admin_borsa":{
        "demanda": ["add","change","delete","view"],
        "empresa": ["add","change","delete","view"],
        "notificacio": ["change","view"],
        "oferta": ["add","change","delete","view"],
        #"subscripcio": ["add","change","delete","view"],
        "titol": ["add","change","delete","view"],
        "categoria": ["add","change","delete","view"],
        "centre": ["add","change","delete","view"],
        "user": ["add","change","delete","view"],
    },
    "admin_empresa":{
        "demanda": ["view"],
        "empresa": ["change","view"],
        "oferta": ["add","change","delete","view"],
    },
    "alumnes":{
        "demanda": ["add","change","delete","view"],
        "oferta": ["view"],
        "subscripcio": ["add","change","delete","view"],
        "titol": ["view"],
        "projecte": ["view"],
        "done spec": ["view"],
        "equip": ["add","change","view"],
        "qualificacio": ["view"],
        "spec": ["view"],
        "sprint": ["view"],
    },
    "profes":{
        "done spec": ["add","change","delete","view"],
        "equip": ["add","change","delete","view"],
        "projecte": ["add","change","delete","view"],
        "qualificacio": ["add","change","delete","view"],
        "spec": ["add","change","delete","view"],
        "sprint": ["add","change","delete","view"],
    },
}


class Command(BaseCommand):
    """ INICIA
        Crea grups en la BD
    """

    def handle(self, *args, **options):
        for nom_grup in PERMISOS:
            grup, creat = Group.objects.get_or_create(name=nom_grup)
            print(grup)
            # buidem tots els permisos de cada grup
            for perm in grup.permissions.all():
                grup.permissions.remove(perm)
            # apliquem permisos
            for model in PERMISOS[nom_grup]:
                for permis in PERMISOS[nom_grup][model]:
                    nom_permis = "Can {} {}".format(permis,model)
                    try:
                        obj_permis = Permission.objects.get(name=nom_permis)
                    except Permission.DoesNotExist:
                        logging.warning("Permís no trobat amb nom '{}'".format(nom_permis))
                        continue
                    if obj_permis in grup.permissions.all():
                        print("\t"+nom_permis+" (ja hi és)")
                    else:
                        print("\t"+nom_permis+" (afegint)")
                        grup.permissions.add(obj_permis)
        print("Creats grups i permisos")
