from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SurfApp', '0004_playa_marea'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playa',
            name='marea_optima',
            field=models.CharField(
                blank=True,
                choices=[
                    ('pleamar', 'Pleamar'),
                    ('media_subiendo', 'Media subiendo'),
                    ('media_bajando', 'Media bajando'),
                    ('bajamar', 'Bajamar'),
                ],
                max_length=25,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='playa',
            name='marea_viva',
            field=models.BooleanField(default=False),
        ),
    ]
