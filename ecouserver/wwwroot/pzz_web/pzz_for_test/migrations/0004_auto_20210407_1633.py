# Generated by Django 3.1.7 on 2021-04-07 16:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pzz_for_test', '0003_auto_20210405_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='testplayinfo',
            name='play_duration',
            field=models.PositiveSmallIntegerField(default=3),
        ),
        migrations.AddField(
            model_name='teststoreinfo',
            name='store_info',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AddField(
            model_name='teststoreinfo',
            name='store_status',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='TestLabelInfo',
            fields=[
                ('label_id', models.AutoField(primary_key=True, serialize=False)),
                ('label_type', models.PositiveSmallIntegerField(default=0)),
                ('label_content', models.CharField(default='', max_length=5)),
                ('label_create_time', models.DateTimeField(auto_now_add=True)),
                ('play_id', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='all_labels', to='pzz_for_test.testplayinfo')),
            ],
            options={
                'ordering': ('label_create_time',),
            },
        ),
    ]