from django.apps import AppConfig

class ProjectappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'projectapp'

    def ready(self):
        import projectapp.signals
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        import os

        # Register Google auth if no Google SocialApp exists
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        name = "Google"

        # Check if any Google provider exists to avoid duplicate creation
        google_apps = SocialApp.objects.filter(provider='google')
        if google_apps.count() == 0 and client_id and secret:
            app = SocialApp.objects.create(
                provider='google',
                name=name,
                client_id=client_id,
                secret=secret
            )
            app.sites.add(Site.objects.get_current())
            app.save()
