"""LavenderTown Streamlit App - CSV Upload and Data Quality Inspection."""

from typing import cast

import pandas as pd
import streamlit as st

from lavendertown import Inspector
from lavendertown.ui.upload import render_file_upload

st.set_page_config(
    page_title="LavenderTown - Data Quality Inspector",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("👻 LavenderTown - Data Quality Inspector")
st.markdown("Upload a CSV file to detect and visualize data quality issues (ghosts).")

# File upload section with dropzone and animations
st.header("📤 Upload CSV File")

uploaded_file, df, encoding_used = render_file_upload(
    st,
    accepted_types=[".csv"],
    help_text="Upload a CSV file to analyze for data quality issues",
    show_file_info=True,
)

if uploaded_file is not None:
    if df is None:
        # File was uploaded but couldn't be read (error already shown by render_file_upload)
        st.stop()

    # Type cast: df is guaranteed to be a pandas DataFrame at this point
    df = cast(pd.DataFrame, df)

    try:
        # Show encoding success message
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
