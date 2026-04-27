from django.contrib import admin

from .models import Company, JobApplication


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location', 'website')
    search_fields = ('name', 'owner__username', 'location')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('role', 'company', 'owner', 'status', 'applied_at', 'follow_up_on')
    list_filter = ('status', 'applied_at')
    search_fields = ('role', 'company__name', 'owner__username')
