# Generated by Django 3.2.2 on 2021-05-11 14:39

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='estimations',
            field=jsonfield.fields.JSONField(default={}),
        ),
        migrations.AddField(
            model_name='claim',
            name='team_comments',
            field=models.TextField(blank=True, default=''),
        ),
    ]
