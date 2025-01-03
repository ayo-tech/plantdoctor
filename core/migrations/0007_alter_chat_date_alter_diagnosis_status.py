# Generated by Django 4.0.4 on 2024-03-22 01:05

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_chat_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2024, 3, 22, 1, 5, 10, 271846, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='diagnosis',
            name='status',
            field=models.CharField(default='new', max_length=100),
        ),
    ]
