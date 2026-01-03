"""
Shared fixtures for convert_prepare tests
"""
import os
import pytest


@pytest.fixture(scope="session")
def ado_token():
    """
    Get ADO token from environment variable.
    
    In Azure Pipeline: Set via env in build.yml
    Locally: Run the following command to set the token
        az login       
        $token = az account get-access-token --resource 499b84ac-1321-427f-aa17-267ca6975798 --query accessToken -o tsv
        $env:SYSTEM_ACCESSTOKEN = $token
    
    Returns:
        str: ADO token or empty string if not available
    """
    return os.getenv("SYSTEM_ACCESSTOKEN", "")