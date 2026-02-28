"""Cloud Provider Adapters"""
from .aws_adapter import AWSAdapter
from .azure_adapter import AzureAdapter
from .gcp_adapter import GCPAdapter

__all__ = ['AWSAdapter', 'AzureAdapter', 'GCPAdapter']
