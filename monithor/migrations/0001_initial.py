# Generated by Django 5.1.3 on 2024-12-01 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Known_mac',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac_text', models.CharField(max_length=20)),
                ('mac_info', models.CharField(max_length=100)),
                ('device', models.CharField(max_length=100)),
                ('count', models.IntegerField(default=0)),
                ('first_seen_date', models.DateTimeField(verbose_name='first seen')),
                ('last_seen_date', models.DateTimeField(verbose_name='last seen')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_text', models.CharField(max_length=50)),
                ('user_text', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_text', models.CharField(max_length=20)),
                ('oid_text', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Unknown_mac',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac_text', models.CharField(max_length=20)),
                ('mac_info', models.CharField(max_length=100)),
                ('device', models.CharField(max_length=100)),
                ('first_seen_date', models.DateTimeField(verbose_name='first seen')),
                ('last_seen_date', models.DateTimeField(verbose_name='last seen')),
            ],
        ),
    ]
