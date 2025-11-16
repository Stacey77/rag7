from rest_framework import serializers
from .models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    """Serializer for Candidate model."""
    
    class Meta:
        model = Candidate
        fields = ['id', 'full_name', 'email', 'applied_role', 'resume', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
