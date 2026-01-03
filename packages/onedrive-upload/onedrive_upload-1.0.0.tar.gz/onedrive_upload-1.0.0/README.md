# OneDrive Upload

Simple Python package for uploading files to a shared OneDrive account.

**Supports files up to 250GB** using resumable upload sessions.

## Installation

```bash
pip install .
```

## Setup

Set environment variables:

```bash
export APPLICATION_ID="your-app-id"
export CLIENT_SECRET="your-secret"
export TENANT_ID="your-tenant-id"
export TARGET_USER_EMAIL="target@company.com"
```

## Usage

```python
from onedrive_upload import upload

# Small file (< 4MB) - simple upload
upload("report.pdf", "Reports/report.pdf")

# Large file (any size) - automatic chunked upload
upload("backup.zip", "Backups/backup.zip")

# With credentials
upload("file.txt", app_id="...", secret="...", tenant="...", user="...")

# Silent mode (no output)
upload("file.txt", silent=True)
```

## Features

- Automatic chunked upload for files > 4MB
- Progress display for large files
- No file size limit (up to 250GB)
- App-only authentication (no user login)

## Azure Setup

1. Register app in Azure AD
2. Add Application permissions: `Files.ReadWrite.All`, `User.Read.All`
3. Grant admin consent
