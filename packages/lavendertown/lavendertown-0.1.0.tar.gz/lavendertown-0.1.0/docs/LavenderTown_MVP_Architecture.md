
# LavenderTown — MVP Architecture Diagram & Explanation

## Purpose
This document describes the **Minimum Viable Product (MVP) architecture** for LavenderTown,
a Streamlit-first data quality inspection framework focused on detecting “data ghosts”.

The design prioritizes:
- Clear separation of concerns
- Extensibility (plugin-style detectors)
- Streamlit-native rendering
- Low cognitive overhead for contributors

---

## High-Level Architecture

```
┌──────────────────────────┐
│        User / App        │
│  (Streamlit Application) │
└─────────────┬────────────┘
              │
              ▼
┌──────────────────────────┐
│        Inspector         │
│  (Orchestrator Layer)    │
└─────────────┬────────────┘
              │
   ┌──────────┼──────────┐
   ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Ghost   │ │Ghost   │ │Ghost   │
│Detector│ │Detector│ │Detector│
│(Nulls) │ │(Types) │ │(Stats) │
└────┬───┘ └────┬───┘ └────┬───┘
     │           │           │
     └───────────┴───────────┘
                 │
                 ▼
        ┌──────────────────┐
        │   Findings Model │
        │ (Normalized Data)│
        └─────────┬────────┘
                  │
        ┌─────────┼─────────┐
        ▼                   ▼
┌──────────────┐   ┌────────────────┐
│ Streamlit UI │   │ Exporters       │
│ (Charts &    │   │ (JSON / CSV)    │
│  Tables)     │   └────────────────┘
└──────────────┘
```

---

## Core Components

### 1. Inspector (Central Orchestrator)
**Responsibility:**
- Accepts a DataFrame (Pandas or Polars)
- Registers and runs ghost detectors
- Aggregates findings
- Controls Streamlit rendering

**Key API:**
```python
from lavendertown import Inspector

inspector = Inspector(df)
inspector.render()
```

The Inspector:
- Detects backend type (Pandas vs Polars)
- Applies caching (`st.cache_data`) where safe
- Acts as the single public-facing API

---

### 2. Ghost Detectors (Plugin System)
Each detector is:
- Stateless
- Focused on a single ghost category
- Easily swappable or extendable

**MVP Detectors:**
- `NullGhostDetector`
- `TypeGhostDetector`
- `OutlierGhostDetector`

**Interface:**
```python
class GhostDetector:
    def detect(self, df) -> list[GhostFinding]:
        ...
```

Detectors should never:
- Render UI
- Modify data
- Depend on Streamlit

---

### 3. Findings Model (Normalization Layer)

All detectors emit findings in a **shared schema**.

```python
GhostFinding:
    - ghost_type        # null, type, range, outlier
    - column            # affected column
    - severity          # info | warning | error
    - description       # human-readable
    - row_indices       # optional list[int]
    - metadata          # free-form dict
```

Benefits:
- UI and exporters don’t care *how* a ghost was detected
- Easy to add new detectors without UI changes

---

### 4. Streamlit UI Layer

**Responsibilities:**
- Present summaries and metrics
- Visualize ghosts (charts, tables, heatmaps)
- Filter and drill into problematic rows
- Explain “why this is a problem”

**UI Sections:**
- Overview metrics (total ghosts, severity counts)
- Sidebar ghost category filters
- Column-level visualizations
- Row-level preview

**Rendering Rule:**
> UI reads from Findings only — never raw detectors

---

### 5. Export Layer (MVP)
Supports exporting findings to:
- JSON (machine readable)
- CSV (analyst friendly)

Future extensions:
- Pandera schemas
- Great Expectations expectations
- Markdown reports

---

## Data Flow Summary

1. User loads data in Streamlit
2. Inspector initializes
3. Inspector runs detectors
4. Detectors emit normalized findings
5. Findings are cached and aggregated
6. UI renders interactive views
7. User optionally exports results

---

## MVP Constraints (Intentional)
- No rule authoring UI
- No cross-column logic
- No persistence or auth
- No background jobs

These are **explicitly deferred** to keep the MVP lean.

---

## Why This Architecture Works
- Encourages clean separation of logic and UI
- Makes Streamlit rendering predictable
- Allows incremental detector development
- Enables future non-Streamlit frontends

---

## Next Implementation Step
Build:
1. `GhostFinding` dataclass
2. `GhostDetector` base class
3. `NullGhostDetector`
4. Minimal `Inspector.render()`

