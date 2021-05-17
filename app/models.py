from decimal import Decimal

from django.utils import timezone
from model_utils import Choices
from django.db import models
import pandas as pd
import jsonfield
import uuid


class Claim(models.Model):
    STATUS = Choices('preparing', 'submitted', 'accepted', 'rejected', 'updated')
    id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=STATUS, default=STATUS.preparing)
    telegram = models.CharField(max_length=64, blank=True)
    vitex_address = models.CharField(max_length=56, default='', blank=True, null=True)
    details = models.TextField(default='', blank=True, null=True)
    estimations = jsonfield.JSONField(default={})
    timestamp = models.DateTimeField(auto_now_add=True)
    team_comments = models.TextField(default='', blank=True, null=True)
    files = models.ManyToManyField('ClaimFile', related_name='claim')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"CLAIM USER: {self.telegram}"


class ClaimFile(models.Model):
    id = models.UUIDField(unique=True, primary_key=True, default=uuid.uuid4)
    file = models.ImageField(upload_to='claims/')
    name = models.CharField(max_length=64, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['-timestamp']


class VitexAccount(models.Model):
    address = models.CharField(max_length=56, default='', blank=True, null=True)
    exchange = models.DecimalField(decimal_places=8, max_digits=32, default=0, blank=True, null=True)
    wallet = models.DecimalField(decimal_places=8, max_digits=32, default=0, blank=True, null=True)
    total = models.DecimalField(decimal_places=8, max_digits=32, default=0, blank=True, null=True)

    def add_data(self, file):
        df = pd.read_csv(file)
        columns = ['ViteX DEX', 'Wallet Balance', 'Balance Total']
        for i, row in df.iterrows():
            if any((x in ['-', '/']) for x in row['ViteX DEX']):
                row['ViteX DEX'] = '0'
            print(row['ViteX DEX'])

            for col in columns:
                row[col] = row[col].replace(',', '')
                print(row[col])

            VitexAccount.objects.create(
                address=row['Vite Address'],
                exchange=Decimal(row['ViteX DEX']),
                wallet=Decimal(row['Wallet Balance']),
                total=Decimal(row['Balance Total'])
                )

    def __str__(self):
        return f"{self.address}"
