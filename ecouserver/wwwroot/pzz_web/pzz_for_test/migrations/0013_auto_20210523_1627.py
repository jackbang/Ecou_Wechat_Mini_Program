# Generated by Django 3.1.7 on 2021-05-23 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pzz_for_test', '0012_testadminstoreinfo_adminstore_verify'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testadminstoreinfo',
            name='adminStore_verify',
            field=models.SmallIntegerField(default=1),
        ),
    ]
