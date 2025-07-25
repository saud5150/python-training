# backend excercise/users/migrations/0002_add_google_social_app.py

from django.db import migrations
import os

def create_google_social_app(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    SocialApp = apps.get_model('socialaccount', 'SocialApp')
    site = Site.objects.get(pk=1)
    app, created = SocialApp.objects.get_or_create(
        provider='google',
        name='Google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    )
    app.sites.add(site)

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('sites', '0001_initial'),
        ('socialaccount', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_google_social_app),
    ]