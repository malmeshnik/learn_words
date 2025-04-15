# Generated by Django 5.2 on 2025-04-15 08:18

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0007_n1_n10_n2_n3_n4_n5_n6_n7_n8_n9'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='n1',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='N1', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='n10',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='N10', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='n2',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='N2', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='n3',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='N3', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='n4',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='N4', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='n5',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='N5', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='n6',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='N6', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='n7',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='N7', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='n8',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='N8', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='n9',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='N9', to=settings.AUTH_USER_MODEL),
        ),
    ]
