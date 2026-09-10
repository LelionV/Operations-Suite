from django.contrib import admin
from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'group', 'get_hod', 'member_count']
    search_fields = ['name', 'code']

    def get_hod(self, obj):
        hod = obj.get_hod()
        return str(hod) if hod else '⚠ No HOD assigned'
    get_hod.short_description = 'HOD'

    def member_count(self, obj):
        return obj.members.filter(is_active=True).count()
    member_count.short_description = 'Members'
