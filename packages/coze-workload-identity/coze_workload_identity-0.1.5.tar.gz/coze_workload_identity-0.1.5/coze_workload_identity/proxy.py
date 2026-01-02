"""
Proxy configuration module for coze_workload_identity.

This module provides functions to retrieve proxy and CA bundle configuration
from environment variables.
"""

import os
from typing import Optional


def HttpsProxy() -> Optional[str]:
    """
    Get HTTPS proxy URL from COZE_OUTBOUND_AUTH_PROXY environment variable.
    
    Returns:
        Optional[str]: The HTTPS proxy URL, or None if not configured.
    """
    return os.environ.get('COZE_OUTBOUND_AUTH_PROXY')


def CaBundleContent() -> Optional[str]:
    """
    Get CA certificate content from COZE_OUTBOUND_AUTH_PROXY_CA environment variable.
    
    Returns:
        Optional[str]: The CA certificate content, or None if not configured.
    """
    return os.environ.get('COZE_OUTBOUND_AUTH_PROXY_CA')


def CaBundlePath() -> Optional[str]:
    """
    Get CA bundle file path from COZE_OUTBOUND_AUTH_PROXY_CA_PATH environment variable.
    
    Returns:
        Optional[str]: The CA bundle file path, or None if not configured.
        
    Raises:
        ValueError: If COZE_OUTBOUND_AUTH_PROXY_CA_PATH environment variable is set
                   but the file does not exist.
    """
    ca_bundle_path = os.environ.get('COZE_OUTBOUND_AUTH_PROXY_CA_PATH')
    if not ca_bundle_path:
        return None
    
    if not os.path.exists(ca_bundle_path):
        raise ValueError(
            f"COZE_OUTBOUND_AUTH_PROXY_CA_PATH environment variable is set to '{ca_bundle_path}' "
            f"but the file does not exist. Please check the path."
        )
    return ca_bundle_path
