# Generated by Django 3.2.2 on 2021-05-13 17:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_claim_claim_files'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='claim',
            name='claim_files',
        ),
        migrations.AlterField(
            model_name='claimfile',
            name='claim',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='app.claim'),
        ),
    ]
