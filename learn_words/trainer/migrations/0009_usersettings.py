# Generated by Django 5.2 on 2025-04-18 11:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0008_n1_user_n10_user_n2_user_n3_user_n4_user_n5_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repeat_count', models.SmallIntegerField(default=1)),
                ('pause_between', models.FloatField(default=1)),
                ('delay_before_translation', models.FloatField(default=0.5)),
                ('hide_translation', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
