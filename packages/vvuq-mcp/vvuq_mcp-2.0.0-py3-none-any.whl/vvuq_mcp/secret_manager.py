"""
Secrets management for VVUQ-MCP.
"""

import os
import logging
from typing import Optional
from google.cloud import secretmanager

logger = logging.getLogger(__name__)

# Cache for secrets to avoid repeated API calls
_secret_cache = {}

def get_secret(secret_id: str, project_id: str = "axiomatic-ai-001") -> Optional[str]:
    """
    Retrieve a secret from Google Secret Manager or environment variables.
    
    Priority:
    1. Environment Variable (local override)
    2. Google Secret Manager
    
    Args:
        secret_id: The ID of the secret (e.g., "github-token")
        project_id: GCP Project ID
        
    Returns:
        The secret value string, or None if not found
    """
    # 1. Check environment variable (convert dashes to underscores + uppercase)
    env_var_name = secret_id.replace("-", "_").upper()
    env_val = os.getenv(env_var_name)
    if env_val:
        return env_val
        
    # 2. Check cache
    if secret_id in _secret_cache:
        return _secret_cache[secret_id]
        
    # 3. Check Google Secret Manager
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
        
        # Cache it
        _secret_cache[secret_id] = secret_value
        return secret_value
        
    except Exception as e:
        logger.warning(f"Could not fetch secret '{secret_id}' from GSM via library: {e}")
        
        # 4. Fallback: Try gcloud CLI (local dev environment)
        try:
            import subprocess
            # Use full path to gcloud found via `which gcloud`
            gcloud_path = "/Users/englund/google-cloud-sdk/bin/gcloud"
            
            with open("/tmp/secret_debug.log", "a") as f:
                f.write(f"Attempting fallback for {secret_id} using {gcloud_path}\n")
            
            result = subprocess.run(
                [gcloud_path, "secrets", "versions", "access", "latest", f"--secret={secret_id}", "--quiet"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
                env=os.environ
            )
            secret_value = result.stdout.strip()
            
            if secret_value:
                _secret_cache[secret_id] = secret_value
                return secret_value
                
        except Exception as cli_error:
            logger.warning(f"Fallback to gcloud CLI failed for '{secret_id}': {cli_error}")
            
        return None
