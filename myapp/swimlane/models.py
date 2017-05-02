from __future__ import unicode_literals

from django.db import models


# Create your models here.


class Geo(models.Model):
    ip = models.CharField(max_length=15, primary_key=True)
    country_code = models.CharField(max_length=2, blank=True, null=True)
    country_name = models.CharField(max_length=84, blank=True, null=True)
    region_code = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    time_zone = models.CharField(max_length=128, blank=True, null=True)
    latitude = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    longitude = models.DecimalField(max_digits=7, decimal_places=4, blank=True, null=True)
    metro_code = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'geo'
        verbose_name = 'Geo Lookup'
        verbose_name_plural = 'Geo Lookups'


class Rdap(models.Model):
    ip = models.CharField(max_length=15, primary_key=True)
    name = models.CharField(max_length=125, blank=True, null=True)
    country = models.CharField(max_length=2, blank=True, null=True)
    start_address = models.CharField(max_length=15, blank=True, null=True)
    end_address = models.CharField(max_length=15, blank=True, null=True)
    entities = models.CharField(max_length=255, blank=True, null=True)
    handle = models.CharField(max_length=50, blank=True, null=True)
    ip_version = models.CharField(max_length=2, blank=True, null=True)
    lang = models.CharField(max_length=2, blank=True, null=True)
    parent_handle = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=125, blank=True, null=True)
    type = models.CharField(max_length=125, blank=True, null=True)
    last_changed = models.DateTimeField(blank=True, null=True)
    registration = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'rdap'
        verbose_name = 'RDAP Lookup'
        verbose_name_plural = 'RDAP Lookups'


class TextFile(models.Model):
    id = models.IntegerField(primary_key=True)
    file_name = models.CharField(max_length=128, blank=True, null=True)
    ip_count = models.IntegerField(blank=True, null=True)
    date_uploaded = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        db_table = 'text_file'
        verbose_name = 'text file'
        verbose_name_plural = 'text files'
