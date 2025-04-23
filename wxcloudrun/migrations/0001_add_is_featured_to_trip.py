from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='is_featured',
            field=models.BooleanField(default=False, verbose_name='是否推荐'),
        ),
    ]