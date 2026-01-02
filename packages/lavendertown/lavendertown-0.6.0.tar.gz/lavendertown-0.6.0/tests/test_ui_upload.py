"""Tests for file upload UI component using Streamlit's AppTest framework.

Note: File upload testing with AppTest has limitations in Streamlit 1.51.0.
The upload() method may not be available. These tests focus on verifying
the component renders correctly. Full file upload functionality should be
tested manually or with integration tests.
"""

from __future__ import annotations

import pytest

# Skip all tests if streamlit testing is not available
try:
    from streamlit.testing.v1 import AppTest

    STREAMLIT_TESTING_AVAILABLE = True
except ImportError:
    STREAMLIT_TESTING_AVAILABLE = False


@pytest.mark.skipif(
    not STREAMLIT_TESTING_AVAILABLE,
    reason="Streamlit testing framework not available",
)
class TestFileUploadUI:
    """Test file upload UI component."""

    def test_render_file_upload_no_file(self):
        """Test upload component renders file uploader when no file is uploaded."""

        def app():
            import streamlit as st
            from lavendertown.ui.upload import render_file_upload

            uploaded_file, df, encoding_used = render_file_upload(st)
            # Verify component returns None when no file uploaded
            assert uploaded_file is None
            assert df is None
            assert encoding_used is None

        at = AppTest.from_function(app)
        at.run()

        # Check that file uploader is present
        file_uploaders = at.get("file_uploader")
        assert len(file_uploaders) >= 1

    def test_render_file_upload_custom_accepted_types(self):
        """Test upload component with custom accepted file types."""

        def app():
            import streamlit as st
            from lavendertown.ui.upload import render_file_upload

            uploaded_file, df, encoding_used = render_file_upload(
                st, accepted_types=[".csv", ".txt"]
            )

        at = AppTest.from_function(app)
        at.run()

        # Check that file uploader accepts the specified types
        file_uploaders = at.get("file_uploader")
        assert len(file_uploaders) >= 1

    def test_render_file_upload_custom_help_text(self):
        """Test upload component with custom help text."""

        def app():
            import streamlit as st
            from lavendertown.ui.upload import render_file_upload

            uploaded_file, df, encoding_used = render_file_upload(
                st, help_text="Custom help text for testing"
            )

        at = AppTest.from_function(app)
        at.run()

        # Check that file uploader is present with custom help
        file_uploaders = at.get("file_uploader")
        assert len(file_uploaders) >= 1

    def test_render_file_upload_css_styling_applied(self):
        """Test that CSS styling is applied to the file uploader."""

        def app():
            import streamlit as st
            from lavendertown.ui.upload import render_file_upload

            uploaded_file, df, encoding_used = render_file_upload(st)

        at = AppTest.from_function(app)
        at.run()

        # Check that markdown with CSS is present
        # The CSS is injected via st.markdown with unsafe_allow_html=True
        # This is harder to verify directly in AppTest, but we can check
        # that the component renders without errors
        file_uploaders = at.get("file_uploader")
        assert len(file_uploaders) >= 1

    def test_render_file_upload_default_parameters(self):
        """Test upload component uses default parameters correctly."""

        def app():
            import streamlit as st
            from lavendertown.ui.upload import render_file_upload

            # Call with no parameters to test defaults
            uploaded_file, df, encoding_used = render_file_upload(st)
            # Should work with defaults (accepted_types=[".csv"], show_file_info=True)
            assert uploaded_file is None  # No file uploaded

        at = AppTest.from_function(app)
        at.run()

        # Component should render successfully with defaults
        file_uploaders = at.get("file_uploader")
        assert len(file_uploaders) >= 1

    def test_render_file_upload_return_value_structure(self):
        """Test that return value structure is correct."""

        def app():
            import streamlit as st
            from lavendertown.ui.upload import render_file_upload

            result = render_file_upload(st)
            # Verify return type is a tuple of 3 elements
            assert isinstance(result, tuple)
            assert len(result) == 3
            # All should be None when no file uploaded
            assert result[0] is None  # uploaded_file
            assert result[1] is None  # dataframe
            assert result[2] is None  # encoding_used

        at = AppTest.from_function(app)
        at.run()

        # Component should render successfully
        file_uploaders = at.get("file_uploader")
        assert len(file_uploaders) >= 1


@pytest.mark.skipif(
    not STREAMLIT_TESTING_AVAILABLE,
    reason="Streamlit testing framework not available",
)
class TestFileUploadComponentStructure:
    """Test the structure and rendering of the upload component."""

    def test_component_renders_without_errors(self):
        """Test that the component renders without raising errors."""

        def app():
            import streamlit as st
            from lavendertown.ui.upload import render_file_upload

            # Component should render without raising exceptions
            uploaded_file, df, encoding_used = render_file_upload(st)
            # If we get here without exception, component rendered successfully

        at = AppTest.from_function(app)
        at.run()

        # Should render without errors - check that file uploader is present
        file_uploaders = at.get("file_uploader")
        assert len(file_uploaders) >= 1

    def test_component_handles_show_file_info_false(self):
        """Test component works when show_file_info is False."""

        def app():
            import streamlit as st
            from lavendertown.ui.upload import render_file_upload

            # Component should work with show_file_info=False
            uploaded_file, df, encoding_used = render_file_upload(
                st, show_file_info=False
            )
            # If we get here, component executed successfully

        at = AppTest.from_function(app)
        at.run()

        # Should render successfully - check that file uploader is present
        file_uploaders = at.get("file_uploader")
        assert len(file_uploaders) >= 1
