# Generated by Django 5.2 on 2025-04-11 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0004_room_user_delete_userroom'),
    ]

    operations = [
        migrations.CreateModel(
            name='SentenceTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Construction',
        ),
    ]
