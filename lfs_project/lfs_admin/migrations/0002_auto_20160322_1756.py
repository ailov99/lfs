# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import hitcount.models


class Migration(migrations.Migration):

    dependencies = [
        ('lfs_admin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonHits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateField(default=datetime.date.today)),
                ('count', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model, hitcount.models.HitCountMixin),
        ),
        migrations.AlterField(
            model_name='userregistrations',
            name='time',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
