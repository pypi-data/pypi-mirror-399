# Feature Version Mapping

This document maps features to the PyPI versions where they were actually introduced, based on git history analysis.

## Version History

### v0.1.0 (Initial Release)
**Phase 0-1: MVP Features**

- Core Inspector class
- Pandas support
- Streamlit-native UI
- Null detection (`NullGhostDetector`)
- Type inconsistency detection (`TypeGhostDetector`)
- Basic outlier detection (`OutlierGhostDetector`)
- CSV upload UI (basic)
- Findings export (JSON/CSV)

**Commit:** `d42b85e` - Complete Phase 2: Add drift detection, rule authoring UI, and performance benchmarks

### v0.2.0
**Phase 2-4: Power Features & Advanced Ghosts**

**Phase 2 Features:**
- Drift detection (schema and distribution comparison)
- Rule authoring UI (range, regex, enum rules)
- Performance optimizations

**Phase 3 Features:**
- CLI wrapper (Click framework)
- Pandera rule export
- Great Expectations export

**Phase 4 Features:**
- Time-series anomaly detection
- Cross-column validation rules
- ML-assisted anomaly detection (scikit-learn: Isolation Forest, LOF, One-Class SVM)
- Collaboration features (annotations, shareable reports)
- Polars support

**Commits:**
- `7940d92` - Upgrade all docstrings and configure doctest support (CLI, Pandera)
- `9300f62` - Add comprehensive Read the Docs documentation setup (Time-series, ML, Collaboration, Cross-column)

### v0.3.0
**Version bump and documentation**

- Read the Docs integration
- Documentation improvements

**Commit:** `ed32c71` - Bump version to 0.3.0 and add Read the Docs badge

### v0.4.0
**Phase 5: Quick Wins**

- Rich CLI output enhancement
- orjson JSON serialization (2-3x faster)
- python-dotenv configuration management

**Commit:** `a053699` - Version bump to 0.4.0 and suppress third-party dependency warnings

### v0.5.0
**Phase 6: Feature Enhancements (Part 1)**

- Typer CLI framework
- PyOD anomaly detection (40+ algorithms)
- Ruptures change point detection
- scipy.stats statistical tests (Kolmogorov-Smirnov, chi-square)
- PyArrow Parquet export
- ydata-profiling integration
- Faker test data generation utilities

**Commit:** `e8a65ce` - docs: Update all documentation with Phase 6 feature enhancements

### v0.6.0
**Phase 6: Feature Enhancements (Part 2)**

- Enhanced File Upload component (drag-and-drop, animated progress, automatic encoding detection)

**Commit:** `d86b46a` - docs: Add file upload component documentation and fix ReadTheDocs build

### v0.7.0
**Phase 7: Advanced Integrations**

- **Modular UI Components**: Flexible component system with `BaseComponent`, `ComponentWrapper`, and `ComponentLayout` for custom UI composition
- **Plotly Interactive Visualizations**: Optional Plotly backend for interactive charts with zoom/pan, 3D visualizations, and enhanced time-series charts
- **tsfresh Time-Series Features**: Advanced time-series feature extraction (700+ features) for ML-based anomaly detection
- **Streamlit Extras UI Components**: Enhanced UI components including metric cards, badges, cards, and improved dataframe explorer
- **SQLAlchemy Database Backend**: Optional database storage for collaboration features (SQLite and PostgreSQL support)

**Commit:** `f917b87` - feat: Add modular UI component system and Phase 7 implementation plan

## Feature Quick Reference

| Feature | Version | Notes |
|---------|---------|-------|
| Core Inspector | v0.1.0 | Foundation |
| Null Detection | v0.1.0 | MVP |
| Type Detection | v0.1.0 | MVP |
| Outlier Detection | v0.1.0 | MVP |
| Drift Detection | v0.2.0 | Phase 2 |
| Custom Rules UI | v0.2.0 | Phase 2 |
| Polars Support | v0.2.0 | Phase 2 |
| CLI Tool (Click) | v0.2.0 | Phase 3 |
| Pandera Export | v0.2.0 | Phase 3 |
| Great Expectations Export | v0.2.0 | Phase 3 |
| Time-Series Anomalies | v0.2.0 | Phase 4 |
| Cross-Column Rules | v0.2.0 | Phase 4 |
| ML Anomaly Detection (scikit-learn) | v0.2.0 | Phase 4 |
| Collaboration Features | v0.2.0 | Phase 4 |
| Rich CLI Output | v0.4.0 | Phase 5 |
| orjson Fast JSON | v0.4.0 | Phase 5 |
| Configuration Management | v0.4.0 | Phase 5 |
| Typer CLI | v0.5.0 | Phase 6 |
| PyOD Algorithms | v0.5.0 | Phase 6 |
| Change Point Detection | v0.5.0 | Phase 6 |
| Statistical Tests | v0.5.0 | Phase 6 |
| Parquet Export | v0.5.0 | Phase 6 |
| Data Profiling | v0.5.0 | Phase 6 |
| Enhanced File Upload | v0.6.0 | Phase 6 |

## Notes

- Most features were added in v0.2.0, which was a major release including Phases 2, 3, and 4
- v0.3.0 was primarily a documentation and version bump release
- v0.4.0 focused on performance and developer experience improvements (Phase 5)
- v0.5.0 and v0.6.0 added advanced features and enhancements (Phase 6)
- v0.7.0 introduced advanced integrations including Plotly, tsfresh, Streamlit Extras, and SQLAlchemy (Phase 7)
