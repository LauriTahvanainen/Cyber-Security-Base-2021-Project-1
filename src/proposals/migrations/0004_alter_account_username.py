# Generated by Django 3.2.7 on 2021-11-15 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposals', '0003_auto_20211109_1212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.CharField(max_length=1000, unique=True),
        ),
    ]
