from django.core.management.base import BaseCommand, CommandError
from borsApp.models import Cicle, Categoria

import csv

class Command(BaseCommand):
    help = 'Carrega dades dels cicles formatius'
    CAT_CICLES = "Cicles Formatius de Formació Professional"
    cicles = {}
    families = {}
    cats = {}

    def handle(self, *args, **options):
        cicles = {}
        with open('misc/Taules_cataleg_FP_18-19-LOE.csv') as csvfile:
            csv_reader = csv.DictReader( csvfile )
            for row in csv_reader:
                self.cicles[row["CODI_CICLE_FORMATIU"]] = row["NOM_CICLE_FORMATIU"]
                fam = row["CODI_CICLE_FORMATIU"][-4:-2]
                self.families[fam] = fam
        #debug
        self.show_families()

        Cicle.objects.all().delete()
        self.carrega()

    def show_families(self):
        for codi in self.families:
            print(self.families[codi])

    def show_cicles(self):
        for codi in self.cicles:
            print(self.cicles[codi])

    def carrega(self):
        # reseteja DB
        Categoria.objects.all().delete()
        Cicle.objects.all().delete()

        # categoria arrel
        arrel = None
        qs = Categoria.objects.filter(nom=self.CAT_CICLES)
        if not len(qs):
            arrel = Categoria(nom=self.CAT_CICLES)
            arrel.save()
        else:
            arrel = qs[0]
        # carrega families (categories)
        for codi in self.families:
            cat = Categoria()
            cat.nom = self.families[codi]
            cat.pare = arrel
            cat.save()
            self.cats[codi] = cat
        # carrega cicles
        for codi in self.cicles:
            cicle = Cicle()
            grau = codi[:4]
            if grau=="CFPS":
                cicle.grau = "CFGS"
            else:
                cicle.grau = "CFGM"
            cicle.codi = codi[-4:]
            cicle.nom = self.cicles[codi]
            codifamilia = codi[-4:-2]
            cicle.familia = self.cats[codifamilia]
            cicle.descripcio = cicle.nom
            print(cicle.codi)
            cicle.save()

