from django import forms
from django.apps import apps
from django.contrib import admin
from django.contrib.admin import widgets
from django.db.models import Q
from django.forms import ModelForm
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from app.models import Claim, ClaimFile, VitexAccount


fields = ['file', 'name', 'telegram', 'status', 'id', 'files', 'timestamp', 'vitex_address', 'team_comments', 'details',
          'estimations', 'images']


admin.site.register(VitexAccount)


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    readonly_fields = ('images',)

    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.list_display = [field.name for field in model._meta.fields if field.name in fields]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['files'].queryset = ClaimFile.objects.filter(
                Q(name__istartswith=obj.id))
        return form

    def images(self, obj):
        html = '<a href="{url}" target="_blank">' \
               '<img style="margin: 10px"; height="200px" src="{url}" /></a>'
        return format_html(''.join(html.format(url=image.file.url) for image in obj.files.all()))


@admin.register(ClaimFile)
class ClaimFileAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.list_display = ['file', 'timestamp']



