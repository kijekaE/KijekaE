# Generated by Django 4.1.4 on 2023-03-13 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0015_contactus"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="productLink",
            field=models.CharField(blank=True, default="", max_length=500, null=True),
        ),
    ]
