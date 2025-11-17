"""
Secrets Management Module

Supports multiple secret backends:
- Environment variables (default)
- AWS Secrets Manager
- HashiCorp Vault

Configuration via SECRETS_BACKEND environment variable.
"""

import os
import json
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class SecretsBackend(ABC):
    """Abstract base class for secrets backends"""
    
    @abstractmethod
    def get_secret(self, key: str, default: Optional[str] = None) -> str:
        """Retrieve a secret by key"""
        pass


class EnvironmentSecretsBackend(SecretsBackend):
    """Default backend using environment variables"""
    
    def get_secret(self, key: str, default: Optional[str] = None) -> str:
        return os.getenv(key, default)


class AWSSecretsManagerBackend(SecretsBackend):
    """AWS Secrets Manager backend"""
    
    def __init__(self):
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            self.client = boto3.client('secretsmanager')
            self.cache: Dict[str, str] = {}
            self.ClientError = ClientError
        except ImportError:
            raise ImportError("boto3 is required for AWS Secrets Manager. Install with: pip install boto3")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> str:
        """
        Retrieve secret from AWS Secrets Manager.
        
        Key format: SECRET_NAME or SECRET_NAME:KEY for JSON secrets
        """
        if key in self.cache:
            return self.cache[key]
        
        # Check if key specifies JSON path
        if ':' in key:
            secret_name, json_key = key.split(':', 1)
        else:
            secret_name = key
            json_key = None
        
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            
            if 'SecretString' in response:
                secret_value = response['SecretString']
                
                # If it's a JSON secret and we have a key, extract it
                if json_key:
                    try:
                        secret_dict = json.loads(secret_value)
                        secret_value = secret_dict.get(json_key, default)
                    except json.JSONDecodeError:
                        return default
                
                self.cache[key] = secret_value
                return secret_value
            else:
                # Binary secret
                return default
        
        except self.ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"Secret {secret_name} not found in AWS Secrets Manager")
            else:
                print(f"Error retrieving secret from AWS: {e}")
            return default
        except Exception as e:
            print(f"Unexpected error retrieving secret: {e}")
            return default


class VaultSecretsBackend(SecretsBackend):
    """HashiCorp Vault backend"""
    
    def __init__(self):
        try:
            import hvac
            
            vault_addr = os.getenv('VAULT_ADDR', 'http://localhost:8200')
            vault_token = os.getenv('VAULT_TOKEN')
            vault_role = os.getenv('VAULT_ROLE')
            
            if not vault_token and not vault_role:
                raise ValueError("Either VAULT_TOKEN or VAULT_ROLE must be set")
            
            self.client = hvac.Client(url=vault_addr, token=vault_token)
            self.mount_point = os.getenv('VAULT_MOUNT_POINT', 'secret')
            self.cache: Dict[str, str] = {}
            
            # Verify connection
            if not self.client.is_authenticated():
                raise ValueError("Failed to authenticate with Vault")
        
        except ImportError:
            raise ImportError("hvac is required for Vault. Install with: pip install hvac")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> str:
        """
        Retrieve secret from Vault.
        
        Key format: path/to/secret:field
        Example: fortfail/orchestrator:jwt_secret
        """
        if key in self.cache:
            return self.cache[key]
        
        # Parse key format
        if ':' in key:
            path, field = key.rsplit(':', 1)
        else:
            path = key
            field = 'value'
        
        try:
            # Try KV v2 first
            try:
                response = self.client.secrets.kv.v2.read_secret_version(
                    path=path,
                    mount_point=self.mount_point
                )
                secret_data = response['data']['data']
            except Exception:
                # Fallback to KV v1
                response = self.client.secrets.kv.v1.read_secret(
                    path=path,
                    mount_point=self.mount_point
                )
                secret_data = response['data']
            
            secret_value = secret_data.get(field, default)
            
            if secret_value:
                self.cache[key] = secret_value
            
            return secret_value
        
        except Exception as e:
            print(f"Error retrieving secret from Vault: {e}")
            return default


class SecretsManager:
    """Unified secrets manager supporting multiple backends"""
    
    def __init__(self):
        backend_type = os.getenv('SECRETS_BACKEND', 'env').lower()
        
        if backend_type == 'aws':
            self.backend = AWSSecretsManagerBackend()
            print("Using AWS Secrets Manager for secrets")
        elif backend_type == 'vault':
            self.backend = VaultSecretsBackend()
            print("Using HashiCorp Vault for secrets")
        else:
            self.backend = EnvironmentSecretsBackend()
            print("Using environment variables for secrets")
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """Retrieve a secret"""
        return self.backend.get_secret(key, default)


# Global secrets manager instance
secrets_manager = SecretsManager()
