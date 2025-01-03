import os
from django import template
from core import views, models
from datetime import datetime, timedelta

register = template.Library()

def date_default(date):
    date_formatted = datetime.strftime(date, "%Y-%m-%d")
    return date_formatted

register.filter('date_default', date_default)

def bars(trigger):
    qrcode_months = [qr.date_created.date().month for qr in models.qrcode.objects.all()]
    return [qrcode_months.count(mnth) for mnth in range(1, 13)]

register.filter('bars', bars)

def percent_acc(label):
    try:
        return int(round(float(label[0].split(" ")[-3])))
    except:
        pass

register.filter('percent_acc', percent_acc)

def disease_pred(label):
    if 'None' not in label and len(label) > 0:
        return " ".join(label[0].split(" ")[6:-5])
    else:
        return 'None'

register.filter('disease_pred', disease_pred)

def new_treatment_checker(secondary_diagnosis_lab):
    return models.new_treatment.objects.filter(secondary_diagnosis_lab=secondary_diagnosis_lab)

register.filter('new_treatment_checker', new_treatment_checker)

def youtube_editor(link):
    try:
        return link.split('youtu.be/')[1]
    except:
        return None

register.filter('youtube_editor', youtube_editor)

def comments(chat):
    comment_string = chat.comment
    return [comm.replace('->@', ' - ') for comm in comment_string.split('/|')]

register.filter('comments', comments)

def check_secondary_diagnosis(image, user):
    try:
        diagnosis = models.diagnosis.objects.get(id=image)
        farmer = models.farmer.objects.get(member__user__id=user)
        return models.secondary_diagnosis_farmer.objects.get(diagnosis=diagnosis, farmer=farmer)
    except:
        return None

register.filter('check_secondary_diagnosis', check_secondary_diagnosis)

def farmed_crops_diseases(farmed_crop):
    directory = '/home/cassavadiseases/cassava/media/images/images/'
    diseases = [folder for folder in os.walk(directory)][0][1]
    return [dis for dis in diseases if farmed_crop in dis]

register.filter('farmed_crops_diseases', farmed_crops_diseases)

def disease_treatment(disease):
    return models.treatment.objects.filter(diagnosis=disease)

register.filter('disease_treatment', disease_treatment)


def disease_database(trigger):
    directory = '/home/cassavadiseases/cassava/media/images/images/'
    return [folder for folder in os.walk(directory)][0][1]

register.filter('disease_database', disease_database)


def diagnosis_editor(diagnosis):
    diag_string = diagnosis.replace('This image most likely belongs to ', '').replace(' with a', '').replace('percent confidence.', '')
    diag_list = diag_string.split()
    diag_list.remove(diag_list[-1])
    return " ".join(diag_list)

register.filter('diagnosis_editor', diagnosis_editor)



