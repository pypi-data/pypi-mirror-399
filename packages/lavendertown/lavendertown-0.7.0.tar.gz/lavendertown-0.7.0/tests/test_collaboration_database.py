"""Tests for SQLAlchemy database storage backend."""

from __future__ import annotations

import pytest
import tempfile
from pathlib import Path

try:
    import sqlalchemy  # noqa: F401

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False


@pytest.mark.skipif(
    not SQLALCHEMY_AVAILABLE,
    reason="SQLAlchemy not available",
)
class TestDatabaseStorage:
    """Tests for DatabaseStorage class."""

    def test_database_storage_initialization_sqlite(self):
        """Test DatabaseStorage initialization with SQLite."""
        from lavendertown.collaboration.database_storage import DatabaseStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            database_url = f"sqlite:///{db_path}"
            storage = DatabaseStorage(database_url=database_url)
            assert storage is not None

    def test_database_storage_initialization_default(self):
        """Test DatabaseStorage initialization with default SQLite."""
        from lavendertown.collaboration.database_storage import DatabaseStorage

        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                storage = DatabaseStorage()
                assert storage is not None
            finally:
                os.chdir(original_cwd)

    def test_save_and_load_report(self):
        """Test saving and loading a report."""
        from lavendertown.collaboration.database_storage import DatabaseStorage
        from lavendertown.collaboration.models import ShareableReport
        from lavendertown.models import GhostFinding

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            database_url = f"sqlite:///{db_path}"
            storage = DatabaseStorage(database_url=database_url)

            findings = [
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Test finding",
                    row_indices=[0],
                    metadata={},
                )
            ]

            import uuid
            from datetime import datetime

            report = ShareableReport(
                id=str(uuid.uuid4()),
                title="Test Report",
                author="Test Author",
                created_at=datetime.now(),
                findings=findings,
            )

            report_id = storage.save_report(report)
            assert report_id is not None

            loaded_report = storage.load_report(report_id)
            assert loaded_report is not None
            assert loaded_report.title == "Test Report"
            assert loaded_report.author == "Test Author"
            assert len(loaded_report.findings) == 1

    def test_save_and_get_annotations(self):
        """Test saving and getting annotations."""
        from lavendertown.collaboration.database_storage import DatabaseStorage
        from lavendertown.collaboration.models import Annotation

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            database_url = f"sqlite:///{db_path}"
            storage = DatabaseStorage(database_url=database_url)

            import uuid
            from datetime import datetime

            annotation = Annotation(
                id=str(uuid.uuid4()),
                finding_id="finding_123",
                author="Test Author",
                timestamp=datetime.now(),
                comment="Test comment",
                tags=["tag1", "tag2"],
                status="open",
            )

            storage.save_annotation(annotation)

            annotations = storage.get_annotations("finding_123")
            assert len(annotations) == 1
            assert annotations[0].comment == "Test comment"
            assert annotations[0].author == "Test Author"

    def test_query_reports(self):
        """Test querying reports with filters."""
        from lavendertown.collaboration.database_storage import DatabaseStorage
        from lavendertown.collaboration.models import ShareableReport
        from datetime import datetime, timedelta

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            database_url = f"sqlite:///{db_path}"
            storage = DatabaseStorage(database_url=database_url)

            import uuid
            from datetime import datetime

            # Create multiple reports
            for i in range(3):
                report = ShareableReport(
                    id=str(uuid.uuid4()),
                    title=f"Report {i}",
                    author=f"Author {i % 2}",  # Two different authors
                    created_at=datetime.now(),
                    findings=[],
                )
                storage.save_report(report)

            # Query all reports
            all_reports = storage.query_reports()
            assert len(all_reports) == 3

            # Query by author
            author_reports = storage.query_reports(author="Author 0")
            assert len(author_reports) >= 1

            # Query with date range
            start_date = datetime.now() - timedelta(days=1)
            end_date = datetime.now() + timedelta(days=1)
            date_reports = storage.query_reports(
                start_date=start_date, end_date=end_date
            )
            assert len(date_reports) == 3

            # Query with limit
            limited_reports = storage.query_reports(limit=2)
            assert len(limited_reports) == 2


class TestDatabaseStorageFallback:
    """Tests for database storage fallback behavior."""

    def test_database_storage_raises_when_not_available(self):
        """Test that DatabaseStorage raises ImportError when SQLAlchemy not available."""
        if SQLALCHEMY_AVAILABLE:
            pytest.skip("SQLAlchemy is available, cannot test fallback")

        from lavendertown.collaboration.database_storage import DatabaseStorage

        with pytest.raises(ImportError, match="SQLAlchemy is required"):
            DatabaseStorage()


@pytest.mark.skipif(
    not SQLALCHEMY_AVAILABLE,
    reason="SQLAlchemy not available",
)
class TestStorageBackendAbstraction:
    """Tests for storage backend abstraction."""

    def test_get_storage_backend_file_default(self):
        """Test getting file storage backend by default."""
        from lavendertown.collaboration.storage import get_storage_backend

        # Should return FileStorage by default
        storage = get_storage_backend()
        assert storage is not None
        # FileStorage should have the required methods
        assert hasattr(storage, "save_annotation")
        assert hasattr(storage, "load_annotations")
        assert hasattr(storage, "save_report")
        assert hasattr(storage, "load_report")

    def test_file_storage_methods(self):
        """Test FileStorage class methods."""
        from lavendertown.collaboration.storage import FileStorage
        from lavendertown.collaboration.models import Annotation, ShareableReport
        from lavendertown.models import GhostFinding

        storage = FileStorage()

        import uuid
        from datetime import datetime

        # Test annotation methods
        annotation = Annotation(
            id=str(uuid.uuid4()),
            finding_id="test_finding",
            author="Test",
            timestamp=datetime.now(),
            comment="Test comment",
        )
        storage.save_annotation(annotation)

        annotations = storage.load_annotations("test_finding")
        assert len(annotations) >= 1

        import uuid
        from datetime import datetime

        # Test report methods
        report = ShareableReport(
            id=str(uuid.uuid4()),
            title="Test",
            author="Test",
            created_at=datetime.now(),
            findings=[
                GhostFinding(
                    ghost_type="null",
                    column="col1",
                    severity="warning",
                    description="Test",
                    row_indices=[],
                    metadata={},
                )
            ],
        )
        report_path = storage.save_report(report)
        assert report_path.exists()

        loaded_report = storage.load_report(str(report_path))
        assert loaded_report.title == "Test"
