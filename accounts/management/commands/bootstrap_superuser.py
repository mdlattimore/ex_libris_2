from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Bootstraps a superuser using environment variables."

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not email or not password:
            self.stderr.write("Environment variables DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD are required.")
            return

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Superuser {email} created."))
        else:
            self.stdout.write(f"Superuser {email} already exists.")
