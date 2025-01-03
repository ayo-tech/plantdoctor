from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
import json


class register(models.Model):
    email = models.EmailField(blank=True, default='me@mail.com')
    phone = models.CharField(max_length=500, blank=True, default='+234 081 5566 6644')
    occupation = models.CharField(max_length=500, blank=True, default='Farmer')
    name = models.CharField(max_length=500, blank=True, default='Name here')
    farm_name = models.CharField(max_length=500, blank=True, default='Farm name here')
    farm_location = models.CharField(max_length=500, blank=True, default='Farm location')
    office_address = models.CharField(max_length=500, blank=True, default='Office address')
    position = models.CharField(max_length=500, blank=True, default='position at the office')
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone


class diagnosis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    image = models.ImageField(upload_to="uploads", blank=True, default=None)
    label = models.CharField(max_length=500, blank=True, default='None')
    disease = models.CharField(max_length=500, blank=True, default='None')
    confidence_level = models.FloatField(default=0.0)
    status = models.CharField(default='new', max_length=100)
    done = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return self.disease


class member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, primary_key=True)
    image = models.ImageField(upload_to="uploads", blank=True, default=None, null=True)
    name = models.CharField(max_length=500, blank=True, default='name here')
    email = models.EmailField(blank=True, default='me@mail.com')
    phone = models.CharField(max_length=500, blank=True, default='+234 081 5566 6644')
    address = models.TextField(blank=True, default='address')
    designation = models.CharField(max_length=2000, default="consultant", null=True, blank=True)

    def __str__(self):
        return self.name


class farmer(models.Model):
    member = models.OneToOneField(member, on_delete=models.CASCADE, default=None, primary_key=True)
    crops_farmed = models.TextField(blank=True, default='crops farmed')
    farm_location = models.TextField(blank=True, default='farm location')
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)

    def __str__(self):
        return f'farmer {self.member}'



class lab_attendant(models.Model):
    member = models.OneToOneField(member, on_delete=models.CASCADE, default=None, primary_key=True)
    lab_specialization = models.TextField(blank=True, default='lab specialization')
    lab_location = models.TextField(blank=True, default='lab location')
    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)

    def __str__(self):
        return f'lab {self.member}'


class treatment(models.Model):
    title = models.CharField(max_length=100, blank=True, default='treatment')
    diagnosis = models.TextField(blank=True, default='no diagnosis')
    prescription = models.TextField(blank=True, default='no treatment')
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'treatment {self.diagnosis}'


class secondary_diagnosis_farmer(models.Model):
    farmer = models.ForeignKey(farmer, on_delete=models.CASCADE, default=None)
    diagnosis = models.ForeignKey(diagnosis, on_delete=models.CASCADE, default=None)
    monday_start = models.TimeField(default=None, blank=True, null=True)
    monday_stop = models.TimeField(default=None, blank=True, null=True)
    tuesday_start = models.TimeField(default=None, blank=True, null=True)
    tuesday_stop = models.TimeField(default=None, blank=True, null=True)
    wednessday_start = models.TimeField(default=None, blank=True, null=True)
    wednessday_stop = models.TimeField(default=None, blank=True, null=True)
    thursday_start = models.TimeField(default=None, blank=True, null=True)
    thursday_stop = models.TimeField(default=None, blank=True, null=True)
    friday_start = models.TimeField(default=None, blank=True, null=True)
    friday_stop = models.TimeField(default=None, blank=True, null=True)

    def __str__(self):
        return f'sec diag {self.farmer}'


class secondary_diagnosis_lab(models.Model):
    lab_attendant = models.ForeignKey(lab_attendant, on_delete=models.CASCADE, default=None)
    secondary_diagnosis_farmer = models.ForeignKey(secondary_diagnosis_farmer, on_delete=models.CASCADE, default=None)
    diagnosis = models.ForeignKey(diagnosis, on_delete=models.CASCADE, default=None)
    selected_visit_day = models.CharField(max_length=500, blank=True, default='day here')

    def __str__(self):
        return f'sec diag lab {self.secondary_diagnosis_farmer.farmer}'


class new_treatment(models.Model):
    secondary_diagnosis_farmer = models.ForeignKey(secondary_diagnosis_farmer, on_delete=models.CASCADE, default=None)
    secondary_diagnosis_lab = models.ForeignKey(secondary_diagnosis_lab, on_delete=models.CASCADE, default=None)
    new_diagnosis = models.TextField(blank=True, default='no diagnosis')
    new_prescription = models.TextField(blank=True, default='no treatment')

    def __str__(self):
        return f'new diag {self.new_diagnosis}'


class chat(models.Model):
    message = models.TextField(default="message here", blank=True)
    likes = models.TextField(default="message here", blank=True)
    picture = models.ImageField(upload_to="uploads", blank=True)
    youtube_video = models.CharField(default="None", max_length=1000, blank=True)
    sound = models.FileField(upload_to="uploads", blank=True)
    comment = models.TextField(default="no comment", blank=True)
    date = models.DateTimeField(default=timezone.now(), blank=True)



