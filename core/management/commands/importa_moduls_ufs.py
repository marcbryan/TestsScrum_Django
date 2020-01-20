
from django.core.management.base import BaseCommand, CommandError

from core.models import *

import csv

class Command(BaseCommand):
    help = 'Carrega dades del Mòduls Professionals i Unitats Formatives (MPs i UFs)'
    mps = {}
    ufs = {}
    cicles = {}

    def handle(self, *args, **options):

        # reseteja DB
        UnitatFormativa.objects.all().delete()
        ModulProfessional.objects.all().delete()

        current_cicle = None
        current_modul = None
        with open('misc/mps_informatica.csv') as csvfile:
            csv_reader = csv.DictReader( csvfile, delimiter=";" )
            for row in csv_reader:
                if row["codi"]:
                    codi = row["codi"]
                    print(codi)
                    cicle = Cicle.objects.filter(codi=codi)
                    # si no hi ha cicle deixar a None per ignorar les subsquents UFs
                    current_cicle = None
                    if cicle:
                        current_cicle = cicle[0]
                    else:
                        print("ERROR cicle no trobat: "+codi)
                if row["modul"]:
                    current_modul = None
                    # cal que hi hagi un cicle assignat
                    if current_cicle:
                        num = int(row["modul"][2:4])
                        print("  "+str(num))
                        current_modul = ModulProfessional(
                            numero = num,
                            nom = row["modul"],
                            cicle = current_cicle,
                            )
                        current_modul.save()
                if row["uf"]:
                    if current_modul:
                        num = int(row["uf"][2])
                        uf = UnitatFormativa(
                            numero = num,
                            nom = row["uf"],
                            mp = current_modul,
                            )
                        uf.save()
        #debug
        #self.show_cicles()

    def show_cicles(self):
        for codi in self.cicles:
            print(self.cicles[codi])

