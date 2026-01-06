# Generated migration for updating StudentProfile with department choices

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_update_department_choices'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='department',
            field=models.CharField(
                choices=[('BCA', 'BCA'), ('IT', 'IT')],
                default='BCA',
                max_length=100
            ),
        ),
    ]
