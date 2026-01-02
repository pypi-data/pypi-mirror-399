# LavenderTown Deployment Guide

This guide covers deploying LavenderTown applications to Streamlit Cloud.

## Streamlit Cloud Deployment

Streamlit Cloud is the easiest way to deploy LavenderTown applications. The platform automatically detects Streamlit apps and deploys them with minimal configuration.

### Prerequisites

1. A GitHub account
2. Your LavenderTown app code pushed to a GitHub repository
3. A Streamlit Cloud account (free tier available at [streamlit.io/cloud](https://streamlit.io/cloud))

### Deployment Steps

#### 1. Prepare Your Application

Ensure your Streamlit app is in a file named `app.py` or `streamlit_app.py` at the root of your repository, or use the example app at `examples/app.py`.

For example, a minimal deployment-ready app:

```python
# app.py
import pandas as pd
import streamlit as st
from lavendertown import Inspector

st.set_page_config(page_title="LavenderTown", layout="wide")

st.title("Data Quality Inspector")
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    inspector = Inspector(df)
    inspector.render()
```

#### 2. Create Requirements File (Optional)

Streamlit Cloud can automatically detect dependencies from `pyproject.toml` if your project uses it. However, you can also create a `requirements.txt` file in your repository root:

```txt
lavendertown>=0.2.0
pandas>=1.5.0
streamlit>=1.28.0
altair>=5.0.0
```

**Note:** For optional features:
- Add `polars>=0.19.0` for Polars support
- Add `pandera>=0.18.0` for Pandera export
- Add `great-expectations>=0.18.0` for Great Expectations export

#### 3. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub account if not already connected
4. Select your repository
5. Choose the branch (usually `main` or `master`)
6. Set the main file path:
   - If your app is at the root: `app.py` or `streamlit_app.py`
   - If using the example: `examples/app.py`
7. Click "Deploy"

#### 4. Configure App Settings (Optional)

After deployment, you can configure:

- **App title and icon**: Edit your `app.py` file
- **Theme**: Create `.streamlit/config.toml` in your repository:

```toml
[theme]
primaryColor = "#9D4EDD"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F0F0"
textColor = "#262730"
font = "sans serif"
```

- **Secrets**: For API keys or sensitive configuration, use Streamlit Cloud's secrets management (Settings → Secrets)

### Using the Example App

The repository includes a ready-to-deploy example at `examples/app.py`. To deploy it:

1. Set the main file path to `examples/app.py` in Streamlit Cloud
2. Ensure `pyproject.toml` is in the repository root (for dependency detection)
3. Deploy!

### Environment Variables

If your app needs environment variables:

1. Go to your app settings on Streamlit Cloud
2. Navigate to "Secrets"
3. Add variables in TOML format:

```toml
[database]
url = "postgresql://..."
password = "..."

[api]
key = "your-api-key"
```

Access in your app:

```python
import streamlit as st

db_url = st.secrets["database"]["url"]
```

### Troubleshooting

#### Common Issues

1. **Import Errors**: Ensure all dependencies are listed in `requirements.txt` or `pyproject.toml`
2. **File Not Found**: Check that your main file path is correct in Streamlit Cloud settings
3. **Memory Issues**: For large datasets, consider:
   - Using Polars backend (`pip install lavendertown[polars]`)
   - Implementing data sampling
   - Using `st.cache_data` for expensive operations

#### Logs and Debugging

- View logs in the Streamlit Cloud dashboard
- Use `st.write()` or `st.error()` for debugging output
- Check "Always rerun" in settings for development

### Performance Considerations

- **Small datasets (<10k rows)**: No special configuration needed
- **Medium datasets (10k-100k rows)**: Consider using Polars backend
- **Large datasets (>100k rows)**: Implement data sampling or use batch processing

### Security Best Practices

- Never commit secrets or API keys to your repository
- Use Streamlit Cloud's secrets management for sensitive data
- Validate and sanitize user inputs (file uploads, etc.)
- Consider rate limiting for public apps

### Updating Your Deployment

Streamlit Cloud automatically redeploys when you push changes to your connected branch. To manually trigger a redeploy:

1. Go to your app settings
2. Click "Reboot app" or "Always rerun"

### Example Repository Structure

```
your-repo/
├── app.py                    # Main Streamlit app (or examples/app.py)
├── pyproject.toml            # Dependencies (preferred)
├── requirements.txt          # Alternative dependencies file
├── .streamlit/
│   └── config.toml          # Streamlit configuration (optional)
└── README.md
```

### Additional Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Deployment Guide](https://docs.streamlit.io/deploy)
- [LavenderTown Examples](../examples/README.md)

