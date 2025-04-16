# Generated by Django 5.2 on 2025-04-16 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow_builder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowstep',
            name='trigger_from',
            field=models.CharField(choices=[('kafka', 'Kafka'), ('mq', 'MQ'), ('cps', 'CPS'), ('database', 'DB')], default='init', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='workflowstep',
            name='trigger_to',
            field=models.CharField(choices=[('kafka', 'Kafka'), ('mq', 'MQ'), ('cps', 'CPS'), ('database', 'DB')], default='init', max_length=50),
            preserve_default=False,
        ),
    ]
