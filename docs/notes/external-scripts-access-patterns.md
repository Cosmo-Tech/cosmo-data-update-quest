# External Scripts Access Patterns in Docker

## Table of Contents
- [Introduction](#introduction)
- [Access Pattern Analysis](#access-pattern-analysis)
  - [Git Integration](#git-integration)
  - [Cloud Storage Solutions](#cloud-storage-solutions)
  - [Package and Container Registries](#package-and-container-registries)
  - [API-Based Solutions](#api-based-solutions)
  - [Volume Mounting](#volume-mounting)
- [Technology Comparison](#technology-comparison)
- [Implementation Considerations](#implementation-considerations)
- [Security and Best Practices](#security-and-best-practices)
- [Recommendations](#recommendations)

## Introduction

When running applications in Docker containers, there's often a need to access external scripts that cannot be embedded directly in the image, particularly for customer-specific customizations. This document analyzes various patterns for accessing these external scripts, comparing their benefits, limitations, and implementation considerations.

### Key Requirements
- Secure access to external scripts
- Version control and change tracking
- Easy updates without rebuilding images
- Scalable across multiple environments
- Support for customer-specific customizations

## Access Pattern Analysis

### Git Integration

Git integration provides a robust solution for managing external scripts with full version control capabilities.

#### Implementation Example
```json
{
  "steps": [
    {
      "id": "git-clone",
      "command": "git",
      "arguments": [
        "clone",
        "--branch", "$GIT_BRANCH",
        "--depth", "1",
        "$REPO_URL",
        "customer-scripts"
      ],
      "useSystemEnvironment": true,
      "environment": {
        "GIT_BRANCH": {
          "description": "Git branch or tag",
          "defaultValue": "main"
        },
        "REPO_URL": {
          "description": "Repository URL"
        }
      }
    }
  ]
}
```

#### Authentication Methods
1. **SSH Keys**
   ```json
   {
     "steps": [
       {
         "id": "setup-ssh",
         "command": "mkdir -p /root/.ssh && echo \"$SSH_PRIVATE_KEY\" > /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa",
         "useSystemEnvironment": true
       }
     ]
   }
   ```

2. **HTTPS with Personal Access Token**
   ```json
   {
     "environment": {
       "GIT_TOKEN": {
         "description": "Git personal access token"
       }
     }
   }
   ```

#### Advantages
- Full version control capabilities
- Branch/tag support for different environments
- Commit history and audit trail
- Support for submodules
- Familiar workflow for developers

#### Limitations
- Requires Git installation in container
- Authentication management
- Network dependency
- Storage overhead from Git metadata

### Cloud Storage Solutions

Cloud storage solutions offer flexible, scalable options for storing and accessing external scripts.

#### Azure Blob Storage Implementation
```python
# download_from_azure.py
from azure.storage.blob import BlobServiceClient
import os

def download_script(connection_string, container_name, blob_name, destination):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    
    with open(destination, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
```

#### AWS S3 Implementation
```json
{
  "steps": [
    {
      "id": "download-from-s3",
      "command": "aws",
      "arguments": [
        "s3",
        "cp",
        "s3://$BUCKET_NAME/$SCRIPT_PATH",
        "./customer_script.py"
      ],
      "useSystemEnvironment": true
    }
  ]
}
```

#### Features Comparison Matrix

| Feature | Azure Blob | AWS S3 | GCS |
|---------|------------|--------|-----|
| Versioning | ✓ | ✓ | ✓ |
| Access Control | ✓ | ✓ | ✓ |
| Event Triggers | ✓ | ✓ | ✓ |
| Geographic Replication | ✓ | ✓ | ✓ |
| Cost | Pay-as-you-go | Pay-as-you-go | Pay-as-you-go |
| Cross-Region Transfer | Supported | Supported | Supported |

### Package and Container Registries

Using package registries provides a standardized way to distribute and version scripts.

#### PyPI Package Example
```dockerfile
# In Dockerfile
FROM python:3.11-bookworm

# Add private package registry
COPY pip.conf /root/.pip/pip.conf

# Install customer scripts package
RUN pip install customer-scripts==1.0.0
```

#### Container Registry Approach
```json
{
  "steps": [
    {
      "id": "pull-script-image",
      "command": "docker",
      "arguments": [
        "pull",
        "customer/scripts:latest"
      ]
    },
    {
      "id": "copy-scripts",
      "command": "docker",
      "arguments": [
        "cp",
        "customer/scripts:/scripts",
        "./customer-scripts/"
      ],
      "precedents": ["pull-script-image"]
    }
  ]
}
```

### API-Based Solutions

API-based solutions provide dynamic script access with strong access control.

#### HTTP/HTTPS Endpoints
```json
{
  "steps": [
    {
      "id": "download-from-api",
      "command": "curl",
      "arguments": [
        "-H", "Authorization: Bearer $API_TOKEN",
        "https://api.customer.com/scripts/transform.py",
        "-o", "customer_script.py"
      ],
      "useSystemEnvironment": true
    }
  ]
}
```

#### WebDAV Integration
```json
{
  "steps": [
    {
      "id": "download-from-webdav",
      "command": "curl",
      "arguments": [
        "--user", "$WEBDAV_USER:$WEBDAV_PASS",
        "https://webdav.example.com/scripts/customer_script.py",
        "-o", "customer_script.py"
      ],
      "useSystemEnvironment": true
    }
  ]
}
```

### Volume Mounting

Direct volume mounting provides simple access to external scripts.

```bash
docker run -v /path/to/customer/scripts:/home/customer-scripts your-image
```

#### Kubernetes ConfigMap Example
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: customer-scripts
data:
  transform.py: |
    def transform_data(input_data):
        # transformation logic here
        pass
```

## Technology Comparison

### Feature Matrix

| Feature | Git | Cloud Storage | Package Registry | API | Volume Mount |
|---------|-----|---------------|------------------|-----|--------------|
| Version Control | ✓✓✓ | ✓✓ | ✓✓✓ | ✓ | ✗ |
| Access Control | ✓✓ | ✓✓✓ | ✓✓ | ✓✓✓ | ✓ |
| Offline Access | ✓✓✓ | ✗ | ✓✓ | ✗ | ✓✓✓ |
| Update Speed | ✓✓ | ✓✓✓ | ✓ | ✓✓✓ | ✓✓✓ |
| Setup Complexity | ✓✓ | ✓✓ | ✓ | ✓✓ | ✓✓✓ |
| Cost | Free/Low | Pay-as-you-go | Low | Varies | Free |
| Enterprise Support | ✓✓✓ | ✓✓✓ | ✓✓ | ✓✓ | ✓ |

## Implementation Considerations

### Authentication and Security
1. **Git Integration**
    - SSH keys or personal access tokens
    - Read-only access
    - Deploy keys for specific repositories

2. **Cloud Storage**
    - Managed identities
    - SAS tokens with expiration
    - Role-based access control

3. **Package Registries**
    - Access tokens
    - Scoped permissions
    - Private registries

4. **API Solutions**
    - Bearer tokens
    - API keys
    - OAuth2 integration

### Performance Optimization
1. **Caching Strategies**
   ```json
   {
     "steps": [
       {
         "id": "check-cache",
         "command": "test",
         "arguments": ["-f", "cache/script.md5"]
       },
       {
         "id": "download-if-changed",
         "command": "curl",
         "arguments": [
           "-z", "cache/script.md5",
           "-o", "script.py",
           "$SCRIPT_URL"
         ],
         "condition": "check-cache"
       }
     ]
   }
   ```

2. **Parallel Downloads**
   ```json
   {
     "steps": [
       {
         "id": "download-scripts",
         "command": "parallel",
         "arguments": [
           "curl -o {1} {2}",
           ":::",
           "script1.py", "script2.py",
           ":::",
           "$URL1", "$URL2"
         ]
       }
     ]
   }
   ```

### Error Handling
```json
{
  "steps": [
    {
      "id": "download-script",
      "command": "curl",
      "arguments": ["$SCRIPT_URL"],
      "retries": 3,
      "backoff": "exponential",
      "onFailure": {
        "action": "fallback",
        "source": "cache/script.py"
      }
    }
  ]
}
```

## Security and Best Practices

### 1. Access Control
- Implement least privilege principle
- Use time-limited access tokens
- Implement IP restrictions where possible
- Regular credential rotation

### 2. Content Validation
```python
def validate_script(script_path):
    # Check file hash
    actual_hash = calculate_file_hash(script_path)
    if actual_hash != expected_hash:
        raise SecurityException("Script integrity check failed")
    
    # Scan for prohibited patterns
    with open(script_path) as f:
        content = f.read()
        if contains_prohibited_patterns(content):
            raise SecurityException("Script contains prohibited patterns")
```

### 3. Monitoring and Logging
```json
{
  "steps": [
    {
      "id": "script-download",
      "command": "curl",
      "arguments": ["$SCRIPT_URL"],
      "logging": {
        "level": "INFO",
        "fields": {
          "script_name": "$SCRIPT_NAME",
          "source": "$SCRIPT_URL",
          "timestamp": "${NOW}"
        }
      }
    }
  ]
}
```

## Recommendations

### Decision Framework

1. **For Development and Testing**
    - Use volume mounting for quick iterations
    - Git integration for version control
    - Local package registry for dependency management

2. **For Production Environments**
    - Cloud storage with proper access controls
    - Container registry for immutable artifacts
    - API-based solution for dynamic updates

3. **For Enterprise Deployments**
    - Combination of Git and package registry
    - Cloud storage for large-scale distribution
    - API gateway for access control

### Implementation Checklist

1. **Security**
    - [ ] Authentication mechanism defined
    - [ ] Access controls implemented
    - [ ] Content validation in place
    - [ ] Secure storage of credentials
    - [ ] Network security configured

2. **Operations**
    - [ ] Monitoring setup
    - [ ] Logging implemented
    - [ ] Error handling defined
    - [ ] Backup strategy in place
    - [ ] Update process documented

3. **Performance**
    - [ ] Caching strategy implemented
    - [ ] Network optimization configured
    - [ ] Resource limits set
    - [ ] Load testing completed
    - [ ] Performance metrics defined

4. **Maintenance**
    - [ ] Version control strategy
    - [ ] Update procedure documented
    - [ ] Rollback procedure defined
    - [ ] Monitoring alerts configured
    - [ ] Support process established
