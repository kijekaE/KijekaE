# Generated by Django 4.1.4 on 2023-03-10 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_category_categorylink"),
    ]

    operations = [
        migrations.CreateModel(
            name="Footer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "mobile1Label",
                    models.CharField(blank=True, default="", max_length=500, null=True),
                ),
                ("isMobile1Label", models.BooleanField(default=False)),
                (
                    "mobile2Label",
                    models.CharField(blank=True, default="", max_length=500, null=True),
                ),
                ("isMobile2Label", models.BooleanField(default=False)),
                (
                    "mobile3Label",
                    models.CharField(blank=True, default="", max_length=500, null=True),
                ),
                ("isMobile3Label", models.BooleanField(default=False)),
                (
                    "email1Label",
                    models.CharField(blank=True, default="", max_length=500, null=True),
                ),
                ("isEmail1Label", models.BooleanField(default=False)),
                (
                    "email2Label",
                    models.CharField(blank=True, default="", max_length=500, null=True),
                ),
                ("isEmail2Label", models.BooleanField(default=False)),
                (
                    "email3Label",
                    models.CharField(blank=True, default="", max_length=500, null=True),
                ),
                ("isEmail3Label", models.BooleanField(default=False)),
                (
                    "addressLabel",
                    models.CharField(blank=True, default="", max_length=500, null=True),
                ),
                ("isaddressLabel", models.BooleanField(default=False)),
                (
                    "aboutUsLabel",
                    models.CharField(blank=True, default="", max_length=500, null=True),
                ),
                ("isaboutUsLabel", models.BooleanField(default=False)),
                (
                    "contactLabel",
                    models.CharField(blank=True, default="", max_length=500, null=True),
                ),
                ("iscontactLabel", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="OurClients",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=500)),
                ("image", models.ImageField(upload_to="images/")),
                (
                    "link",
                    models.CharField(blank=True, default="", max_length=500, null=True),
                ),
            ],
        ),
    ]
