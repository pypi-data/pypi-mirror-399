"""Database storage backend for collaboration features using SQLAlchemy."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

try:
    from sqlalchemy import (
        JSON,
        Column,
        DateTime,
        Integer,
        String,
        Text,
        create_engine,
    )
    from sqlalchemy.orm import declarative_base
    from sqlalchemy.orm import sessionmaker

    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    create_engine = None  # type: ignore[assignment, misc]
    declarative_base = None  # type: ignore[assignment, misc]
    sessionmaker = None  # type: ignore[assignment, misc]

from lavendertown.collaboration.models import Annotation, ShareableReport
from lavendertown.models import GhostFinding

if SQLALCHEMY_AVAILABLE:
    Base = declarative_base()  # type: ignore[assignment, misc]

    class ReportModel(Base):  # type: ignore[misc, valid-type]
        """SQLAlchemy model for reports."""

        __tablename__ = "reports"

        id = Column(Integer, primary_key=True)
        title = Column(String(255), nullable=False)
        author = Column(String(255), nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
        findings_json = Column(JSON, nullable=False)

    class AnnotationModel(Base):  # type: ignore[misc, valid-type]
        """SQLAlchemy model for annotations."""

        __tablename__ = "annotations"

        id = Column(Integer, primary_key=True)
        report_id = Column(Integer, nullable=False)
        finding_id = Column(String(255), nullable=False)
        author = Column(String(255), nullable=False)
        comment = Column(Text)
        tags = Column(JSON)
        status = Column(String(50))
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    class RuleSetModel(Base):  # type: ignore[misc, valid-type]
        """SQLAlchemy model for rulesets."""

        __tablename__ = "rulesets"

        id = Column(Integer, primary_key=True)
        name = Column(String(255), nullable=False)
        description = Column(Text)
        rules_json = Column(JSON, nullable=False)
        created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DatabaseStorage:
    """Database storage backend for collaboration features."""

    def __init__(self, database_url: str | None = None) -> None:
        """Initialize database storage.

        Args:
            database_url: SQLAlchemy database URL. If None, uses SQLite in
                .lavendertown directory. Examples:
                - SQLite: "sqlite:///lavendertown.db"
                - PostgreSQL: "postgresql://user:pass@localhost/lavendertown"
        """
        if not SQLALCHEMY_AVAILABLE:
            raise ImportError(
                "SQLAlchemy is required for database storage. "
                "Install with: pip install lavendertown[database]"
            )

        if database_url is None:
            from pathlib import Path

            storage_dir = Path.cwd() / ".lavendertown"
            storage_dir.mkdir(exist_ok=True)
            database_url = f"sqlite:///{storage_dir / 'lavendertown.db'}"

        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables
        Base.metadata.create_all(self.engine)

    def save_report(self, report: ShareableReport) -> str:
        """Save a report to the database.

        Args:
            report: ShareableReport to save

        Returns:
            Report ID as string
        """
        session = self.SessionLocal()
        try:
            # Convert findings to JSON
            findings_json = [f.__dict__ for f in report.findings]

            db_report = ReportModel(
                title=report.title,
                author=report.author,
                findings_json=findings_json,
            )
            session.add(db_report)
            session.commit()
            return str(db_report.id)
        finally:
            session.close()

    def load_report(self, report_id: str) -> ShareableReport | None:
        """Load a report from the database.

        Args:
            report_id: Report ID

        Returns:
            ShareableReport if found, None otherwise
        """
        session = self.SessionLocal()
        try:
            db_report = session.query(ReportModel).filter_by(id=int(report_id)).first()
            if db_report is None:
                return None

            # Convert JSON back to findings
            findings_data = db_report.findings_json
            findings = [GhostFinding(**f) for f in findings_data]  # type: ignore[arg-type, attr-defined]

            return ShareableReport(
                id=str(db_report.id),
                title=str(db_report.title),  # type: ignore[arg-type]
                author=str(db_report.author),  # type: ignore[arg-type]
                created_at=db_report.created_at,  # type: ignore[arg-type]
                findings=findings,
            )
        finally:
            session.close()

    def save_annotation(self, annotation: Annotation) -> None:
        """Save an annotation to the database.

        Args:
            annotation: Annotation to save
        """
        session = self.SessionLocal()
        try:
            db_annotation = AnnotationModel(
                report_id=0,  # Not stored in Annotation model, use 0 as default
                finding_id=annotation.finding_id,
                author=annotation.author,
                comment=annotation.comment,
                tags=annotation.tags,
                status=annotation.status,
            )
            session.add(db_annotation)
            session.commit()
        finally:
            session.close()

    def get_annotations(self, finding_id: str) -> list[Annotation]:
        """Get annotations for a finding.

        Args:
            finding_id: Finding ID

        Returns:
            List of annotations
        """
        session = self.SessionLocal()
        try:
            db_annotations = (
                session.query(AnnotationModel).filter_by(finding_id=finding_id).all()
            )

            annotations = []
            for db_ann in db_annotations:
                annotations.append(
                    Annotation(
                        id=str(db_ann.id),
                        finding_id=str(db_ann.finding_id),  # type: ignore[arg-type]
                        author=str(db_ann.author),  # type: ignore[arg-type]
                        timestamp=db_ann.created_at,  # type: ignore[arg-type]
                        comment=str(db_ann.comment or ""),  # type: ignore[arg-type]
                        tags=list(db_ann.tags or []),  # type: ignore[arg-type]
                        status=str(db_ann.status) if db_ann.status else None,  # type: ignore[arg-type]
                    )
                )
            return annotations
        finally:
            session.close()

    def query_reports(
        self,
        author: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 100,
    ) -> list[dict[str, object]]:
        """Query reports with filters.

        Args:
            author: Filter by author
            start_date: Filter reports created after this date
            end_date: Filter reports created before this date
            limit: Maximum number of results

        Returns:
            List of report dictionaries
        """
        session = self.SessionLocal()
        try:
            query = session.query(ReportModel)

            if author:
                query = query.filter_by(author=author)
            if start_date:
                query = query.filter(ReportModel.created_at >= start_date)
            if end_date:
                query = query.filter(ReportModel.created_at <= end_date)

            query = query.order_by(ReportModel.created_at.desc()).limit(limit)

            reports = []
            for db_report in query.all():
                reports.append(
                    {
                        "id": str(db_report.id),
                        "title": db_report.title,
                        "author": db_report.author,
                        "created_at": db_report.created_at,
                        "finding_count": len(db_report.findings_json),
                    }
                )
            return reports
        finally:
            session.close()
