"""
OneDrive Upload Package

Simple OneDrive upload for company-wide access using app-only authentication.

Usage:
    from onedrive_upload import upload
    
    # Using environment variables
    upload("file.txt", "Folder/file.txt")
    
    # Passing credentials
    upload("file.txt", app_id="...", secret="...", tenant="...", user="...")
"""

from .core import upload, OneDriveUploadError

__version__ = "1.0.0"
__all__ = ["upload", "OneDriveUploadError"]
