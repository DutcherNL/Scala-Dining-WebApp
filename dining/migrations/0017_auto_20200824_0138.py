# Generated by Django 2.2.15 on 2020-08-23 23:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('creditmanagement', '0012_auto_20200824_0135'),
        ('dining', '0016_auto_20190514_1317'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DiningListComment',
        ),
        migrations.AddField(
            model_name='diningentry',
            name='transaction',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.PROTECT, to='creditmanagement.Transaction'),
        ),
        migrations.AlterField(
            model_name='diningcomment',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='dininglist',
            name='owners',
            field=models.ManyToManyField(help_text='Owners can manage the dining list.', related_name='owned_dining_lists', to=settings.AUTH_USER_MODEL),
        ),
    ]