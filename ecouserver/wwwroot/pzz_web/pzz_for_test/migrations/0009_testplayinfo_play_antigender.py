# Generated by Django 3.1.7 on 2021-05-21 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pzz_for_test', '0008_auto_20210515_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='testplayinfo',
            name='play_antigender',
            field=models.BooleanField(default=False),
        ),
    ]
