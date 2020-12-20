# Generated by Django 3.1.4 on 2020-12-20 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20201220_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='alpha_2',
            field=models.CharField(default='', max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='country',
            name='alpha_3',
            field=models.CharField(default='', max_length=3),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='film',
            name='hasGenre',
        ),
        migrations.AddField(
            model_name='film',
            name='hasGenre',
            field=models.ManyToManyField(null=True, to='app.Genre'),
        ),
    ]
