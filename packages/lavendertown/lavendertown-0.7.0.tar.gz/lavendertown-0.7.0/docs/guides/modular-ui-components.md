# Modular UI Components

LavenderTown's Streamlit UI components are now fully modular, allowing you to customize which components are displayed, their order, and even create completely custom layouts.

## Overview

The modular component system consists of:

- **UIComponent Protocol**: A protocol that all components must follow
- **BaseComponent**: Abstract base class for creating custom components
- **ComponentWrapper**: Wrapper to convert function-based components to component objects
- **ComponentLayout**: Manages the composition and rendering of multiple components

## Basic Usage

### Default Layout

By default, the Inspector uses a standard layout with all components:

```python
from lavendertown import Inspector
import pandas as pd

df = pd.read_csv("data.csv")
inspector = Inspector(df)
inspector.render()  # Uses default layout
```

The default layout includes (in order):
1. Overview (metrics and statistics)
2. Charts (visualizations)
3. Table (detailed findings table)
4. Export (download buttons)

### Custom Layout

Create a custom layout by providing a `ComponentLayout` to the Inspector:

```python
from lavendertown import Inspector
from lavendertown.ui.layout import ComponentLayout, create_default_layout
from lavendertown.ui.base import ComponentWrapper
from lavendertown.ui.overview import render_overview
from lavendertown.ui.export import render_export_section
import pandas as pd

# Create minimal layout (overview + export only)
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

df = pd.read_csv("data.csv")
inspector = Inspector(df, ui_layout=minimal_layout)
inspector.render()
```

## Component Management

### Adding Components

```python
from lavendertown.ui.layout import ComponentLayout
from lavendertown.ui.base import ComponentWrapper
from lavendertown.ui.charts import render_charts

layout = ComponentLayout()

# Add component at the end
layout.add_component(
    ComponentWrapper(
        name="charts",
        render_func=render_charts,
        order=20,
        requires_df=True,
        requires_findings=True,
        requires_backend=True,
    )
)

# Add component at specific position
layout.add_component(
    ComponentWrapper(name="custom", render_func=my_custom_component),
    position=0  # Insert at beginning
)
```

### Removing Components

```python
# Remove by name
layout.remove_component("charts")
```

### Enabling/Disabling Components

```python
# Disable a component (it won't render but stays in the layout)
layout.disable_component("charts")

# Enable a component
layout.enable_component("charts")
```

### Reordering Components

Components are automatically sorted by their `order` attribute. Lower numbers appear first:

```python
# Get a component and change its order
charts = layout.get_component("charts")
if charts:
    charts.order = 5  # Move to beginning
```

## Creating Custom Components

### Using ComponentWrapper

Wrap existing functions to make them components:

```python
from lavendertown.ui.base import ComponentWrapper

def my_custom_component(st, findings):
    st.header("Custom Component")
    st.write(f"Found {len(findings)} issues")

layout.add_component(
    ComponentWrapper(
        name="custom",
        render_func=my_custom_component,
        order=15,
        requires_findings=True,
    )
)
```

### Using BaseComponent

Create a class-based component:

```python
from lavendertown.ui.base import BaseComponent
from lavendertown.models import GhostFinding

class MyCustomComponent(BaseComponent):
    def __init__(self):
        super().__init__(
            name="custom",
            enabled=True,
            order=15,
        )
    
    def render(
        self,
        st,
        df=None,
        findings=None,
        backend=None,
        **kwargs
    ):
        st.header("Custom Component")
        if findings:
            st.write(f"Found {len(findings)} issues")

layout.add_component(MyCustomComponent())
```

## Component Requirements

When creating components, specify what they need:

- `requires_df=True`: Component needs the DataFrame
- `requires_findings=True`: Component needs the findings list
- `requires_backend=True`: Component needs backend info ("pandas" or "polars")

The layout system automatically passes only the required parameters to each component.

## Examples

### Example 1: Minimal Layout

Show only overview and export:

```python
from lavendertown.ui.layout import ComponentLayout
from lavendertown.ui.base import ComponentWrapper
from lavendertown.ui.overview import render_overview
from lavendertown.ui.export import render_export_section

minimal = ComponentLayout()
minimal.add_component(
    ComponentWrapper("overview", render_overview, order=10, requires_findings=True)
)
minimal.add_component(
    ComponentWrapper("export", render_export_section, order=20, requires_findings=True)
)

inspector = Inspector(df, ui_layout=minimal)
```

### Example 2: Reordered Layout

Show table first, then charts:

```python
from lavendertown.ui.layout import create_default_layout

layout = create_default_layout()
layout.components.clear()  # Remove all

# Add in custom order
layout.add_component(ComponentWrapper("table", render_table, order=10, ...))
layout.add_component(ComponentWrapper("charts", render_charts, order=20, ...))
layout.add_component(ComponentWrapper("overview", render_overview, order=30, ...))
```

### Example 3: Conditional Components

Dynamically enable/disable based on conditions:

```python
layout = create_default_layout()

# Disable charts if dataset is too large
if len(df) > 100000:
    layout.disable_component("charts")

inspector = Inspector(df, ui_layout=layout)
```

## Available Components

The following components are available in the default layout:

- `overview`: High-level metrics and statistics (`render_overview`)
- `charts`: Visualizations and charts (`render_charts`)
- `table`: Detailed findings table (`render_table`)
- `export`: Export/download section (`render_export_section`)

Additional components can be imported from `lavendertown.ui`:

- `render_sidebar`: Sidebar with filters and summary
- `render_rule_management`: Rule authoring interface
- `render_file_upload`: Enhanced file upload component

## Best Practices

1. **Use meaningful names**: Component names should be descriptive
2. **Set appropriate order**: Use increments of 10 (10, 20, 30) to allow easy reordering
3. **Specify requirements**: Always set `requires_df`, `requires_findings`, `requires_backend` correctly
4. **Keep components focused**: Each component should have a single responsibility
5. **Test layouts**: Verify your custom layouts work with different datasets

## Migration Guide

Existing code continues to work without changes. The Inspector uses the default layout if no custom layout is provided.

To migrate to custom layouts:

1. Import the layout utilities
2. Create a `ComponentLayout`
3. Add components in your desired order
4. Pass the layout to `Inspector(ui_layout=layout)`

See `examples/custom_ui_layout.py` for complete examples.

