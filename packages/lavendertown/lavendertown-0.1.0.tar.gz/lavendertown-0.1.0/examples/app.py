"""LavenderTown Streamlit App - CSV Upload and Data Quality Inspection."""

import pandas as pd
import streamlit as st

from lavendertown import Inspector

st.set_page_config(
    page_title="LavenderTown - Data Quality Inspector",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("👻 LavenderTown - Data Quality Inspector")
st.markdown("Upload a CSV file to detect and visualize data quality issues (ghosts).")

# File upload section
st.header("📤 Upload CSV File")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    help="Upload a CSV file to analyze for data quality issues",
)

if uploaded_file is not None:
    # Display file info
    file_size = len(uploaded_file.getvalue())
    st.info(f"📄 File: `{uploaded_file.name}` ({file_size:,} bytes)")

    # File size warning for very large files
    if file_size > 10_000_000:  # 10 MB
        st.warning(
            "⚠️ Large file detected. Processing may take longer. "
            "Consider sampling for faster analysis."
        )

    try:
        # Try to read the CSV file
        with st.spinner("Reading CSV file..."):
            # Attempt multiple encodings
            encodings = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
            df = None
            encoding_used = None

            for encoding in encodings:
                try:
                    uploaded_file.seek(0)  # Reset file pointer
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    encoding_used = encoding
                    break
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue

            if df is None:
                st.error(
                    "❌ Could not read CSV file. Please check the file format and encoding."
                )
                st.stop()

            st.success(f"✅ File read successfully (encoding: {encoding_used})")

        # Display basic info about the dataset
        st.header("📊 Dataset Preview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", f"{len(df):,}")
        with col2:
            st.metric("Columns", len(df.columns))
        with col3:
            st.metric(
                "Memory Usage",
                f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB",
            )

        # Show first few rows
        with st.expander("Preview first 10 rows"):
            st.dataframe(df.head(10), use_container_width=True)

        # Run inspection
        st.header("🔍 Data Quality Inspection")
        st.markdown("Analyzing dataset for data quality issues...")

        try:
            inspector = Inspector(df)
            inspector.render()
        except Exception as e:
            st.error(f"❌ Error during inspection: {str(e)}")
            st.exception(e)

    except pd.errors.EmptyDataError:
        st.error("❌ The CSV file is empty.")
    except pd.errors.ParserError as e:
        st.error(f"❌ Error parsing CSV file: {str(e)}")
        st.info("Please ensure the file is a valid CSV format.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        st.exception(e)

else:
    # Show instructions when no file is uploaded
    st.info("👆 Please upload a CSV file to get started.")

    st.markdown("### 📝 Instructions")
    st.markdown(
        """
        1. Click "Browse files" or drag and drop a CSV file
        2. Wait for the file to be processed
        3. Explore the data quality insights in the sidebar and main panel
        
        **Supported formats:**
        - CSV files (`.csv`)
        - UTF-8, Latin-1, ISO-8859-1, or CP1252 encoding
        
        **Tips:**
        - Files up to 200MB are supported
        - For very large files, consider sampling the data first
        - The analysis includes null detection, type inconsistencies, and outlier detection
        """
    )
