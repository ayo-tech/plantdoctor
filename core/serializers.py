from rest_framework import serializers
from django.contrib.auth.models import User
from . import models
from django.conf import settings
from django.core.mail import send_mass_mail, send_mail

# class rent

class diagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.diagnosis
        fields = ('id', 'image', 'label', 'done', 'date')