"""Example: Custom UI layout with modular components.

This example demonstrates how to create custom UI layouts by:
1. Creating a custom component layout
2. Adding/removing components
3. Reordering components
4. Disabling components
"""

import streamlit as st
from lavendertown import Inspector
from lavendertown.ui.base import ComponentWrapper
from lavendertown.ui.layout import ComponentLayout, create_default_layout
from lavendertown.ui.charts import render_charts
from lavendertown.ui.export import render_export_section
from lavendertown.ui.overview import render_overview
from lavendertown.ui.table import render_table
import pandas as pd

# Create sample data
data = {
    "product_id": [1, 2, 3, 4, 5],
    "price": [10.99, 25.50, None, 45.00, -5.00],
    "quantity": [100, 50, 75, None, 200],
}
df = pd.DataFrame(data)

st.title("Custom UI Layout Example")

# Example 1: Use default layout (same as before)
st.header("Example 1: Default Layout")
with st.expander("Show code"):
    st.code("""
    inspector = Inspector(df)
    inspector.render()  # Uses default layout
    """)

if st.button("Run Example 1"):
    inspector = Inspector(df)
    inspector.render()

st.divider()

# Example 2: Custom layout with only overview and export
st.header("Example 2: Minimal Layout (Overview + Export Only)")
with st.expander("Show code"):
    st.code("""
    from lavendertown.ui.layout import ComponentLayout
    from lavendertown.ui.base import ComponentWrapper
    from lavendertown.ui.overview import render_overview
    from lavendertown.ui.export import render_export_section
    
    # Create minimal layout
    minimal_layout = ComponentLayout(show_dividers=True)
    minimal_layout.add_component(
        ComponentWrapper(
            name="overview",
            render_func=render_overview,
            order=10,
            requires_findings=True,
        )
    )
    minimal_layout.add_component(
        ComponentWrapper(
            name="export",
            render_func=render_export_section,
            order=20,
            requires_findings=True,
        )
    )
    
    inspector = Inspector(df, ui_layout=minimal_layout)
    inspector.render()
    """)

if st.button("Run Example 2"):
    minimal_layout = ComponentLayout(show_dividers=True)
    minimal_layout.add_component(
        ComponentWrapper(
            name="overview",
            render_func=render_overview,
            order=10,
            requires_findings=True,
        )
    )
    minimal_layout.add_component(
        ComponentWrapper(
            name="export",
            render_func=render_export_section,
            order=20,
            requires_findings=True,
        )
    )

    inspector = Inspector(df, ui_layout=minimal_layout)
    inspector.render()

st.divider()

# Example 3: Reordered layout (table first, then charts)
st.header("Example 3: Reordered Layout (Table First)")
with st.expander("Show code"):
    st.code("""
    # Start with default layout
    custom_layout = create_default_layout()
    
    # Remove all components
    custom_layout.components.clear()
    
    # Add components in custom order
    custom_layout.add_component(
        ComponentWrapper(
            name="table",
            render_func=render_table,
            order=10,  # First
            requires_df=True,
            requires_findings=True,
            requires_backend=True,
        )
    )
    custom_layout.add_component(
        ComponentWrapper(
            name="charts",
            render_func=render_charts,
            order=20,  # Second
            requires_df=True,
            requires_findings=True,
            requires_backend=True,
        )
    )
    custom_layout.add_component(
        ComponentWrapper(
            name="overview",
            render_func=render_overview,
            order=30,  # Third
            requires_findings=True,
        )
    )
    
    inspector = Inspector(df, ui_layout=custom_layout)
    inspector.render()
    """)

if st.button("Run Example 3"):
    custom_layout = create_default_layout()
    custom_layout.components.clear()

    custom_layout.add_component(
        ComponentWrapper(
            name="table",
            render_func=render_table,
            order=10,
            requires_df=True,
            requires_findings=True,
            requires_backend=True,
        )
    )
    custom_layout.add_component(
        ComponentWrapper(
            name="charts",
            render_func=render_charts,
            order=20,
            requires_df=True,
            requires_findings=True,
            requires_backend=True,
        )
    )
    custom_layout.add_component(
        ComponentWrapper(
            name="overview",
            render_func=render_overview,
            order=30,
            requires_findings=True,
        )
    )

    inspector = Inspector(df, ui_layout=custom_layout)
    inspector.render()

st.divider()

# Example 4: Disable specific components
st.header("Example 4: Disable Components Dynamically")
with st.expander("Show code"):
    st.code("""
    # Start with default layout
    layout = create_default_layout()
    
    # Disable charts component
    layout.disable_component("charts")
    
    inspector = Inspector(df, ui_layout=layout)
    inspector.render()
    """)

if st.button("Run Example 4"):
    layout = create_default_layout()
    layout.disable_component("charts")

    inspector = Inspector(df, ui_layout=layout)
    inspector.render()
