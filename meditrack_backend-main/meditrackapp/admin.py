from django.contrib import admin

from .models import Admin

# Use a Proxy model to help distinguish this in the Admin UI
class DashboardAdmin(Admin):
    class Meta:
        proxy = True
        verbose_name = "Dashboard Admin"
        verbose_name_plural = "Dashboard Admins"

admin.site.register(DashboardAdmin)
