# Generated by Django 2.2.4 on 2019-10-16 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scrum', '0005_merge_20190914_0948'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sprint',
            name='specs',
        ),
        migrations.AddField(
            model_name='spec',
            name='sprints',
            field=models.ManyToManyField(blank=True, related_name='sprints', to='scrum.Sprint'),
        ),
    ]
