# File Upload Component

Enhanced file upload UI component with drag-and-drop support, animated progress indicators, and automatic encoding detection.

::: lavendertown.ui.upload.render_file_upload

## Overview

The `render_file_upload()` function provides a polished file upload experience for Streamlit applications. It includes:

- **Drag-and-drop interface**: Enhanced styling for intuitive file uploads
- **Animated progress indicators**: Multi-stage progress animations (minimum ~750ms) for visual feedback
- **Automatic encoding detection**: Tries multiple encodings (UTF-8, Latin-1, ISO-8859-1, CP1252) automatically
- **File validation**: Validates file format and provides clear error messages
- **File size display**: Shows file information and warnings for large files

## Basic Usage

```python
import streamlit as st
from lavendertown.ui.upload import render_file_upload

# Basic usage with defaults
uploaded_file, df, encoding_used = render_file_upload(st)

if uploaded_file is not None:
    if df is not None:
        st.write(f"File loaded successfully with {encoding_used} encoding")
        st.dataframe(df)
    else:
        st.error("Could not read the uploaded file")
```

## Customization

### Custom Accepted File Types

```python
uploaded_file, df, encoding_used = render_file_upload(
    st,
    accepted_types=[".csv", ".txt", ".tsv"]
)
```

### Custom Help Text

```python
uploaded_file, df, encoding_used = render_file_upload(
    st,
    help_text="Upload your data file here. Supported formats: CSV, TSV"
)
```

### Hide File Info Display

```python
uploaded_file, df, encoding_used = render_file_upload(
    st,
    show_file_info=False
)
```

## Return Values

The function returns a tuple of three values:

1. **`uploaded_file`**: The uploaded file object (or `None` if no file uploaded)
2. **`dataframe`**: Pandas DataFrame if file was successfully read (or `None` if read failed)
3. **`encoding_used`**: The encoding that successfully decoded the file (or `None` if read failed)

## Encoding Detection

The component automatically tries multiple encodings in order:

1. UTF-8 (most common)
2. Latin-1 (ISO-8859-1)
3. ISO-8859-1
4. CP1252 (Windows-1252)

The first encoding that successfully decodes the file is used. If all encodings fail, the function returns `None` for the dataframe and shows an error message.

## Progress Animation

The component includes a multi-stage progress animation:

1. **Upload Stage** (0-20%): "Reading file..."
2. **Validation Stage** (20-40%): "Validating format..."
3. **Processing Stage** (40-60%): "Processing data..."
4. **Encoding Detection** (60-80%): "Preparing analysis..."
5. **Ready Stage** (80-100%): "Ready!"

Each stage has a minimum delay to ensure users see feedback even for very fast operations.

## File Size Warnings

For files larger than 10MB, the component automatically displays a warning suggesting data sampling for faster analysis.

## Error Handling

The component handles various error cases gracefully:

- **Empty files**: Shows clear error message
- **Invalid CSV format**: Displays parsing error
- **Encoding failures**: Tries multiple encodings before failing
- **File read errors**: Returns file object but `None` for dataframe

## Example: Complete Upload Workflow

```python
import streamlit as st
from lavendertown import Inspector
from lavendertown.ui.upload import render_file_upload

st.title("Data Quality Inspector")

# Upload file with enhanced UI
uploaded_file, df, encoding_used = render_file_upload(
    st,
    accepted_types=[".csv"],
    help_text="Upload a CSV file to analyze for data quality issues",
    show_file_info=True
)

if uploaded_file is not None:
    if df is None:
        st.error("Could not read the CSV file. Please check the file format.")
        st.stop()
    
    # Show success message
    st.success(f"✅ File loaded successfully (encoding: {encoding_used})")
    
    # Display dataset preview
    st.header("Dataset Preview")
    st.dataframe(df.head(10))
    
    # Run inspection
    inspector = Inspector(df)
    inspector.render()
else:
    st.info("👆 Please upload a CSV file to get started.")
```

## Integration with Inspector

The upload component is designed to work seamlessly with LavenderTown's Inspector:

```python
from lavendertown import Inspector
from lavendertown.ui.upload import render_file_upload

uploaded_file, df, encoding_used = render_file_upload(st)

if df is not None:
    inspector = Inspector(df)
    inspector.render()  # Full data quality analysis
```

## Styling

The component includes enhanced CSS styling for a modern dropzone appearance:

- Dashed border with hover effects
- Smooth transitions
- Visual feedback on file selection
- Consistent with Streamlit's design system

## Performance Considerations

- **Small files (<1MB)**: Near-instantaneous processing
- **Medium files (1-10MB)**: Fast processing with progress feedback
- **Large files (>10MB)**: Shows warning and suggests sampling

For very large files, consider implementing data sampling before analysis.

## See Also

- [Basic Usage Guide](../user-guide/basic-usage.md) for general usage patterns
- [Examples](../guides/examples.md) for complete examples
- [Inspector API](inspector.md) for data quality analysis

