"""
Proxy configuration module for coze_workload_identity.

This module provides functions to retrieve proxy and CA bundle configuration
from environment variables.
"""

import os
import tempfile
import atexit
from typing import Optional
from urllib.parse import urlparse, urlunparse, quote_plus


def HttpsProxy() -> Optional[str]:
    """
    Get HTTPS proxy URL from COZE_OUTBOUND_AUTH_PROXY environment variable.
    
    Returns:
        Optional[str]: The HTTPS proxy URL, or None if not configured.
    """
    
    proxy_url = os.environ.get('COZE_OUTBOUND_AUTH_PROXY')
    if not proxy_url:
        return None

    username = None
    password = None

    # Coze Space sandbox use identity_ticket env as password
    identity_ticket = os.environ.get('identity_ticket')
    if identity_ticket:
        username = 'space'
        password = quote_plus(identity_ticket)

    if not username or not password:
        return None
    
    # Parse the proxy URL
    parsed = urlparse(proxy_url)
    
    # Get the host part (hostname + port), ignoring existing auth
    if '@' in parsed.netloc:
        host_part = parsed.netloc.split('@')[-1]
    else:
        host_part = parsed.netloc

    # Construct new netloc with Basic Auth
    new_netloc = f"{username}:{password}@{host_part}"
    
    # Reconstruct the URL
    new_parts = list(parsed)
    new_parts[1] = new_netloc
    
    return urlunparse(new_parts)


_temp_ca_file = None

def _cleanup_temp_ca_file():
    """Cleanup the temporary CA file if it exists."""
    global _temp_ca_file
    if _temp_ca_file and os.path.exists(_temp_ca_file):
        try:
            os.remove(_temp_ca_file)
        except OSError:
            pass
    _temp_ca_file = None

atexit.register(_cleanup_temp_ca_file)


def CaBundlePath() -> Optional[str]:
    """
    Get CA bundle file path from environment variables.
    
    Priority:
    1. COZE_OUTBOUND_AUTH_PROXY_CA: Content of the CA certificate.
       If set, writes content to a temporary file and returns its path.
    2. COZE_OUTBOUND_AUTH_PROXY_CA_PATH: Path to the CA certificate file.
    
    Returns:
        Optional[str]: The CA bundle file path, or None if not configured.
        
    Raises:
        ValueError: If COZE_OUTBOUND_AUTH_PROXY_CA_PATH environment variable is set
                   but the file does not exist.
    """
    # 1. Check for CA content in environment variable
    ca_content = os.environ.get('COZE_OUTBOUND_AUTH_PROXY_CA')
    if ca_content:
        global _temp_ca_file
        if _temp_ca_file is None:
            # Create a temporary file for the CA bundle
            # We use delete=False so we can close the file and let requests open it
            # The file is registered for cleanup at exit
            fd, path = tempfile.mkstemp(text=True)
            with os.fdopen(fd, 'w') as f:
                f.write(ca_content)
            _temp_ca_file = path
        return _temp_ca_file

    # 2. Check for CA path in environment variable
    ca_bundle_path = os.environ.get('COZE_OUTBOUND_AUTH_PROXY_CA_PATH')
    if not ca_bundle_path:
        return None
    
    if not os.path.exists(ca_bundle_path):
        raise ValueError(
            f"COZE_OUTBOUND_AUTH_PROXY_CA_PATH environment variable is set to '{ca_bundle_path}' "
            f"but the file does not exist. Please check the path."
        )
    return ca_bundle_path
