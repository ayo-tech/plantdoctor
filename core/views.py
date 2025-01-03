from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
# Create your views here.
from django.views.generic import TemplateView, FormView
from django.http import HttpResponse, HttpResponseRedirect
from . import models, forms
import os
import requests
import random
import string
from rest_framework import generics, permissions
from rest_framework.response import Response
from . import serializers
from django.contrib.auth import login
from rest_framework import permissions, status
from django.urls import reverse_lazy, reverse
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import api_view
from . import models, forms
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser, FileUploadParser, JSONParser
from rest_framework import viewsets
from datetime import datetime, timezone
from django.utils.timezone import now
from django.views.generic.base import RedirectView
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth import logout
from django.core.mail import send_mass_mail, send_mail
from django.conf import settings
import haversine as hs
import requests
import json
import numpy as np
import PIL
import GeoIP
from ipware import get_client_ip
from django.core.paginator import Paginator
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential


batch_size = 32
img_height = 180
img_width = 180
data_dir = "/home/cassavadiseases/cassava/media/images/images/"

train_ds = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  validation_split=0.2,
  subset="training",
  seed=123,
  image_size=(img_height, img_width),
  batch_size=batch_size)

class_names = train_ds.class_names
model = load_model('/home/cassavadiseases/cassava/media/neural_model/imgrec.keras')

# test the model
def img_prediction(image_url):
    image_path = tf.keras.utils.get_file(origin=image_url)

    img = tf.keras.utils.load_img(
        image_path, target_size=(img_height, img_width)
    )
    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0) # Create a batch

    predictions = model.predict(img_array)
    score = tf.nn.softmax(predictions[0])

    return "This image most likely belongs to {} with a {:.2f} percent confidence.".format(class_names[np.argmax(score)], 100 * np.max(score))


# test the model

class UploadImage(viewsets.ModelViewSet):
    serializer_class = serializers.diagnosisSerializer
    queryset = models.diagnosis.objects.all()
    parser_classes = (JSONParser, MultiPartParser, FileUploadParser)


class home(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'home'
        return context


class ImageUpload(CreateView):
    model = models.diagnosis
    fields = ['image', 'label']
    success_url = reverse_lazy('imageupload')

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idd = self.request.GET.get('delete')
        if idd is not None:
            models.diagnosis.objects.filter(id=int(idd)).delete()
        context['images'] = [(img.label.split(","), img.image, img.done, img.id) for img in models.diagnosis.objects.all()]
        context['client'] = 'image upload'
        context['dones'] = [dn.done for dn in models.diagnosis.objects.all()]
        return context


class ImageProcess(APIView):
    def get(self, request, **kwargs):
        imagelabel, imageid = self.kwargs['label'], self.kwargs['id']
        diagnosis = models.diagnosis.objects.get(id=imageid)
        diagnosis.done, diagnosis.label = True, imagelabel

        disease, confidence_level = " ".join(self.kwargs['label'].split(" ")[6:-5]), int(round(float(self.kwargs['label'].split(" ")[-3])))
        diagnosis.disease, diagnosis.confidence_level = disease, confidence_level
        if confidence_level > 60:
            diagnosis.status = 'decisive'
        else:
            diagnosis.status = 'indecisive'
        diagnosis.save()

        resp = {'state': 'image id {imgid} processed'.format(imgid=diagnosis.id), 'date': diagnosis.date}
        return Response(resp)


class register(CreateView):
    model = models.register
    fields = "__all__"
    success_url = reverse_lazy('register_completed')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'register'
        return context


class registration(ListView):
    model = models.register
    fields = "__all__"
    success_url = reverse_lazy('registration')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = models.register.objects.all()
        context['client'] = 'registration'
        return context


class app_dashboard(TemplateView):
    template_name = 'app_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'dashboard'
        return context


class app_details(TemplateView):
    template_name = 'app_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'details'
        return context


class app_slider(TemplateView):
    template_name = 'app_slider.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'App slider'
        return context


class app_starter(RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'app_slider'

    def get_redirect_url(self, args, kwargs):
        if self.request.user.is_authenticated:
            self.pattern_name = 'app_dashboard'
        return super().get_redirect_url()


class app_get_started(TemplateView):
    template_name = 'app_get_started.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'app get started'
        return context


class app_login(LoginView):
    redirect_authenticated_user = True
    template_name = 'app_login.html'

    def get_success_url(self):
        return reverse_lazy('app_dashboard')

    def form_invalid(self, form):
        messages.error(self.request,'Invalid username or password')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['go'] = self.request.session.get('go', None)
        context['client'] = 'app login'
        return context


def app_logout(request):
    logout(request)
    return redirect("app_slider")


class appImageUpload(CreateView):
    model = models.diagnosis
    fields = ['image']
    template_name = 'app_image_upload.html'
    success_url = reverse_lazy('app_image_upload')

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        self.object.save()
        img = self.object.image
        self.object.label = img_prediction('https://www.technetspace.com/media/{}'.format(img))
        self.object.user = self.request.user
        self.object.done = True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idd = self.request.GET.get('delete')
        if idd is not None:
            models.diagnosis.objects.filter(id=int(idd)).delete()

        images = [(img.label.split(","), img.image, img.done, img.id) for img in models.diagnosis.objects.all() if img.user == self.request.user]
        context['page_obj'] = Paginator(images, 5)

        context['dones'] = [dn.done for dn in models.diagnosis.objects.filter(user=self.request.user)]
        context['client'] = 'plant image upload'
        return context


class diagnosis_detail(DetailView):
    model = models.diagnosis
    template_name = 'diagnosis_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['treatments'] = models.treatment.objects.filter(diagnosis=self.object)
        context['client'] = 'diagnosis detail'
        return context


class diagnosis_history(TemplateView):
    template_name = 'diagnosis_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        idd = self.request.GET.get('delete')
        if idd is not None:
            models.diagnosis.objects.filter(id=int(idd)).delete()

        format = "%Y-%m-%d"

        start_date = self.request.GET.get('start_date')
        stop_date = self.request.GET.get('stop_date')

        if start_date is not None and stop_date is not None and start_date != '' and stop_date != '':

            start_date = datetime.strptime(start_date, format)
            stop_date = datetime.strptime(stop_date, format)

            start_date = start_date.replace(tzinfo=timezone.utc)
            stop_date = stop_date.replace(tzinfo=timezone.utc)

            images = [(img.label.split(","), img.image, img.done, img.id, img.date) for img in models.diagnosis.objects.all() if img.user == self.request.user and start_date <= img.date <= stop_date]
        else:
            images = [(img.label.split(","), img.image, img.done, img.id, img.date) for img in models.diagnosis.objects.all() if img.user == self.request.user]

        context['page_obj'] = Paginator(images, 5)
        try:
            context['start_date'] = start_date
            context['stop_date'] = stop_date
        except:
            context['start_date'] = images[0][4]
            context['stop_date'] = images[-1][4]

        context['dones'] = [dn.done for dn in models.diagnosis.objects.filter(user=self.request.user)]
        context['client'] = 'diagnosis history'
        return context


class treatments(CreateView):
    model = models.treatment
    fields = ['diagnosis', 'prescription']
    template_name = 'treatments.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('treatments', kwargs={'use': 'display', 'diagnosis': None})

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        if 'create' in self.request.POST:
            self.object.save()
        elif 'update' in self.request.POST:
            treatment_id = int(self.request.POST.get('treatment_id'))
            diagnosis, prescription = form.cleaned_data['diagnosis'], form.cleaned_data['prescription']
            models.treatment.objects.filter(id=treatment_id).update(diagnosis=diagnosis, prescription=prescription)
        elif 'delete' in self.request.POST:
            treatment_id = int(self.request.POST.get('treatment_id'))
            models.treatment.objects.filter(id=treatment_id).delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diagnosis'], context['use'] = diagnosis, use = self.kwargs['diagnosis'], self.kwargs['use']
        if use == 'display':
            context['object_list'] = models.treatment.objects.all()
        elif use == 'diagnosis':
            context['object_list'] = models.treatment.objects.filter(diagnosis=diagnosis)
        context['client'] = 'treatments'
        directory = '/home/cassavadiseases/cassava/media/images/images/'
        diseases = [folder for folder in os.walk(directory)][0][1]
        treated_diseases = [tre.diagnosis for tre in models.treatment.objects.all()]
        context['diseases'] = [ds for ds in diseases if ds not in treated_diseases]
        return context


class first_aids(CreateView):
    model = models.treatment
    fields = ['diagnosis', 'prescription']
    template_name = 'treatments.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('treatments', kwargs={'use': 'display', 'diagnosis': None})

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        if 'create' in self.request.POST:
            self.object.title = 'first_aid'
            self.object.save()
        elif 'update' in self.request.POST:
            treatment_id = int(self.request.POST.get('treatment_id'))
            diagnosis, prescription, title = form.cleaned_data['diagnosis'], form.cleaned_data['prescription'], 'first_aid'
            models.treatment.objects.filter(id=treatment_id).update(diagnosis=diagnosis, prescription=prescription, title=title)
        elif 'delete' in self.request.POST:
            treatment_id = int(self.request.POST.get('treatment_id'))
            models.treatment.objects.filter(id=treatment_id).delete()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diagnosis'], context['use'] = diagnosis, use = self.kwargs['diagnosis'], self.kwargs['use']
        if use == 'display':
            context['object_list'] = models.treatment.objects.filter(title='first_aid')
        elif use == 'diagnosis':
            context['object_list'] = models.treatment.objects.filter(title='first_aid').filter(diagnosis=diagnosis)
        context['client'] = 'first_aids'
        directory = '/home/cassavadiseases/cassava/media/images/images/'
        diseases = [folder for folder in os.walk(directory)][0][1]
        treated_diseases = [tre.diagnosis for tre in models.treatment.objects.filter(title='first_aid')]
        context['diseases'] = [ds for ds in diseases if ds not in treated_diseases]
        return context


class get_secondary_diagnosis(CreateView):
    model = models.secondary_diagnosis_farmer
    template_name = 'get_secondary_diagnosis.html'
    fields = ['monday_start', 'monday_stop', 'tuesday_start', 'tuesday_stop', 'wednessday_start', 'wednessday_stop', 'thursday_start', 'thursday_stop', 'friday_start', 'friday_stop']

    def get_success_url(self, **kwargs):
        return reverse_lazy('get_secondary_diagnosis_confirmed', kwargs={'diagnosis_id': self.kwargs['diagnosis_id'], 'farmer_id': self.kwargs['farmer_id']})

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        diagnosis = models.diagnosis.objects.get(id=self.kwargs['diagnosis_id'])
        farmer = models.farmer.objects.get(member__user__id=self.kwargs['farmer_id'])
        labs = list(models.lab_attendant.objects.all())
        distances = list(map(lambda lab: hs.haversine((farmer.longitude, farmer.latitude),(lab.longitude, lab.latitude)), labs)) + [0.0]
        selected_lab = labs[distances.index(max(distances + [0.0]))]
        self.object.farmer = farmer
        self.object.diagnosis = diagnosis
        subject, message = 'Secondary Diagnosis', f'our farmer {farmer.member.name} has accepted asecondary diagnosis for his plant that has the disease {diagnosis}'
        messages = []
        messages.append(("PLANT DOCTOR " + subject, f"Dear {selected_lab.member.name}\n" + message + "\nManagement \n Plant Doctor", settings.EMAIL_HOST_USER, [farmer.member.email, selected_lab.member.email]))
        send_mass_mail(tuple(messages), fail_silently=False)
        self.object.save()
        models.secondary_diagnosis_lab.objects.create(lab_attendant=selected_lab, secondary_diagnosis_farmer=self.object, diagnosis=diagnosis)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'get secondary diagnosis'
        return context


class secondary_diagnosis_response(RedirectView):
    permanent = True
    query_string = False
    pattern_name = 'secondary_diagnosis_response_confirmed'

    def get_redirect_url(self, *args, **kwargs):
        secondary_diagnosis = models.secondary_diagnosis_lab.objects.get(id=self.kwargs['id'])
        selected_visit_day = f"{self.kwargs['day']} between {self.kwargs['start']} and {self.kwargs['stop']}"
        secondary_diagnosis.selected_visit_day = selected_visit_day
        messages = []
        subject, message = 'Secondary Diagnosis Response', f"Our lab {secondary_diagnosis.lab_attendant.member.name} has agreed to come and take your soil samples on a {selected_visit_day}"
        messages.append(("PLANT DOCTOR " + subject, f"Dear {secondary_diagnosis.secondary_diagnosis_farmer.farmer.member.name}\n" + message + "\nManagement \n Plant Doctor", settings.EMAIL_HOST_USER, [secondary_diagnosis.secondary_diagnosis_farmer.farmer.member.email, secondary_diagnosis.lab_attendant.member.email]))
        send_mass_mail(tuple(messages), fail_silently=False)
        secondary_diagnosis.save()
        return super().get_redirect_url()


class view_secondary_diagnosis(TemplateView):
    template_name = 'view_secondary_diagnosis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        diagnosis = models.diagnosis.objects.get(id=self.kwargs['diagnosis_id'])
        farmer = models.farmer.objects.get(member__user__id=self.kwargs['farmer_id'])
        context['secondary_diagnosis_farmer'] = models.secondary_diagnosis_farmer.objects.get(diagnosis=diagnosis, farmer=farmer)
        context['secondary_diagnosis_lab'] = models.secondary_diagnosis_lab.objects.get(diagnosis=diagnosis)
        context['client'] = 'view secondary diagnosis'
        return context


class get_secondary_diagnosis_confirmed(TemplateView):
    template_name = 'get_secondary_diagnosis_confirmed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['diagnosis'] = models.diagnosis.objects.get(id=self.kwargs['diagnosis_id'])
        context['farmer'] = models.farmer.objects.get(member__user__id=self.kwargs['farmer_id'])
        return context


class secondary_diagnosis_list(ListView):
    model = models.secondary_diagnosis_lab
    paginate_by = 10
    template_name = 'secondary_diagnosis_list.html'

    def get_queryset(self, **kwargs):
        if 'delete' in self.request.GET:
            idx_list = [int(idx) for idx in self.request.GET.getlist('new_treatment_id')]
            print(idx_list)
            models.new_treatment.objects.filter(id__in=idx_list).delete()
        user = self.request.user
        query = self.request.POST.get('q')
        if query is not None:
            if user.member.designation == 'farmer':
                object_list = models.secondary_diagnosis_lab.objects.filter(secondary_diagnosis_farmer__farmer=user.member.farmer).filter(Q(diagnosis__icontains=query) | Q(selected_visit_day__icontains=query) | Q(lab_attendant__member__name__icontains=query))
            else:
                object_list = models.secondary_diagnosis_lab.objects.filter(lab_attendant=user.member.lab_attendant).filter(Q(diagnosis__icontains=query) | Q(selected_visit_day__icontains=query) | Q(secondary_diagnosis_farmer__farmer__member__name__icontains=query))
        else:
            if user.member.designation == 'farmer':
                object_list = models.secondary_diagnosis_lab.objects.filter(secondary_diagnosis_farmer__farmer=user.member.farmer)
            else:
                object_list = models.secondary_diagnosis_lab.objects.filter(lab_attendant=user.member.lab_attendant)
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'secondary diagnosis list'
        return context


class new_treatment(CreateView):
    model = models.new_treatment
    fields = ['new_diagnosis', 'new_prescription']
    success_url = reverse_lazy('new_treatment_confirmed')
    template_name = 'new_treatment.html'

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        models.treatment.objects.create(diagnosis=form.cleaned_data['new_diagnosis'], prescription=form.cleaned_data['new_prescription'])
        secondary_diagnosis_lab = models.secondary_diagnosis_lab.objects.get(id=self.kwargs['id'])
        secondary_diagnosis_farmer = secondary_diagnosis_lab.secondary_diagnosis_farmer
        self.object.secondary_diagnosis_lab = secondary_diagnosis_lab
        self.object.secondary_diagnosis_farmer = secondary_diagnosis_farmer
        messages = []
        subject, message = '', ''
        messages.append(("PLANT DOCTOR " + subject, f"Dear {secondary_diagnosis_farmer.farmer.member.name}\n" + message + "\nManagement \n Plant Doctor", settings.EMAIL_HOST_USER, [secondary_diagnosis_farmer.farmer.member.email, secondary_diagnosis_lab.lab_attendant.member.email]))
        send_mass_mail(tuple(messages), fail_silently=False)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['secondary_diagnosis_lab'] = models.secondary_diagnosis_lab.objects.get(id=self.kwargs['id'])
        context['client'] = 'new treatment'
        return context


class register_user(CreateView):
    model = models.member
    fields = ['name', 'email', 'phone', 'address', 'designation']
    success_url = reverse_lazy('register_completed')
    template_name = 'register_user.html'

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        username = form.cleaned_data['name'].split(" ")[0] + ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user = User.objects.create_user(username=username, email=form.cleaned_data['email'], password=password)
        self.object.user = user
        self.object.username = username
        self.object.password = password
        designation = form.cleaned_data['designation']
        self.object.designation = designation
        self.object.save()
        member = self.object
        if designation == 'farmer':
            models.farmer.objects.create(member=member)
        elif designation == 'lab attendant':
            models.lab_attendant.objects.create(member=member)
        messages = []
        subject, message = 'Registration Succesfull', f'username: {username} \npassword: {password}'
        messages.append(("PLANT DOCTOR " + subject, f"Dear {self.object.name}\n" + message + "\nManagement \n Plant Doctor", settings.EMAIL_HOST_USER, [self.object.email]))
        send_mass_mail(tuple(messages), fail_silently=False)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'register user'
        return context


class profile(UpdateView):
    model = models.member
    fields = ['image', 'name', 'email', 'phone', 'address']
    template_name = 'profile.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('profile', kwargs={'pk': self.object.user.id})

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        designation = self.object.designation
        if designation == 'farmer':
            farmer = self.object.farmer
            farmer.crops_farmed = self.request.POST.get('crops_farmed')
            farmer.farm_location = self.request.POST.get('farm_location')
            farmer.longitude = self.request.POST.get('longitude')
            farmer.latitude = self.request.POST.get('latitude')
            farmer.save()
        elif designation == 'lab attendant':
            lab_attendant = self.object.lab_attendant
            lab_attendant.lab_specialization = self.request.POST.get('lab_specialization')
            lab_attendant.lab_location = self.request.POST.get('lab_location')
            lab_attendant.longitude = self.request.POST.get('longitude')
            lab_attendant.latitude = self.request.POST.get('latitude')
            lab_attendant.save()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'profile'
        return context


class chats(CreateView):
    model = models.chat
    fields = ['message', 'picture', 'youtube_video', 'sound']
    success_url = reverse_lazy('chats')
    template_name = 'chats.html'

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        if 'comment' in self.request.POST:
            idx = self.request.POST.get('chat_id')
            new_comment = self.request.POST.get('new_comment') + '->@' + self.request.user.username
            chat = models.chat.objects.get(id=idx)
            comment = chat.comment
            comment_list = comment.split('/|')
            new_comment_list = comment_list + [new_comment]
            chat.comment = "/|".join(new_comment_list)
            chat.save()
        else:
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = models.chat.objects.all()
        context['client'] = 'chats'
        return context


class plant_types(UpdateView):
    model = models.farmer
    fields = ['crops_farmed']
    template_name = 'plant_types.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy('plant_types', kwargs={'pk': self.object.member.user.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['farmed_crops'] = [fc.strip() for fc in self.object.crops_farmed.split(',')]
        context['client'] = 'plant_types'
        return context


class decisive_diagnosis(ListView):
    model = models.diagnosis
    template_name = 'diagnosis.html'

    def get_queryset(self, **kwargs):
        query = self.request.POST.get('q')
        if query is not None:
            object_list = models.diagnosis.objects.filter(disease__icontains=query, status='decisive')
        else:
            object_list = models.diagnosis.objects.filter(status='decisive')
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'decisive diagnosis'
        return context


class indecisive_diagnosis(ListView):
    model = models.diagnosis
    template_name = 'diagnosis.html'

    def get_queryset(self, **kwargs):
        query = self.request.POST.get('q')
        if query is not None:
            object_list = models.diagnosis.objects.filter(disease__icontains=query, status='indecisive')
        else:
            object_list = models.diagnosis.objects.filter(status='indecisive')
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'indecisive diagnosis'
        return context


class all_diagnosis_details(ListView):
    model = models.diagnosis
    template_name = 'all_diagnosis_details.html'

    def get_queryset(self, **kwargs):
        query = self.request.POST.get('q')
        if query is not None:
            object_list = models.diagnosis.objects.filter(disease__icontains=query)
        else:
            object_list = models.diagnosis.objects.all()
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'all diagnosis details'
        return context



class treatment_in_progress(ListView):
    model = models.diagnosis
    template_name = 'diagnosis.html'

    def get_queryset(self, **kwargs):
        query = self.request.POST.get('q')
        if query is not None:
            object_list = models.diagnosis.objects.filter(disease__icontains=query, status='treatment')
        else:
            object_list = models.diagnosis.objects.filter(status='treatment')
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'treatment'
        return context


class successful_treatments(ListView):
    model = models.diagnosis
    template_name = 'diagnosis.html'

    def get_queryset(self, **kwargs):
        query = self.request.POST.get('q')
        if query is not None:
            object_list = models.diagnosis.objects.filter(disease__icontains=query, status='successful')
        else:
            object_list = models.diagnosis.objects.filter(status='successful')
        return object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client'] = 'successful'
        return context


class status_toggle(RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'view_secondary_diagnosis'

    def get_redirect_url(self, *args, **kwargs):
        diagnosis = models.diagnosis.objects.get(id=self.kwargs['diagnosis_id'])
        if diagnosis.status == 'decisive':
            diagnosis.status = 'indecisive'
        elif diagnosis.status == 'indecisive':
            diagnosis.status = 'treatment'
        elif diagnosis.status == 'treatment':
            diagnosis.status = 'successful'
        elif diagnosis.status == 'successful':
            diagnosis.status = 'decisive'
        diagnosis.save()
        return super().get_redirect_url(self.kwargs['diagnosis_id'], self.kwargs['farmer_id'])


class disease_database(TemplateView):
    template_name = 'disease_database.html'


class download_app(TemplateView):
    template_name = 'download_app.html'


