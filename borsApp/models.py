from django.db import models
from django.conf import settings

from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point
from djrichtextfield.models import RichTextField


from core.models import User, Cicle, Centre, Categoria

# Create your models here.


# Empresa o centre de treball
class Empresa(models.Model):
    class Meta:
        verbose_name_plural = "Empreses"
    nom = models.CharField(max_length=255,unique=True)
    direccio = RichTextField()
    poblacio = models.CharField(max_length=255)
    cp = models.CharField(max_length=5)
    telefon = models.IntegerField()
    email = models.EmailField()
    web = models.URLField(blank=True)
    # loc inicial al mar, enfront al Maresme (2.6875,41.5600)
    localitzacio = gismodels.PointField(blank=True,default=Point(2.6875,41.5600))
    descripcio = RichTextField(blank=True)
    # usuaris administradors
    admins = models.ManyToManyField(User,blank=True,related_name="empreses_admin")
    # logo
    imatge = models.ImageField(upload_to='imatgesCentre', blank=True)
    # empreses adscrites a centres educatius
    adscripcio = models.ManyToManyField(Centre,blank=True,
                    related_name="empreses",symmetrical=False,
                    help_text="Centres educatius als que està adscrita l'empresa. ")
    def __str__(self):
        return self.nom



# titol de CF obtingut per un alumne
class Titol(models.Model):
    cicle = models.ForeignKey(Cicle,on_delete=models.SET_NULL,null=True)
    centre = models.ForeignKey(Centre,on_delete=models.SET_NULL,null=True)
    graduat = models.BooleanField()
    data = models.DateField(help_text="Data de graduació de l'alumne",blank=True,null=True)
    alumne = models.ForeignKey(User,on_delete=models.CASCADE,related_name="titols")
    # guardar descripció títol per si s'esborra el títol de referència
    descripcio = RichTextField(blank=True)
    def __str__(self):
        return str(self.alumne.first_name+" "+self.alumne.last_name+" | "+self.cicle.nom)


# Alertes d'ofertes de feina
class Subscripcio(models.Model):
    class Meta:
        verbose_name_plural = "Subscripcions"
    alumne = models.ForeignKey(User,on_delete=models.CASCADE)
    # centre al què està adscrit l'alumne (p.ex. on ha tret el títol)
    centre_educatiu = models.ForeignKey(Centre,on_delete=models.CASCADE,null=True,blank=True,
                    help_text="Rebre les ofertes dirigides a aquest centre",
                    related_name="subscripcions")
    centre_treball = models.ForeignKey(Empresa,on_delete=models.CASCADE,null=True,blank=True,
                    help_text="Rebre les ofertes d'aquesta empresa",
                    related_name="subscipcions")
    categories = models.ManyToManyField(Categoria,blank=True,
                    help_text="Rebre les ofertes que estiguin en aquestes categories")
    cicles = models.ManyToManyField(Cicle,
                    help_text="Rebre les ofertes relacionades amb aquests cicles")
    # distancia en km al centre (educatiu o de treball)
    # si és 0.0 o negatiu s'entén que a qualsevol distància
    distancia = models.FloatField(default=0.0,
                    help_text="Si la distància és 0 no es tindrà en compte aquest paràmetre")
    creat = models.DateTimeField(auto_now_add=True)
    modificat = models.DateTimeField(auto_now=True)


from django.utils import timezone

class Oferta(models.Model):
    class Meta:
        verbose_name_plural = "Ofertes"
    inici = models.DateTimeField(default=timezone.now)
    # TODO: check timedelta
    final = models.DateTimeField()
    activa = models.BooleanField(default=True)
    empresa = models.ForeignKey(Empresa,on_delete=models.CASCADE,null=True)
    cicles = models.ManyToManyField(Cicle)
    titol = models.CharField(max_length=255)
    descripcio = RichTextField()
    creador = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    categories = models.ManyToManyField(Categoria,blank=True)
    def __str__(self):
        return self.titol+" ("+self.empresa.nom+")"

class Demanda(models.Model):
    pass


class Notificacio(models.Model):
    """Objecte per al registre de notificacions als alumnes subscrits a la borsa
    """
    class Meta:
        unique_together = (('oferta','usuari'),)
        verbose_name_plural = "Notificacions"
    oferta = models.ForeignKey(Oferta,on_delete=models.CASCADE)
    usuari = models.ForeignKey(User,on_delete=models.CASCADE)
    registre = models.TextField(blank=True)
    enviament = models.DateTimeField(blank=True,null=True)
    confirmacio = models.DateTimeField(blank=True,null=True)

