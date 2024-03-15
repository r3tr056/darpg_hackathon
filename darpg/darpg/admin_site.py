from django.contrib.admin import AdminSite
from authentication.models import OtpCode, CustomUser

class DARPGAdminSite(AdminSite):
    site_header = 'DARPG administration'
    site_title = 'DARPG site admin'

    def __init__(self, name='admin'):
        super().__init__(name)

    def has_permission(self, request):
        return request.user.is_superuser


admin_site = DARPGAdminSite()

admin_site.register(CustomUser)
admin_site.register(OtpCode)