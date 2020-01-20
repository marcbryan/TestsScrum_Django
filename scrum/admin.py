from django.contrib import admin
from django import forms

from django.utils.safestring import mark_safe
from easy_select2 import select2_modelform
from adminsortable2.admin import SortableAdminMixin
from adminsortable2.admin import SortableInlineAdminMixin

# Register your models here.

from scrum.models import *
"""# Ja no cal pq hem posat plugin
ProjecteForm = select2_modelform(Projecte)
SprintForm = select2_modelform(Sprint)
EquipForm = select2_modelform(Equip)
SpecForm = select2_modelform(Spec)
"""

class QualificacioInline(admin.TabularInline):
    model = Qualificacio
    extra = 0
    fields = ('sprint','nota','specs_completades','hores_completades','specs_completades_mps','specs_completades_mps_ponderat')
    readonly_fields = ('sprint','specs_completades','hores_completades','specs_completades_mps','specs_completades_mps_ponderat')
    ordering = ('sprint__nom',)

class EquipAdmin(admin.ModelAdmin):
    model = Equip
    #form = EquipForm
    filter_horizontal = ('membres',)
    list_display = ('nom','projecte','centre','show_membres',)
    inlines = [ QualificacioInline, ]
    def centre(self,obj):
        return obj.projecte.centre.nom
    def cicle(self,obj):
        return obj.projecte.cicle.nom
    def show_membres(self,obj):
        ret = ""
        for membre in obj.membres.all():
            ret += membre.first_name + " " + membre.last_name \
                + " (<a href='/admin/core/user/"+str(membre.id)+"'>" + membre.username+"</a>)<br>\n"
        return mark_safe(ret)
    def get_queryset(self,request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # filtrem projectes propis
        # + (OR) projectes dels centres on soc admin
        # + (OR) projectes en els que participo com a alumne
        cids = [ centre.id for centre in request.user.centres_admin.all() ]
        qs = qs.filter( Q(projecte__admins__in=[request.user])
                        | Q(projecte__centre__in=cids)
                        | Q(membres__in=[request.user]) )
        return qs.distinct()
    def formfield_for_foreignkey(slef,db_field,request=None,**kwargs):
        if db_field.name=="projecte" and not request.user.is_superuser:
            # restringir a projectes del propi centre/s
            # TODO: restringir dates projectes en curs
            centres = Centre.objects.filter(admins__in=[request.user])
            if request.user.centre:
                centres |= Centre.objects.filter(pk=request.user.centre.id)
            kwargs["queryset"] = Projecte.objects.filter(centre__in=centres)
        return super().formfield_for_foreignkey(db_field,request=request,**kwargs)
    def formfield_for_manytomany(slef,db_field,request=None,**kwargs):
        if db_field.name=="membres" and not request.user.is_superuser:
            # els membres de l'equip poden ser els alumnes del mateix centre que l'usuari
            if request.user.centre:
                kwargs["queryset"] = User.objects.filter(centre=request.user.centre,titols__graduat=False)
                #TODO: initial sense modificar els que hi ha ja
                kwargs["initial"] = User.objects.filter(pk=request.user.id)
        return super().formfield_for_manytomany(db_field,request=request,**kwargs)

class SpecInline(SortableInlineAdminMixin,admin.TabularInline):
    model = Spec
    #form = SpecForm
    fields = ('nom','mp','hores_estimades','sprints')
    #readonly_fields = ('show_sprints',)
    #exclude = ('pare','descripcio')
    #TODO: no exclude descripcio pero adaptar-ho be en amplada
    extra = 2
    """def get_form(self,request,obj=None,**kwargs):
        form = super().get_form(request,obj,**kwargs)
        form.fields["descripcio"].widget.field_settings={'width':'300'}
        return form"""
    """def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        print(dir(self.form))
        self.form.visible_fields["descripcio"].widget.field_settings={'width':'300'}"""
    # restrict mps al cicle
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'mp':
            try:
                parts = request.get_raw_uri().split("/")
                i = parts.index("projecte")
                #print("I="+str(i))
                obj_id = parts[i+1]
                #print(obj_id)
                # obj és un projecte
                obj = Projecte.objects.get(pk=obj_id)
                #print(obj.id)
                if obj:
                    kwargs['queryset'] = ModulProfessional.objects.filter(cicle=obj.cicle).order_by('numero')
                else:
                    kwargs['queryset'] = ModulProfessional.objects.none()
            except:
                print("ERROR in formfield_for_manytomany (SpecInline)")
        elif db_field.name == 'sprints':
            try:
                parts = request.get_raw_uri().split("/")
                i = parts.index("projecte")
                #print("I="+str(i))
                obj_id = parts[i+1]
                #print(obj_id)
                # obj és un projecte
                obj = Projecte.objects.get(pk=obj_id)
                #print(obj.id)
                if obj:
                    kwargs['queryset'] = Sprint.objects.filter(projecte=obj).order_by('nom')
                else:
                    kwargs['queryset'] = Sprint.objects.none()
            except:
                print("ERROR in formfield_for_manytomany (SpecInline)")
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)
class SprintInline(admin.TabularInline):
    model = Sprint
    #form = SprintForm
    ordering = ('inici',)
    exclude = ('notes',)
    extra = 1
    # restrict specs al proj
    """def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'specs':
            try:
                parts = request.get_raw_uri().split("/")
                i = parts.index("projecte")
                #print("I="+str(i))
                obj_id = parts[i+1]
                #print(obj_id)
                if obj_id:
                    kwargs['queryset'] = Spec.objects.filter(projecte=obj_id).order_by('ordre')
                else:
                    kwargs['queryset'] = Spec.objects.none()
            except:
                print("ERROR in formfield_for_manytomany (SprintInline)")
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)
"""
from django.db.models import Q
class ProjecteAdmin(admin.ModelAdmin):
    model = Projecte
    #form = ProjecteForm
    list_display = ('nom','centre','cicle','inici','final','hores','resum_mps')
    ordering = ('centre','cicle','-inici')
    search_fields = ('nom','centre__nom','cicle__nom',)
    readonly_fields = ('descripcio_html',)
    exclude = ('descripcio',)
    filter_horizontal = ('admins',)
    inlines = [ SprintInline, SpecInline, ]
    save_on_top = True
    def hores(self,obj):
        hores = 0
        for spec in obj.spec_set.all():
            hores += spec.hores_estimades
        return "{:.0f}".format(hores)
    def resum_mps(self,obj):
        res = {}
        total = 0
        for spec in obj.spec_set.all():
            for mp in spec.mp.all():
                mpshort = mp.nom[:4]
                if not res.get(mpshort):
                    res[mpshort] = 0
                res[mpshort] += spec.hores_estimades
                total += spec.hores_estimades
        ret = ""
        for mp in res:
            percent = 0
            if total != 0:
                percent = 100*res[mp]/total
            ret += "{}: {:.0f} ({:.0f}%)<br>\n".format(mp,res[mp],percent)
        return mark_safe(ret)
    def get_form(self,request,obj=None,**kwargs):
        if request.user.es_alumne:
            # mostrem read-only i amaguem desc field (renderitzem html)
            self.exclude = ('descripcio',)
            self.readonly_fields = ('descripcio_html',)
        else:
            # mostrem tot normal (editable)
            self.exclude = ()
            self.readonly_fields = ()
        return super().get_form(request,obj,**kwargs)
    def get_queryset(self,request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # filtrem projectes propis
        # + (OR) projectes dels centres on soc admin o al que pertanyo
        # + (OR) projectes en els que participo com a alumne
        cids = [ centre.id for centre in request.user.centres_admin.all() ]
        if request.user.centre:
            cids.append(request.user.centre.id)
        qs = qs.filter( Q(admins__in=[request.user])
                        | Q(centre__in=cids)
                        | Q(equips__membres__in=[request.user]) ).distinct()
        return qs.distinct()
    def formfield_for_foreignkey(self,db_field,request=None,**kwargs):
        # filtre camp alumne
        if db_field.name=="centre":
            if request.user.es_admin_centre:
                # filtrem els centres del qual es admin
                kwargs["queryset"] = request.user.centres_admin.all()
            elif request.user.es_profe:
                kwargs["queryset"] = Centre.objects.filter(id__in=[request.user.centre.id,])
            elif request.user.es_alumne:
                kwargs["queryset"] = Centre.objects.none()
            elif request.user.is_superuser:
                kwargs["queryset"] = Centre.objects.all()
        elif db_field.name=="cicle":
            if request.user.es_admin_centre:
                # filtrem els centres del qual es admin
                kwargs["queryset"] = Cicle.objects.filter(centres__in=request.user.centres_admin.all())
            elif request.user.es_profe:
                kwargs["queryset"] = Cicle.objects.filter(centres__id__in=[request.user.centre.id,])
            elif request.user.es_alumne:
                kwargs["queryset"] = Cicle.objects.none()
            elif request.user.is_superuser:
                kwargs["queryset"] = Cicle.objects.all()
        return super().formfield_for_foreignkey(db_field,request=request,**kwargs)
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name=="admins":
            gprofes = Group.objects.get(name="profes")
            if request.user.es_admin_centre:
                # filtrem els centres del qual es admin
                kwargs["queryset"] = User.objects.filter(
                                            centre__in=request.user.centres_admin.all(),
                                            groups__in=[gprofes,])
            elif request.user.es_profe:
                kwargs["queryset"] = User.objects.filter(
                                            centre__id__in=[request.user.centre.id,],
                                            groups__in=[gprofes,])
            elif request.user.es_alumne:
                kwargs["queryset"] = User.objects.none()
            elif request.user.is_superuser:
                kwargs["queryset"] = User.objects.all()
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)

from urllib.parse import urlsplit
class SpecAdmin(SortableAdminMixin,admin.ModelAdmin):
    model = Spec
    search_fields = ('projecte__nom','mp__nom','sprints__nom')
    filter_horizontal = ('mp',)
    list_display = ('nom','descripcio_html','projecte','mostra_sprints','hores_estimades','moduls','ordre',)
    list_editable = ('hores_estimades',)
    readonly_fields = ('descripcio_html',)
    ordering = ('ordre',)
    #form = SpecForm
    def mostra_sprints(self,obj):
        ret = ""
        for sprint in obj.sprints.all():
            ret += sprint.nom + "<br>"
        return mark_safe(ret)
    def moduls(self,obj):
        mps = ""
        for mp in obj.mp.all():
            mps += mp.nom + "<br>"
        return mark_safe(mps)
    def descripcio_html(self,obj):
        return mark_safe(obj.descripcio)
    def get_form(self,request,obj=None,**kwargs):
        if request.user.es_alumne:
            # mostrem read-only i amaguem desc field (renderitzem html)
            self.exclude = ('descripcio',)
            self.readonly_fields = ('descripcio_html',)
        else:
            # mostrem tot normal (editable)
            self.exclude = ()
            self.readonly_fields = ()
        return super().get_form(request,obj,**kwargs)
    def get_list_display(self,request):
        # TODO: falla (ordre apareix en num enlloc de control). arreglar
        # per a admins i super
        """self.list_display = ('nom','projecte','hores_estimades','moduls','ordre',)
        self.list_editable = ('hores_estimades',)
        # modifiquem per alumnes
        if request.user.es_alumne:
            self.list_display = ('nom','projecte','hores_estimades','moduls',)
            self.list_editable = ()"""
        return super().get_list_display(request)
    def get_queryset(self,request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # filtrem projectes propis (profe)
        # + (OR) projectes dels centres on soc admin <- TODO: treure aquest? de monent no
        # + (OR) projectes en els que participo com a alumne
        cids = [ centre.id for centre in request.user.centres_admin.all() ]
        qs = qs.filter( Q(projecte__admins__in=[request.user])
                | Q(projecte__centre__in=cids)
                | Q(projecte__equips__membres__in=[request.user]) ).distinct()
        return qs
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'mp':
            try:
                parts = request.get_raw_uri().split("/")
                i = parts.index("spec")
                #print("I="+str(i))
                obj_id = parts[i+1]
                #print(obj_id)
                obj = self.get_object(request,obj_id)
                if obj:
                    kwargs['queryset'] = ModulProfessional.objects.filter(
                                cicle=obj.projecte.cicle).order_by('numero')
                else:
                    kwargs['queryset'] = Spec.objects.none()
            except:
                print("ERROR in formfield_for_manytomany (SpecAdmin)")
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)

# deprecated (no registrem pel backend, ho fem inline al Projecte admin)
#class SpecInline(admin.TabularInline):
#    model = Sprint.specs.through
class SprintAdmin(admin.ModelAdmin):
    model = Sprint
    list_display = ('nom','projecte','inici','final','hores')
    #form = SprintForm
    #filter_horizontal = ('specs',)
    ordering = ['inici',]
    search_fields = ('projecte__nom','nom')
    #inlines = [ SpecInline, ]
    #exclude = ('specs',)
    #fields = ('nom','notes','projecte','inici','final','show_specs')
    readonly_fields = ('notes_html','hores','show_specs',)
    def get_form(self,request,obj=None,**kwargs):
        if request.user.es_alumne:
            self.exclude = ('notes')
        else:
            self.exclude = ('notes_html',)
        return super().get_form(request,obj,**kwargs)
    def notes_html(self,obj):
        return mark_safe(obj.notes)
    def show_specs(self,obj):
        ret = "<ol>\n"
        for spec in obj.specs.all():
            ret += '<li>{}<dl>'.format(spec.nom)
            ret += '<dd>Hores estimades: {}</dd>'.format(spec.hores_estimades)
            ret += '<dd>'
            for mp in spec.mp.all():
                ret += '{} '.format(mp.nom[:4])
            ret += '</dd>\n'
            ret += '<dd>{}</dd>\n'.format(spec.descripcio)
            ret += '</dl>\n'
            #print(spec.nom)
            #print(spec.notes)
        ret += '</ol>\n'
        return mark_safe(ret)
    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'specs':
            try:
                parts = request.get_raw_uri().split("/")
                i = parts.index("sprint")
                #print("I="+str(i))
                obj_id = parts[i+1]
                #print(obj_id)
                obj = self.get_object(request,obj_id)
                if obj:
                    kwargs['queryset'] = Spec.objects.filter(projecte=obj.projecte).order_by('ordre')
                else:
                    kwargs['queryset'] = Spec.objects.none()
            except:
                print("ERROR in formfield_for_manytomany (SprintAdmin)")
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)


class DoneSpecInline(admin.TabularInline):
    model = DoneSpec
    extra = 0
    can_delete = False
    ordering = ('spec__ordre',)
    readonly_fields = ('is_done','spec','hores_estimades','descripcio','mps')
    def is_done(self,obj):
        return obj.done
    is_done.boolean = True
    def hores_estimades(self,obj):
        return obj.spec.hores_estimades
    def descripcio(self,obj):
        return mark_safe(obj.spec.descripcio)
    def mps(self,obj):
        mps = ""
        for mp in obj.spec.mp.all():
            mps += mp.nom + "<br>"
        return mark_safe(mps)
class QualificacioAdmin(admin.ModelAdmin):
    model = Qualificacio
    list_display = ('__str__','projecte','sprint','equip','membres','nota','specs_completades','hores_completades','specs_completades_mps','specs_completades_mps_ponderat')
    search_fields = ('sprint__projecte__nom','sprint__nom','equip__nom')
    readonly_fields = ('sprint','equip','specs_completades','hores_completades','specs_completades_mps','specs_completades_mps_ponderat')
    inlines = [ DoneSpecInline, ]
    def get_list_display(self,*args,**kwargs):
        request = args[0]
        # no actualitzem amb alumnes (si amb profes/admins)
        # TODO: optimitzar mes (actualitzar nomes quan modifiquem projecte o equip)
        if not request.user.es_alumne:
            actualitza_qualificacions()
        return super().get_list_display(*args,**kwargs)
    def get_queryset(self,request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            # super ho veu tot
            return qs
        elif request.user.es_alumne:
            # alumne només veu qualificacions dels seus grups
            qs = qs.filter(equip__membres__in=[request.user])
            return qs
        # altres (admins centre, profes)
        # filtrem projectes propis (profe)
        # + (OR) projectes dels centres on soc admin <- TODO: treure aquest?
        # + (OR) projectes en els que participo com a membre (alumnes, TODO: treure-ho?)
        centres = request.user.centres_admin.all()
        qs = qs.filter( Q(sprint__projecte__admins__in=[request.user])
                | Q(sprint__projecte__centre__in=centres)
                | Q(sprint__projecte__equips__membres__in=[request.user]) )
        return qs.distinct()
"""
class DoneSpecAdmin(admin.ModelAdmin):
    model = DoneSpec
    list_display = ('__str__','is_done','done','projecte','sprint','equip')
    list_editable = ('done',)
    search_fields = ('qualificacio__sprint__projecte__nom','qualificacio__equip__nom','qualificacio__sprint__nom','spec__nom')
    ordering = ('qualificacio__sprint__projecte__nom','qualificacio__equip__nom','qualificacio__sprint__inici',)
    def projecte(self,obj):
        return obj.qualificacio.sprint.projecte.nom
    def sprint(self,obj):
        return obj.qualificacio.sprint.nom
    def equip(self,obj):
        return obj.qualificacio.equip.nom
    def is_done(self,obj):
        if obj.done:
            return True
        return False
    is_done.boolean = True
    def get_list_display(self,*args,**kwargs):
        actualitza_qualificacions()
        return super().get_list_display(*args,**kwargs)
"""
def actualitza_qualificacions():
    print("actualitzant...")
    sprints = Sprint.objects.all()
    for sprint in sprints:
        # cal crear una Qualificació per cada sprint i equip
        for equip in sprint.projecte.equips.all():
            quali = None
            qualis = Qualificacio.objects.filter(sprint=sprint,equip=equip)
            if not qualis:
                print("Creant Qualificacio per a "+sprint.nom)
                quali = Qualificacio(sprint=sprint,equip=equip)
                quali.save()
            else:
                quali = qualis[0]
            # cal crear un DoneSpec per cada Qualificació i Spec
            for spec in sprint.specs.all():
                dspecs = DoneSpec.objects.filter(qualificacio=quali,spec=spec)
                if not dspecs:
                    dspec = DoneSpec(qualificacio=quali,spec=spec)
                    dspec.save()
            # esborrar done_specs que s'hagin tret del sprint
            for dspec in quali.done_specs.all():
                if dspec.spec not in sprint.specs.all():
                    dspec.delete()



admin.site.register( Projecte, ProjecteAdmin )
admin.site.register( Spec, SpecAdmin )
admin.site.register( Sprint, SprintAdmin )
admin.site.register( Equip, EquipAdmin )
admin.site.register( Qualificacio, QualificacioAdmin )
#admin.site.register( DoneSpec, DoneSpecAdmin )


