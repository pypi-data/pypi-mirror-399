"""
OneDrive Upload - Company-Wide File Upload

A simple Python package for uploading files to a shared OneDrive account
using Microsoft Graph API with app-only authentication.

Supports files up to 250GB using resumable upload sessions.
"""

import os
import logging
import msal
import requests
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

# Upload thresholds
SIMPLE_UPLOAD_LIMIT = 4 * 1024 * 1024  # 4MB
CHUNK_SIZE = 10 * 1024 * 1024  # 10MB chunks for large files


class OneDriveUploadError(Exception):
    """Exception raised for OneDrive upload errors."""
    pass


def upload(file_path, destination_path=None, *,
           app_id=None, secret=None, tenant=None, user=None,
           silent=False, chunk_size=CHUNK_SIZE):
    """
    Upload a file to company OneDrive. Automatically handles large files.
    
    Args:
        file_path: Path to the local file to upload.
        destination_path: Destination path in OneDrive. Defaults to filename.
        app_id: Azure Application ID (or set APPLICATION_ID env var).
        secret: Azure Client Secret (or set CLIENT_SECRET env var).
        tenant: Azure Tenant ID (or set TENANT_ID env var).
        user: Target OneDrive user email (or set TARGET_USER_EMAIL env var).
        silent: If True, suppress progress output. Default False.
        chunk_size: Size of chunks for large file upload. Default 10MB.
    
    Returns:
        dict: Response containing 'url', 'id', 'name', 'size'.
    
    Raises:
        OneDriveUploadError: If credentials missing or upload fails.
        FileNotFoundError: If local file does not exist.
    """
    # Get credentials
    app_id = app_id or os.getenv('APPLICATION_ID')
    secret = secret or os.getenv('CLIENT_SECRET')
    tenant = tenant or os.getenv('TENANT_ID')
    target_user = user or os.getenv('TARGET_USER_EMAIL')
    
    missing = []
    if not app_id: missing.append('app_id/APPLICATION_ID')
    if not secret: missing.append('secret/CLIENT_SECRET')
    if not tenant: missing.append('tenant/TENANT_ID')
    if not target_user: missing.append('user/TARGET_USER_EMAIL')
    
    if missing:
        raise OneDriveUploadError(f"Missing credentials: {', '.join(missing)}")
    
    # Validate file
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_size = file_path.stat().st_size
    
    if destination_path is None:
        destination_path = file_path.name
    
    # Get access token
    token = _get_token(app_id, secret, tenant)
    headers = {'Authorization': f'Bearer {token}'}
    
    # Choose upload method based on file size
    if file_size <= SIMPLE_UPLOAD_LIMIT:
        return _simple_upload(file_path, destination_path, target_user, headers, silent)
    else:
        return _chunked_upload(file_path, destination_path, target_user, headers, 
                               file_size, chunk_size, silent)


def _get_token(app_id, secret, tenant):
    """Get app-only access token."""
    client = msal.ConfidentialClientApplication(
        client_id=app_id,
        client_credential=secret,
        authority=f'https://login.microsoftonline.com/{tenant}'
    )
    
    result = client.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    
    if 'access_token' not in result:
        raise OneDriveUploadError(f"Auth failed: {result.get('error_description')}")
    
    return result['access_token']


def _simple_upload(file_path, destination_path, target_user, headers, silent):
    """Simple upload for files <= 4MB."""
    url = f"https://graph.microsoft.com/v1.0/users/{target_user}/drive/root:/{destination_path}:/content"
    
    upload_headers = headers.copy()
    upload_headers['Content-Type'] = 'application/octet-stream'
    
    if not silent:
        print(f"Uploading: {file_path.name} ({_format_size(file_path.stat().st_size)})")
    
    with open(file_path, 'rb') as f:
        response = requests.put(url, headers=upload_headers, data=f.read())
    
    if response.status_code in [200, 201]:
        return _parse_response(response, destination_path, silent)
    else:
        raise OneDriveUploadError(f"Upload failed: {response.status_code} - {response.text}")


def _chunked_upload(file_path, destination_path, target_user, headers, 
                    file_size, chunk_size, silent):
    """Resumable upload for large files using upload session."""
    
    # Step 1: Create upload session
    session_url = f"https://graph.microsoft.com/v1.0/users/{target_user}/drive/root:/{destination_path}:/createUploadSession"
    
    session_body = {
        "item": {
            "@microsoft.graph.conflictBehavior": "replace",
            "name": Path(destination_path).name
        }
    }
    
    session_headers = headers.copy()
    session_headers['Content-Type'] = 'application/json'
    
    response = requests.post(session_url, headers=session_headers, json=session_body)
    
    if response.status_code not in [200, 201]:
        raise OneDriveUploadError(f"Failed to create upload session: {response.text}")
    
    upload_url = response.json().get('uploadUrl')
    
    if not silent:
        print(f"Uploading: {file_path.name} ({_format_size(file_size)})")
    
    # Step 2: Upload file in chunks
    uploaded = 0
    
    with open(file_path, 'rb') as f:
        while uploaded < file_size:
            chunk_start = uploaded
            chunk_end = min(uploaded + chunk_size, file_size) - 1
            chunk_data = f.read(chunk_size)
            actual_chunk_size = len(chunk_data)
            
            chunk_headers = {
                'Content-Length': str(actual_chunk_size),
                'Content-Range': f'bytes {chunk_start}-{chunk_end}/{file_size}'
            }
            
            response = requests.put(upload_url, headers=chunk_headers, data=chunk_data)
            
            if response.status_code not in [200, 201, 202]:
                raise OneDriveUploadError(f"Chunk upload failed: {response.status_code} - {response.text}")
            
            uploaded += actual_chunk_size
            
            if not silent:
                progress = (uploaded / file_size) * 100
                print(f"  Progress: {progress:.1f}% ({_format_size(uploaded)} / {_format_size(file_size)})", end='\r')
    
    if not silent:
        print()  # New line after progress
    
    # Final response contains file info
    if response.status_code in [200, 201]:
        return _parse_response(response, destination_path, silent)
    else:
        raise OneDriveUploadError(f"Upload finalization failed: {response.text}")


def _parse_response(response, destination_path, silent):
    """Parse upload response and return result dict."""
    data = response.json()
    result = {
        'url': data.get('webUrl'),
        'id': data.get('id'),
        'name': data.get('name'),
        'size': data.get('size')
    }
    if not silent:
        print(f"Uploaded: {destination_path}")
    return result


def _format_size(size_bytes):
    """Format bytes into human readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
