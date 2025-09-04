# Docker Deployment Guide

## 🐳 GitHub Container Registry Deployment

This project uses GitHub Container Registry (ghcr.io) for private container deployment with baked-in API keys.

## 🔐 Security Approach

- **Google API Key**: Baked directly into `.env` file during build
- **Private Registry**: Images stored in GitHub Container Registry (ghcr.io)
- **Access Control**: Only authorized users can pull images
- **No Runtime Configuration**: Ready to run immediately after pull

## 🚀 Deployment Flow

### **Automatic Deployment (GitHub Actions)**

When you push to `main` branch or create a release:

1. **GitHub Actions** builds Docker image with real `GOOGLE_API_KEY`
2. **Image** is pushed to `ghcr.io/yourusername/mcp_rag`
3. **Tagged** with version number and `latest`

### **Local Usage**

Pull and run the pre-built image:

```bash
# Authenticate with GitHub Container Registry (one-time setup)
echo $GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin

# Pull the latest image
docker pull ghcr.io/yourusername/mcp_rag:latest

# Run the container (API key already configured)
docker run -p 8080:8080 ghcr.io/yourusername/mcp_rag:latest
```

## 🏗️ Build Process

The Dockerfile now bakes the API key directly during build:

```dockerfile
# Build argument receives the secret
ARG GOOGLE_API_KEY

# Generate .env file with real API key
RUN cp /app/.env_template /app/.env \
    && sed -i "s/your_google_api_key_here/${GOOGLE_API_KEY}/g" /app/.env \
    && chmod 600 /app/.env
```

## 📋 Available Images

- `ghcr.io/yourusername/mcp_rag:latest` - Latest stable version
- `ghcr.io/yourusername/mcp_rag:v1.x.x` - Specific version tags

## 🔧 Local Development

For local development without pulling from registry:

```bash
# Build locally (you need to provide GOOGLE_API_KEY)
docker build --build-arg GOOGLE_API_KEY=your_key_here -t mcp-rag-dev .

# Run locally built image
docker run -p 8080:8080 mcp-rag-dev
```

## 🛡️ Security Benefits

- ✅ **Private Registry**: Only authorized users can access images
- ✅ **No Runtime Secrets**: No need to manage secrets at runtime  
- ✅ **Immutable**: API key baked into image, can't be accidentally overridden
- ✅ **Version Control**: Each image version has consistent configuration
- ✅ **Audit Trail**: GitHub tracks who builds and accesses images

## 🚨 Important Notes

- **Repository must be private** for security
- **GITHUB_TOKEN permissions** are automatically configured for packages
- **Images expire** according to your GitHub package retention policy
- **API Key rotation** requires rebuilding and redeploying images