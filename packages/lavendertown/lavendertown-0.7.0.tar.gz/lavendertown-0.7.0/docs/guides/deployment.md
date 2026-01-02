# Deployment Guide

This guide covers deploying LavenderTown applications to various platforms, including Streamlit Cloud, Docker, and traditional hosting environments.

## Streamlit Cloud Deployment

Streamlit Cloud is the easiest way to deploy LavenderTown applications with minimal configuration.

### Prerequisites

1. A GitHub account
2. Your LavenderTown app code pushed to a GitHub repository
3. A Streamlit Cloud account (free tier available at [streamlit.io/cloud](https://streamlit.io/cloud))

### Quick Deployment

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account if not already connected
4. Select your repository and branch
5. Set the main file path (e.g., `app.py` or `examples/app.py`)
6. Click "Deploy"

### Minimal App Example

Create a deployment-ready app:

```python
# app.py
import pandas as pd
import streamlit as st
from lavendertown import Inspector

st.set_page_config(
    page_title="LavenderTown - Data Quality Inspector",
    page_icon="👻",
    layout="wide"
)

st.title("👻 Data Quality Inspector")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    inspector = Inspector(df)
    inspector.render()
```

### Dependencies

Streamlit Cloud can automatically detect dependencies from `pyproject.toml`. Alternatively, create `requirements.txt`:

```txt
lavendertown>=0.7.0
pandas>=1.5.0
streamlit>=1.28.0
altair>=4.2.1
```

For optional features:

```txt
# Polars support
polars>=0.19.0

# ML features
scikit-learn>=1.0.0

# Time-series features
statsmodels>=0.14.0

# Ecosystem integrations
pandera>=0.18.0
great-expectations>=0.18.0
```

### Configuration

#### Theme Customization

Create `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#9D4EDD"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F0F0"
textColor = "#262730"
font = "sans serif"
```

#### Environment Variables and Secrets

For sensitive data, use Streamlit Cloud's secrets management (Settings → Secrets):

```toml
[database]
url = "postgresql://user:pass@host/db"

[api]
key = "your-api-key"
```

Access in your app:

```python
import streamlit as st

db_url = st.secrets["database"]["url"]
api_key = st.secrets["api"]["key"]
```

### Performance Optimization for Cloud

For large datasets on Streamlit Cloud:

```python
import streamlit as st
from lavendertown import Inspector
import pandas as pd

@st.cache_data
def load_and_analyze(file):
    """Cache analysis results."""
    df = pd.read_csv(file)
    inspector = Inspector(df)
    findings = inspector.detect()
    return df, findings

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df, findings = load_and_analyze(uploaded_file)
    
    # Display results
    st.write(f"Found {len(findings)} data quality issues")
    inspector = Inspector(df)
    inspector.render()
```

## Docker Deployment

Deploy LavenderTown applications using Docker for more control and portability.

### Dockerfile

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .
COPY .streamlit .streamlit

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose

For easier deployment with `docker-compose.yml`:

```yaml
version: '3.8'

services:
  lavendertown:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
    environment:
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    restart: unless-stopped
```

Build and run:

```bash
docker-compose up -d
```

### Multi-stage Dockerfile (Production)

For optimized production builds:

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages
COPY --from=builder /root/.local /root/.local

# Copy application
COPY app.py .
COPY .streamlit .streamlit

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Traditional Server Deployment

Deploy LavenderTown on your own server or VPS.

### Using systemd

Create a systemd service `/etc/systemd/system/lavendertown.service`:

```ini
[Unit]
Description=LavenderTown Data Quality Inspector
After=network.target

[Service]
Type=simple
User=lavendertown
WorkingDirectory=/opt/lavendertown
Environment="PATH=/opt/lavendertown/venv/bin"
ExecStart=/opt/lavendertown/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable lavendertown
sudo systemctl start lavendertown
```

### Using Nginx Reverse Proxy

Configure Nginx as a reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### Using Gunicorn (Advanced)

For production deployments, use Gunicorn with multiple workers:

```python
# wsgi.py
from streamlit.web.server import Server
from streamlit.runtime.scriptrunner.magic_funcs import draw_all
import sys

def application(environ, start_response):
    # Set up Streamlit
    sys.argv = ["streamlit", "run", "app.py"]
    
    # Create server
    server = Server("app.py", False)
    
    # Handle request
    # (Implementation details depend on your setup)
    pass
```

## Cloud Platform Deployments

### AWS (Elastic Beanstalk or EC2)

1. Create `requirements.txt` with dependencies
2. Deploy using Elastic Beanstalk or configure EC2 instance
3. Use Application Load Balancer for HTTPS
4. Configure security groups to allow port 8501

### Google Cloud Platform (App Engine or Cloud Run)

For Cloud Run, create `app.yaml`:

```yaml
runtime: python311

entrypoint: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0

env_variables:
  STREAMLIT_SERVER_PORT: 8080
```

Deploy:

```bash
gcloud run deploy lavendertown --source .
```

### Azure (App Service)

1. Create `requirements.txt`
2. Deploy via Azure CLI or portal
3. Configure startup command: `streamlit run app.py --server.port=8000 --server.address=0.0.0.0`

## Environment-Specific Configuration

### Development

```python
# config.py
import os

ENV = os.getenv("ENV", "development")

if ENV == "development":
    DEBUG = True
    LOG_LEVEL = "DEBUG"
elif ENV == "production":
    DEBUG = False
    LOG_LEVEL = "WARNING"
```

### Production Considerations

1. **Security**:
   - Use HTTPS (configure reverse proxy)
   - Set `STREAMLIT_SERVER_HEADLESS=true`
   - Configure CORS if needed
   - Implement authentication (Streamlit Authenticator or similar)

2. **Performance**:
   - Enable caching with `@st.cache_data`
   - Use Polars for large datasets
   - Implement data sampling for very large files
   - Configure appropriate timeout values

3. **Monitoring**:
   - Set up logging
   - Monitor resource usage
   - Track error rates
   - Set up alerts for failures

### Example Production App

```python
import streamlit as st
import pandas as pd
from lavendertown import Inspector
import os

# Configuration
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ENABLE_CACHING = os.getenv("ENABLE_CACHING", "true").lower() == "true"

st.set_page_config(
    page_title="Data Quality Inspector",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(show_spinner="Analyzing data quality...")
def analyze_data(df: pd.DataFrame):
    """Cache analysis results."""
    inspector = Inspector(df)
    findings = inspector.detect()
    return findings

st.title("Data Quality Inspector")

uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=["csv"],
    help=f"Maximum file size: {MAX_FILE_SIZE / 1024 / 1024}MB"
)

if uploaded_file is not None:
    # Check file size
    file_size = len(uploaded_file.getvalue())
    if file_size > MAX_FILE_SIZE:
        st.error(f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB")
    else:
        try:
            df = pd.read_csv(uploaded_file)
            
            if ENABLE_CACHING:
                findings = analyze_data(df)
            else:
                inspector = Inspector(df)
                findings = inspector.detect()
            
            inspector = Inspector(df)
            inspector.render()
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.exception(e)
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are in `requirements.txt`
2. **Port Conflicts**: Change port with `--server.port=8502`
3. **Memory Issues**: Use Polars backend, implement data sampling
4. **Timeout Errors**: Increase timeout in reverse proxy configuration

### Logs and Debugging

View logs:

```bash
# Streamlit Cloud
# Check dashboard logs

# Docker
docker logs <container_id>

# systemd
journalctl -u lavendertown -f
```

### Health Checks

Implement health check endpoint:

```python
import streamlit as st

if st.query_params.get("health") == "check":
    st.write("OK")
    st.stop()
```

## Security Best Practices

1. **Never commit secrets**: Use environment variables or secrets management
2. **Validate inputs**: Sanitize file uploads
3. **Rate limiting**: Implement rate limiting for public apps
4. **Authentication**: Add authentication for sensitive data
5. **HTTPS**: Always use HTTPS in production
6. **CORS**: Configure CORS appropriately
7. **File size limits**: Enforce reasonable file size limits

## Scaling Considerations

1. **Horizontal scaling**: Use load balancer with multiple instances
2. **Caching**: Implement Redis or similar for shared cache
3. **Database**: Store results in database for persistence
4. **Queue system**: Use message queue for batch processing
5. **CDN**: Use CDN for static assets

## Additional Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Deployment Guide](https://docs.streamlit.io/deploy)
- [Docker Documentation](https://docs.docker.com/)
- [Examples Guide](../guides/examples.md) for usage patterns
