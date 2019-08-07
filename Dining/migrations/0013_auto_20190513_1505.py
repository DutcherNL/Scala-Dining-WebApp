# Generated by Django 2.2 on 2019-05-13 13:05

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Dining', '0012_auto_20190728_1359'),
    ]

    operations = [
        migrations.AddField(
            model_name='dininglist',
            name='owners',
            field=models.ManyToManyField(help_text='These users can manage the dining list', related_name='owned_dining_lists', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='dininglist',
            name='dining_cost',
            field=models.DecimalField(blank=True, decimal_places=2, default=None, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='dinner cost per person'),
        ),
    ]