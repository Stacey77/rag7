from django.contrib import admin
from .models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'applied_role', 'created_at']
    search_fields = ['full_name', 'email', 'applied_role']
    list_filter = ['created_at']

