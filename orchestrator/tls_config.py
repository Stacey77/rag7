"""
TLS/HTTPS Configuration Module

Supports loading TLS certificates for production deployment.
Configure via environment variables:
- TLS_ENABLED: Enable TLS (default: false)
- TLS_CERT_FILE: Path to certificate file
- TLS_KEY_FILE: Path to private key file
- TLS_CA_FILE: Path to CA certificate file (optional)
"""

import os
import ssl
from pathlib import Path
from typing import Optional, Dict


def get_ssl_context() -> Optional[ssl.SSLContext]:
    """
    Create SSL context for HTTPS if TLS is enabled.
    
    Returns:
        ssl.SSLContext if TLS is enabled and certificates are found, None otherwise
    """
    tls_enabled = os.getenv("TLS_ENABLED", "false").lower() == "true"
    
    if not tls_enabled:
        return None
    
    cert_file = os.getenv("TLS_CERT_FILE")
    key_file = os.getenv("TLS_KEY_FILE")
    ca_file = os.getenv("TLS_CA_FILE")
    
    if not cert_file or not key_file:
        print("Warning: TLS_ENABLED=true but TLS_CERT_FILE or TLS_KEY_FILE not set")
        return None
    
    cert_path = Path(cert_file)
    key_path = Path(key_file)
    
    if not cert_path.exists():
        print(f"Warning: Certificate file not found: {cert_file}")
        return None
    
    if not key_path.exists():
        print(f"Warning: Key file not found: {key_file}")
        return None
    
    # Create SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # Load certificate and key
    try:
        ssl_context.load_cert_chain(
            certfile=str(cert_path),
            keyfile=str(key_path)
        )
        
        # Load CA certificate if provided
        if ca_file:
            ca_path = Path(ca_file)
            if ca_path.exists():
                ssl_context.load_verify_locations(cafile=str(ca_path))
            else:
                print(f"Warning: CA file not found: {ca_file}")
        
        # Set modern TLS settings
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        print(f"TLS enabled with certificate: {cert_file}")
        return ssl_context
    
    except Exception as e:
        print(f"Error loading TLS certificates: {e}")
        return None


def get_uvicorn_ssl_config() -> Dict:
    """
    Get SSL configuration for uvicorn.
    
    Returns:
        Dictionary with ssl_keyfile and ssl_certfile if TLS is enabled
    """
    tls_enabled = os.getenv("TLS_ENABLED", "false").lower() == "true"
    
    if not tls_enabled:
        return {}
    
    cert_file = os.getenv("TLS_CERT_FILE")
    key_file = os.getenv("TLS_KEY_FILE")
    ca_file = os.getenv("TLS_CA_FILE")
    
    if not cert_file or not key_file:
        return {}
    
    config = {
        "ssl_keyfile": key_file,
        "ssl_certfile": cert_file,
    }
    
    if ca_file:
        config["ssl_ca_certs"] = ca_file
    
    # Set TLS version
    config["ssl_version"] = ssl.PROTOCOL_TLS_SERVER
    
    return config
