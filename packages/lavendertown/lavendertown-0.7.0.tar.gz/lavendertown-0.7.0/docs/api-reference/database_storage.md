# Database Storage Backend

!!! info "Version"
    This feature was introduced in **v0.7.0**.

LavenderTown supports SQLAlchemy-based database storage for collaboration features, enabling scalable multi-user scenarios and persistent report storage.

## Installation

```bash
pip install lavendertown[database]
```

This installs:
- `sqlalchemy>=2.0.0`
- `psycopg2-binary>=2.9.0` (for PostgreSQL support)

## Configuration

### Environment Variables

Set the storage type and database URL:

```bash
# Use database storage
LAVENDERTOWN_STORAGE_TYPE=database

# SQLite (default, no URL needed)
# Database created at .lavendertown/lavendertown.db

# PostgreSQL
LAVENDERTOWN_DATABASE_URL=postgresql://user:password@localhost/lavendertown
```

### Programmatic Configuration

```python
from lavendertown.collaboration.database_storage import DatabaseStorage

# SQLite (default location)
storage = DatabaseStorage()

# SQLite (custom location)
storage = DatabaseStorage(database_url="sqlite:///path/to/database.db")

# PostgreSQL
storage = DatabaseStorage(
    database_url="postgresql://user:password@localhost/lavendertown"
)
```

## Usage

### Saving Reports

```python
from lavendertown.collaboration.models import ShareableReport
from lavendertown.models import GhostFinding
import uuid
from datetime import datetime

report = ShareableReport(
    id=str(uuid.uuid4()),
    title="Q4 Data Quality Report",
    author="Alice",
    created_at=datetime.now(),
    findings=[finding1, finding2],
)

report_id = storage.save_report(report)
```

### Loading Reports

```python
report = storage.load_report(report_id)
```

### Saving Annotations

```python
from lavendertown.collaboration.models import Annotation

annotation = Annotation(
    id=str(uuid.uuid4()),
    finding_id="finding_123",
    author="Bob",
    timestamp=datetime.now(),
    comment="This looks like a data entry error",
    tags=["data-entry", "needs-review"],
    status="reviewed",
)

storage.save_annotation(annotation)
```

### Querying Reports

```python
from datetime import datetime, timedelta

# Query all reports
all_reports = storage.query_reports()

# Query by author
author_reports = storage.query_reports(author="Alice")

# Query with date range
start_date = datetime.now() - timedelta(days=30)
recent_reports = storage.query_reports(
    start_date=start_date,
    limit=50
)
```

## Database Schema

The database storage creates the following tables:

- **reports**: Stores shareable reports with findings
- **annotations**: Stores annotations on findings
- **rulesets**: Stores rule sets (future use)

## Migration from File Storage

The system maintains backward compatibility with file-based storage. To migrate:

1. Export reports from file storage
2. Import them into database storage
3. Update configuration to use database storage

## Storage Backend Abstraction

The storage system uses an abstraction layer that supports both file and database backends:

```python
from lavendertown.collaboration.storage import get_storage_backend

# Get configured storage backend
storage = get_storage_backend()

# Use storage methods
storage.save_report(report)
storage.load_report(report_id)
storage.save_annotation(annotation)
```

## Error Handling

If SQLAlchemy is not installed, `DatabaseStorage` will raise an `ImportError`:

```python
try:
    storage = DatabaseStorage()
except ImportError:
    print("SQLAlchemy is required. Install with: pip install lavendertown[database]")
```

