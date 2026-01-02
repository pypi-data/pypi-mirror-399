"""Enhanced UI components using streamlit-extras."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

try:
    from streamlit_extras import (
        add_vertical_space,
        badge,
        card,
        data_frame_explorer,
        metric_card,
        toggle_switch,
    )

    STREAMLIT_EXTRAS_AVAILABLE = True
except ImportError:
    STREAMLIT_EXTRAS_AVAILABLE = False

    # Create dummy functions for fallback
    def metric_card(*args, **kwargs):
        pass

    def card(*args, **kwargs):
        pass

    def badge(*args, **kwargs):
        pass

    def toggle_switch(*args, **kwargs):
        pass

    def data_frame_explorer(*args, **kwargs):
        pass

    def add_vertical_space(*args, **kwargs):
        pass


def render_metric_card(
    st: object,
    title: str,
    value: str | int | float,
    delta: str | int | float | None = None,
    help_text: str | None = None,
) -> None:
    """Render an enhanced metric card using streamlit-extras.

    Falls back to st.metric if streamlit-extras is not available.

    Args:
        st: Streamlit module
        title: Metric title
        value: Metric value
        delta: Optional delta value
        help_text: Optional help text
    """
    if STREAMLIT_EXTRAS_AVAILABLE:
        try:
            metric_card(
                title=title,
                value=str(value),
                delta=str(delta) if delta is not None else None,
                help=help_text,
            )
            return
        except Exception:
            # Fallback to standard metric if extras fails
            pass

    # Fallback to standard Streamlit metric
    st.metric(label=title, value=value, delta=delta, help=help_text)  # type: ignore[attr-defined]


def render_card(
    st: object,
    title: str | None = None,
    text: str | None = None,
    **kwargs: object,
) -> object:
    """Render a card component using streamlit-extras.

    Falls back to st.container if streamlit-extras is not available.

    Args:
        st: Streamlit module
        title: Optional card title
        text: Optional card text
        **kwargs: Additional card properties

    Returns:
        Card context manager or container
    """
    if STREAMLIT_EXTRAS_AVAILABLE:
        try:
            return card(title=title, text=text, **kwargs)
        except Exception:
            # Fallback to container
            pass

    # Fallback to standard Streamlit container
    return st.container()  # type: ignore[attr-defined]


def render_badge(
    st: object,
    label: str,
    value: str,
    color: str | None = None,
) -> None:
    """Render a badge using streamlit-extras.

    Falls back to st.caption if streamlit-extras is not available.

    Args:
        st: Streamlit module
        label: Badge label
        value: Badge value
        color: Optional badge color
    """
    if STREAMLIT_EXTRAS_AVAILABLE:
        try:
            badge(type=label, text=value)
            return
        except Exception:
            # Fallback to caption
            pass

    # Fallback to standard Streamlit caption
    st.caption(f"{label}: {value}")  # type: ignore[attr-defined]


def render_toggle(
    st: object,
    label: str,
    default_value: bool = False,
    key: str | None = None,
) -> bool:
    """Render a toggle switch using streamlit-extras.

    Falls back to st.checkbox if streamlit-extras is not available.

    Args:
        st: Streamlit module
        label: Toggle label
        default_value: Default toggle state
        key: Optional unique key

    Returns:
        Toggle state (True/False)
    """
    if STREAMLIT_EXTRAS_AVAILABLE:
        try:
            return toggle_switch(label, default_value=default_value, key=key)  # type: ignore[call-arg]
        except Exception:
            # Fallback to checkbox
            pass

    # Fallback to standard Streamlit checkbox
    return st.checkbox(label, value=default_value, key=key)  # type: ignore[attr-defined]


def render_dataframe_explorer(
    st: object,
    df: object,
    **kwargs: object,
) -> None:
    """Render an enhanced dataframe explorer using streamlit-extras.

    Falls back to st.dataframe if streamlit-extras is not available.

    Args:
        st: Streamlit module
        df: DataFrame to display
        **kwargs: Additional arguments
    """
    if STREAMLIT_EXTRAS_AVAILABLE:
        try:
            data_frame_explorer(df, **kwargs)
            return
        except Exception:
            # Fallback to standard dataframe
            pass

    # Fallback to standard Streamlit dataframe
    st.dataframe(df, **kwargs)  # type: ignore[attr-defined]
