# Generated by Django 3.2.2 on 2021-05-13 17:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20210513_1826'),
    ]

    operations = [
        migrations.AddField(
            model_name='claim',
            name='claim_files',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='app.claim'),
        ),
    ]