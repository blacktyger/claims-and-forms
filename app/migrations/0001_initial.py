# Generated by Django 3.2.2 on 2021-05-11 14:28

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True)),
                ('file', models.FileField(upload_to='claims/')),
                ('type', models.CharField(choices=[('vitex_user', 'vitex_user'), ('miner', 'miner'), ('vitex_and_miner', 'vitex_and_miner')], default='vitex_and_miner', max_length=20)),
                ('status', models.CharField(choices=[('submitted', 'submitted'), ('accepted', 'accepted'), ('rejected', 'rejected'), ('updated', 'updated')], default='submitted', max_length=20)),
                ('telegram', models.CharField(default='', max_length=64)),
                ('details', models.TextField(blank=True, default='')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('vitex_address', models.CharField(default='', max_length=56, unique=True)),
            ],
        ),
    ]
