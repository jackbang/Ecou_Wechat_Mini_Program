# Generated by Django 3.1.7 on 2021-04-05 18:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pzz_for_test', '0002_auto_20210405_1504'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestPlayInfo',
            fields=[
                ('play_id', models.AutoField(primary_key=True, serialize=False)),
                ('play_name', models.CharField(blank=True, default='', max_length=20)),
                ('play_headcount', models.PositiveSmallIntegerField(blank=True, default=0)),
                ('play_male_num', models.PositiveSmallIntegerField(blank=True, default=0)),
                ('play_female_num', models.PositiveSmallIntegerField(blank=True, default=0)),
                ('play_score', models.PositiveSmallIntegerField(blank=True, default=3)),
                ('play_intro', models.TextField(blank=True, default='')),
                ('play_img', models.CharField(blank=True, default='', max_length=20)),
                ('play_is_original', models.BooleanField(blank=True, default=False)),
                ('play_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('play_created',),
            },
        ),
        migrations.AlterField(
            model_name='teststoreinfo',
            name='store_pic',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.CreateModel(
            name='TestQueueInfo',
            fields=[
                ('queue_id', models.AutoField(primary_key=True, serialize=False)),
                ('queue_status', models.SmallIntegerField(default=0)),
                ('queue_create_time', models.DateTimeField(auto_now_add=True)),
                ('queue_end_time', models.DateTimeField()),
                ('queue_current_num', models.SmallIntegerField(default=0)),
                ('queue_current_male_num', models.SmallIntegerField(default=0)),
                ('queue_current_female_num', models.SmallIntegerField(default=0)),
                ('queue_allow_antigender', models.BooleanField(default=False)),
                ('play_id', models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='all_queues', to='pzz_for_test.testplayinfo')),
                ('store_id', models.ForeignKey(default=0, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='all_queues', to='pzz_for_test.teststoreinfo')),
            ],
            options={
                'ordering': ('queue_create_time',),
            },
        ),
    ]
