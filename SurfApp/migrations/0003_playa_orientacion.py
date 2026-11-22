from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SurfApp', '0002_marine_and_weather_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='playa',
            name='ola_optima',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='playa',
            name='viento_optimo',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
