from django.apps import AppConfig


# class LibraryConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'catalog'


class CatalogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "catalog"

    def ready(self):
        import catalog.signals
        try:
            import pillow_heif
            pillow_heif.register_heif_opener()
        except Exception:
            pass
