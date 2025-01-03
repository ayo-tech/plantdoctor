# Generated by Django 4.0.4 on 2024-03-23 11:10

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_diagnosis_taskimage_diagnosis_label_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='diagnosis',
            name='done',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='chat',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2024, 3, 23, 11, 10, 8, 39157, tzinfo=utc)),
        ),
    ]
