"""File upload UI component with dropzone and animations."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore[assignment]


def render_file_upload(
    st: object,
    accepted_types: list[str] | None = None,
    help_text: str | None = None,
    show_file_info: bool = True,
) -> tuple[object | None, object | None, str | None]:
    """Render file upload UI with dropzone and animations.

    Provides a polished file upload experience with:
    - Drag-and-drop dropzone interface
    - Animated progress indicators (minimum ~750ms)
    - Automatic encoding detection
    - File validation and error handling

    Args:
        st: Streamlit module object
        accepted_types: List of accepted file extensions (e.g., [".csv"])
            Defaults to [".csv"]
        help_text: Optional help text to display
        show_file_info: Whether to display file info after upload (default: True)

    Returns:
        Tuple of (uploaded_file, dataframe, encoding_used)
        - uploaded_file: The uploaded file object or None
        - dataframe: Pandas DataFrame if file was successfully read, None otherwise
        - encoding_used: The encoding that worked, or None if file read failed
    """
    if accepted_types is None:
        accepted_types = [".csv"]

    if help_text is None:
        help_text = "Upload a CSV file to analyze for data quality issues"

    # Convert accepted_types to format expected by file_uploader (e.g., ".csv" -> "csv")
    accept_list = [ext.lstrip(".") for ext in accepted_types]

    # Add custom CSS for enhanced dropzone appearance
    # Streamlit's native file_uploader supports drag-and-drop in recent versions
    st.markdown(
        """
    <style>
    /* Enhanced styling for file uploader to look like a dropzone */
    .uploadedFile {
        border: 2px dashed #9e9e9e !important;
        border-radius: 10px !important;
        padding: 20px !important;
        text-align: center !important;
        background: #f5f5f5 !important;
        transition: all 0.3s ease !important;
    }
    .uploadedFile:hover {
        border-color: #6366f1 !important;
        background: #f0f0ff !important;
    }
    /* Style the file uploader container */
    div[data-testid="stFileUploader"] {
        border: 2px dashed #9e9e9e;
        border-radius: 10px;
        padding: 20px;
        background: #fafafa;
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #6366f1;
        background: #f0f0ff;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Use Streamlit's native file_uploader with enhanced styling
    # It supports drag-and-drop in recent versions
    uploaded_file = st.file_uploader(
        "📤 Drag and drop a CSV file here, or click to browse",
        type=accept_list,
        help=help_text,
    )

    if uploaded_file is None:
        return None, None, None

    # Create upload animation container
    upload_container = st.container()

    with upload_container:
        # Show upload progress animation
        upload_status = st.status("📤 Uploading file...", expanded=True)

        with upload_status:
            # Simulate upload progress (even if instant)
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Calculate file size
            file_size = len(uploaded_file.getvalue())
            file_size_mb = file_size / (1024 * 1024)

            # Multi-stage progress animation with minimum duration
            stages = [
                ("Reading file...", 0.2),
                ("Validating format...", 0.4),
                ("Processing data...", 0.6),
                ("Preparing analysis...", 0.8),
                ("Ready!", 1.0),
            ]

            for step_text, progress in stages:
                status_text.text(step_text)
                progress_bar.progress(progress)
                # Minimum delay to show animation (150ms per step = ~750ms total)
                time.sleep(0.15)

            status_text.text(
                f"✅ File uploaded: {uploaded_file.name} ({file_size_mb:.2f} MB)"
            )

        # Close status after animation
        upload_status.update(state="complete", expanded=False)

    # Display file info if requested
    if show_file_info:
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📄 **File:** `{uploaded_file.name}`")
        with col2:
            st.info(f"📊 **Size:** {file_size:,} bytes ({file_size_mb:.2f} MB)")

        # File size warning for very large files
        if file_size > 10_000_000:  # 10 MB
            st.warning(
                "⚠️ Large file detected. Processing may take longer. "
                "Consider sampling for faster analysis."
            )

    # Read CSV with encoding detection and animation
    with st.status("📖 Reading CSV file...", expanded=True) as read_status:
        with read_status:
            read_progress = st.progress(0)
            read_status_text = st.empty()

            read_status_text.text("Detecting encoding...")
            read_progress.progress(0.3)
            time.sleep(0.1)  # Small delay for visual feedback

            # Attempt multiple encodings
            encodings = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
            df = None
            encoding_used = None

            read_status_text.text("Trying encodings...")
            read_progress.progress(0.5)

            for i, encoding in enumerate(encodings):
                try:
                    uploaded_file.seek(0)  # Reset file pointer
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    encoding_used = encoding
                    read_progress.progress(0.7 + (i * 0.1))
                    break
                except (UnicodeDecodeError, pd.errors.ParserError):  # type: ignore[union-attr]
                    continue

            if df is None:
                read_status_text.text("❌ Could not read file")
                read_progress.progress(1.0)
                st.error(
                    "❌ Could not read CSV file. Please check the file format and encoding."
                )
                # Return the uploaded file but no dataframe
                return uploaded_file, None, None

            read_status_text.text(f"✅ Successfully read with {encoding_used} encoding")
            read_progress.progress(1.0)
            time.sleep(0.2)  # Brief pause to show success

    return uploaded_file, df, encoding_used
