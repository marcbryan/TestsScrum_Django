from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

from borsApp.models import *
from borsApp.views import filtra_ofertes_alumne


class Command(BaseCommand):
    """ DIGEST
        Aquesta comanda "digest" està pensada per programar-la amb CRON
        cada dia al finalitzar la jornada laboral (p.ex. 21h)
        Informa als alumnes de les ofertes que tenen disponibles
        per la seva titulació i centre
    """

    def handle(self, *args, **options):
        print("OFERTES per dia %s" % (timezone.now(),))
        # iterem alumnes que hagin acceptat el TOS
        # per enviar email amb ofertes pertinents
        total = 0
        galumnes = Group.objects.get(name="alumnes")
        for alumne in User.objects.filter(groups__in=[galumnes,],tos=True):
            ofertes = filtra_ofertes_alumne(alumne)
            if not ofertes:
                #print("\tAlumne %s: no té ofertes avui" % (alumne,))
                pass
            else:
                # Enviem DIGEST (email resum)
                # l'email constarà de les ofertes que son compatibles amb l'alumne
                # cada oferta té la seva notificació per saber si ha estat notificada

                # 1) llista de notificacions/ofertes a enviar
                notis = []
                # iterem ofertes actives i generem notificacions
                for oferta in ofertes:
                    #print("\t"+oferta.titol)
                    noti = Notificacio.objects.filter(usuari=alumne,oferta=oferta)
                    if not noti:
                        #print("\t\tCreant notificació...")
                        noti = Notificacio(
                                    usuari=alumne,
                                    oferta=oferta,
                                    registre="Creat el "+str(timezone.now())+"\n")
                        noti.save()
                    else:
                        noti = noti[0]
                    # enviem email només si no ha estat enviat prèviament
                    if not noti.enviament:
                        #print("\t\t\tNo ha estat notificada. Reintentem.")
                        notis.append(noti)
                # si hi ha notificacions pendents, fem email
                if notis:
                    #print(alumne)
                    # 2) creem cos de l'email amb totes les ofertes
                    body = "<p>Borsa de treball IETI.cat</p>\
                            <p>Avui tens %i ofertes de treball</p><br>\n" % (len(notis))
                    # TODO: mes sofisticat (sense iterar notis)
                    # html_message = render_to_string('mail_template.html', {'context': 'values'})
                    for noti in notis:
                        # registre d'activitat de la notificació
                        noti.registre += "Intentant enviament a %s el %s\n" % \
                                                (alumne.email, str(timezone.now()))
                        noti.save()
                        # afegim al body html email
                        body += "<div style='border:1px black solid;border-radius:1em;margin:1em;padding:1em;'><br>" +\
                                noti.oferta.titol + "<br>" +\
                                str(noti.oferta.empresa) + "<br>" +\
                                noti.oferta.descripcio + "<br>" +\
                                "</div>";
                                #TODO: noti.oferta.dades_empresa()
                                #TODO: botó enviar CV
                    # afegim footer al email
                    body += "<br><p>En qualsevol moment pots donar-te de baixa escrivint a borsa@iesesteveterradas.cat</p>"
                    # 3) notifiacions pendents: s'intenten enviar
                    subject = "Borsa de treball: tens %i ofertes" % (len(notis),)
                    email_from = settings.EMAIL_FROM_NAME+"<"+settings.EMAIL_HOST_USER+">"
                    email_to = [ alumne.email, ]
                    plain_body = strip_tags(body)
                    enviat = send_mail( subject, plain_body, email_from, email_to, html_message=body )
                    #enviat = True # per DEBUG
                    if not enviat:
                        print("\tError enviant email a {} amb {} ofertes".format(alumne.email,len(notis)))
                        # saltem a seguent iteracio
                        continue
                    # 4) si l'email s'envia correctament, es marquen totes les notificacions com OK
                    total += 1
                    print("\tEmail enviat a {} amb {} ofertes".format(alumne.email,len(notis)))
                    for noti in notis:
                        temps = timezone.now()
                        if enviat:
                            noti.enviament = temps
                            noti.registre += "\tEnviament correcte (%s)\n" % (str(temps),)
                        else:
                            noti.registre += "\tEnviament fallit (%s)\n" % (str(temps),)
                        print("\t\t{}".format(noti.oferta.titol))
                        # guardem dades de registre d'enviament
                        noti.save()
                    if total>=settings.MAX_EMAILS:
                        print("\tArribat a MAX_EMAILS, aturem enviament fins següent interval\n")
                        break


                # TODO: informe admins

