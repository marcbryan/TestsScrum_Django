from django.core.management.base import BaseCommand, CommandError
from borsApp.models import Cicle, Categoria, Centre
from django.contrib.gis.geos import Point

import csv

class Command(BaseCommand):
    help = 'Carrega dades dels centres docents'

    def handle(self, *args, **options):
        # esborrem tots els centres
        #Centre.objects.all().delete()

        with open('misc/Directori_de_centres_docents.csv') as csvfile:
            csv_reader = csv.DictReader( csvfile )
            for row in csv_reader:
                # incialitzem centre
                centre = None
                # filtrem centres del curs actual
                if row["Curs"] != "2018/2019" or "institut" not in row["Denominació completa"].lower():
                    continue
                # filtrem casos erronis
                if not row["Codi centre"] or row["Codi centre"]==0:
                    print("--- CODI DE CENTRE ERRONI: "+row["Denominació completa"])
                    continue
                # si és el mateix centre, actualitzem dades
                qs = Centre.objects.filter(codi=row["Codi centre"])
                if qs:
                    print("--- ACTUALITZANT : "+row["Denominació completa"])
                    centre = qs[0]
                # si té el mateix nom q un altre centre, els distingim el nom
                qs = Centre.objects.filter(nom=row["Denominació completa"])
                if qs:
                    print("--- Centre amb el mateix nom : "+row["Denominació completa"])
                    #continue
                if not centre:
                    centre = Centre()
                centre.educatiu = True
                centre.codi = row["Codi centre"]
                centre.nom = row["Denominació completa"]
                centre.direccio = row["Adreça"]
                centre.poblacio = row["Nom localitat"]
                centre.cp = row["Codi postal"]
                centre.telefon = 1 #row["Telèfon"]
                centre.email = row["E-mail centre"]
                centre.web = ""
                centre.codi = row["Codi centre"]
                x = row["Coordenades GEO X"]
                y = row["Coordenades GEO Y"]
                if( x and y ):
                    centre.localitzacio = Point(float(x),float(y))
                else:
                    centre.localitzacio = Point(0,0)
                centre.save()
                print(row["Codi centre"]+" | "+row["Denominació completa"])

