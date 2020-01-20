
# Borsa de Treball IETI

Projecte per a borsa de treball online per a centres on s'imparteixen cicles formatius. El projecte s'ha iniciat a l'Institut Esteve Terradas i Illa de Cornellà de Llobregat i està sent dut a terme pels alumnes de DAW (programació web).

## Instal·lació

Per instal·lar-te aquest software has de tenir instal·lat GIT, Python 3.x i Virtualenv.

    $ git clone https://github.com/aws2/BorsaDeTreball.git
    $ cd BorsaDeTreball
    $ virtualenv env
    $ source env/bin/activate
    (env)$ pip install -r requirements.txt

Si en aquest punt obtens errors del pip install, probablement és perquè tens un virtualenv que només treballa en Python 2.x, i ens cal un virtualenv instal·lat per a Python 3.x (amb pip3). Consulta la documentació de pip.


Com a BD no ens servirà utilitzar SQLite, haurem d'utilitzar MySQL o bé PostGis (PostgreSQL amb ampliacions de geolocalització com s'explica [aquí](https://realpython.com/location-based-app-with-geodjango-tutorial/)). Per arrencar una instància dockeritzada ho farem mitjançant:

    $ docker run --name=postgis -d -e POSTGRES_USER=user001 -e POSTGRES_PASS=123456789 -e POSTGRES_DBNAME=gis -p 5432:5432 kartoza/postgis:9.6-2.4

Cal crear un arxiu settings2.py amb les dades en producció:

    $ cp BorsaDeTreball/settings2example.py BorsaDeTreball/settings2.py
    $ vi BorsaDeTreball/settings2.py

Seguim creant la BD, carregant permisos i posant en marxa l'aplicació:

    (env)$ python manage.py migrate
    (env)$ python manage.py createsuperuser
    (env)$ python manage.py permisos
    (env)$ python manage.py runserver

Si volem importar dades d'inici:

    (env)$ python manage.py loaddata categories
    (env)$ python manage.py loaddata cicles
    (env)$ python manage.py loaddata centres
    (env)$ python manage.py loaddata mps
    (env)$ python manage.py loaddata ufs

Alternativament disposem de la comanda per importar centres des d'un full de càlcul:

    (env)$ ./manage.py importa_centres

## CRON
Per que funcioni l'enviament d'emails amb el resum (digest) de les ofertes acumulades, caldrà afegir una línia al CRON a la hora convenient i executar la comanda //digest//

    $ python manage.py digest


## Seguiment del projecte
Pots trobar més informació del desenvolupament del projecte a la wiki de l'Esteve Terradas:

    https://wiket.esteveterradas.cat/index.php/Projecte_Borsa_de_Treball


