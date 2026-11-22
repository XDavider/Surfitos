from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('SurfApp', '0003_playa_orientacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='playa',
            name='marea_optima',
            field=models.CharField(
                blank=True,
                choices=[('pleamar', 'Pleamar'), ('media', 'Media marea'), ('bajamar', 'Bajamar')],
                max_length=20,
                null=True,
            ),
        ),
    ]
