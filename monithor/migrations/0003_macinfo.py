# Generated by Django 5.1.3 on 2024-12-08 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monithor', '0002_rename_count_known_mac_count_int_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Macinfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token_mac_text', models.CharField(max_length=256)),
            ],
        ),
    ]