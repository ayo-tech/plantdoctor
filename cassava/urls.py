"""cassava URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core import views
from django.views.generic.base import TemplateView


urlpatterns = [
    path("admin/", admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path('m/', include('core.urls')),
    path('', views.home.as_view(), name='home'),
    path('imageupload', views.ImageUpload.as_view(), name='imageupload'),
    path('register', views.register.as_view(), name='register'),
    path('registration', views.registration.as_view(), name='registration'),
    path("register_completed", TemplateView.as_view(template_name='register_completed.html'), name='register_completed'),
    path('app_slider', views.app_slider.as_view(), name='app_slider'),
    path('app_starter', views.app_starter.as_view(), name='app_starter'),
    path('app_dashboard', views.app_dashboard.as_view(), name='app_dashboard'),
    path('app_details', views.app_details.as_view(), name='app_details'),
    path('app_get_started', views.app_get_started.as_view(), name='app_get_started'),
    path('app_login', views.app_login.as_view(), name='app_login'),
    path('app_logout', views.app_logout, name='app_logout'),

    path('app_image_upload', views.appImageUpload.as_view(), name='app_image_upload'),
    path('diagnosis_history', views.diagnosis_history.as_view(), name='diagnosis_history'),
    path('diagnosis_detail/<int:pk>', views.diagnosis_detail.as_view(), name='diagnosis_detail'),

    path('treatments/<str:use>/<str:diagnosis>', views.treatments.as_view(), name='treatments'),
    path('first_aids/<str:use>/<str:diagnosis>', views.first_aids.as_view(), name='first_aids'),

    path('view_secondary_diagnosis/<str:diagnosis_id>/<str:farmer_id>', views.view_secondary_diagnosis.as_view(), name='view_secondary_diagnosis'),
    path('status_toggle/<str:diagnosis_id>/<str:farmer_id>', views.status_toggle.as_view(), name='status_toggle'),

    path('get_secondary_diagnosis/<str:diagnosis_id>/<str:farmer_id>', views.get_secondary_diagnosis.as_view(), name='get_secondary_diagnosis'),
    path('get_secondary_diagnosis_confirmed/<str:diagnosis_id>/<str:farmer_id>', views.get_secondary_diagnosis_confirmed.as_view(), name='get_secondary_diagnosis_confirmed'),

    path('secondary_diagnosis_response/<str:id>/<str:day>/<str:start>/<str:stop>', views.secondary_diagnosis_response.as_view(), name='secondary_diagnosis_response'),
    path('secondary_diagnosis_response_confirmed', TemplateView.as_view(template_name='secondary_diagnosis_response_confirmed.html'), name='secondary_diagnosis_response_confirmed'),
    path('new_treatment/<str:id>', views.new_treatment.as_view(), name='new_treatment'),
    path('register_user', views.register_user.as_view(), name='register_user'),
    path('profile/<int:pk>', views.profile.as_view(), name='profile'),
    path('secondary_diagnosis_list', views.secondary_diagnosis_list.as_view(), name='secondary_diagnosis_list'),
    path('new_treatment_confirmed', TemplateView.as_view(template_name='new_treatment_confirmed.html'), name='new_treatment_confirmed'),

    path('chats', views.chats.as_view(), name='chats'),
    path('plant_types/<int:pk>', views.plant_types.as_view(), name='plant_types'),

    path('decisive_diagnosis', views.decisive_diagnosis.as_view(), name='decisive_diagnosis'),
    path('indecisive_diagnosis', views.indecisive_diagnosis.as_view(), name='indecisive_diagnosis'),
    path('treatment_in_progress', views.treatment_in_progress.as_view(), name='treatment_in_progress'),
    path('successful_treatments', views.successful_treatments.as_view(), name='successful_treatments'),
    path('disease_database', views.disease_database.as_view(), name='disease_database'),
    path('download_app', views.download_app.as_view(), name='download_app'),
    path('all_diagnosis_details', views.all_diagnosis_details.as_view(), name='all_diagnosis_details'),



]
