# Generated by Django 4.1.11 on 2023-09-16 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_productimage_image4_productimage_image5_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productimage',
            name='image1',
            field=models.ImageField(blank=True, null=True, upload_to='mimages/'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image2',
            field=models.ImageField(blank=True, null=True, upload_to='mimages/'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image3',
            field=models.ImageField(blank=True, null=True, upload_to='mimages/'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image4',
            field=models.ImageField(blank=True, null=True, upload_to='mimages/'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image5',
            field=models.ImageField(blank=True, null=True, upload_to='mimages/'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image6',
            field=models.ImageField(blank=True, null=True, upload_to='mimages/'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image7',
            field=models.ImageField(blank=True, null=True, upload_to='mimages/'),
        ),
    ]
