from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.secondary_diagnosis_lab)
admin.site.register(models.register)

admin.site.register(models.diagnosis)
admin.site.register(models.member)
admin.site.register(models.farmer)
admin.site.register(models.lab_attendant)
admin.site.register(models.treatment)
admin.site.register(models.secondary_diagnosis_farmer)
admin.site.register(models.new_treatment)
admin.site.register(models.chat)