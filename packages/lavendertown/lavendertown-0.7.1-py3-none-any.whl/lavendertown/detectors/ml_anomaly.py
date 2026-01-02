"""ML-assisted anomaly detector - detects anomalies using machine learning.

This module provides the MLAnomalyDetector class, which uses machine learning
algorithms to identify anomalies in numeric data. It supports multiple ML
algorithms including Isolation Forest, Local Outlier Factor (LOF), and
One-Class SVM.
"""

from __future__ import annotations

from lavendertown.detectors.base import GhostDetector, detect_dataframe_backend
from lavendertown.models import GhostFinding


class MLAnomalyDetector(GhostDetector):
    """Detects anomalies using machine learning algorithms.

    This detector uses unsupervised machine learning algorithms to identify
    anomalous patterns in numeric data. It supports multiple algorithms:

    scikit-learn algorithms:
    - Isolation Forest: Good for general anomaly detection
    - Local Outlier Factor (LOF): Density-based detection
    - One-Class SVM: Boundary-based detection

    PyOD algorithms (40+ additional algorithms available, requires pyod>=1.1.0):
    - ABOD: Angle-Based Outlier Detection
    - CBLOF: Cluster-Based Local Outlier Factor
    - HBOS: Histogram-based Outlier Score
    - KNN: k-Nearest Neighbors
    - MCD: Minimum Covariance Determinant
    - PCA: Principal Component Analysis
    - And many more (see PyOD documentation for full list)

    The detector automatically selects numeric columns for analysis and
    normalizes features before applying ML algorithms. For large datasets
    (>100k rows), it uses sampling to improve performance.

    Attributes:
        algorithm: ML algorithm to use. Options: "isolation_forest" (default),
            "lof", "one_class_svm".
        contamination: Expected proportion of anomalies (0.0 to 0.5).
            Default is 0.1 (10%).
        random_state: Random seed for reproducibility. None for random.
        max_samples: Maximum number of samples to use for training. If dataset
            is larger, it will be sampled. None to use all data.

    Example:
        Use default Isolation Forest::

            detector = MLAnomalyDetector()
            findings = detector.detect(df)

        Use LOF with custom contamination::

            detector = MLAnomalyDetector(
                algorithm="lof",
                contamination=0.05
            )
            findings = detector.detect(df)
    """

    def __init__(
        self,
        algorithm: str = "isolation_forest",
        contamination: float = 0.1,
        random_state: int | None = None,
        max_samples: int | None = None,
    ) -> None:
        """Initialize ML anomaly detector.

        Args:
            algorithm: ML algorithm to use. Valid options:
                scikit-learn algorithms:
                - "isolation_forest": Isolation Forest (default)
                - "lof": Local Outlier Factor
                - "one_class_svm": One-Class SVM
                PyOD algorithms (requires pyod>=1.1.0):
                - "abod": Angle-Based Outlier Detection
                - "cblof": Cluster-Based Local Outlier Factor
                - "hbos": Histogram-based Outlier Score
                - "knn": k-Nearest Neighbors
                - "mcd": Minimum Covariance Determinant
                - "pca": Principal Component Analysis
                - "iforest": PyOD's Isolation Forest
                - "ocsvm": PyOD's One-Class SVM
            contamination: Expected proportion of anomalies (0.0 to 0.5).
                Default is 0.1. Higher values detect more anomalies.
            random_state: Random seed for reproducibility. None for random.
            max_samples: Maximum number of samples for training. If dataset
                is larger, it will be sampled. None to use all data.
                Default is 10000 for performance.

        Raises:
            ValueError: If algorithm is invalid, or contamination is not
                in [0.0, 0.5], or max_samples is not positive.
            ImportError: If scikit-learn is not installed (raised during detect).
        """
        # Valid algorithms: scikit-learn and PyOD
        sklearn_algorithms = {"isolation_forest", "lof", "one_class_svm"}
        pyod_algorithms = {
            "abod",
            "cblof",
            "hbos",
            "knn",
            "mcd",
            "pca",
            "iforest",  # PyOD's Isolation Forest (alternative to sklearn)
            "ocsvm",  # PyOD's One-Class SVM (alternative to sklearn)
            "lof",  # PyOD's LOF (alternative to sklearn)
        }
        valid_algorithms = sklearn_algorithms | pyod_algorithms

        if algorithm not in valid_algorithms:
            raise ValueError(
                f"Algorithm must be one of {sorted(valid_algorithms)}, got {algorithm}"
            )

        if not 0.0 <= contamination <= 0.5:
            raise ValueError(
                f"Contamination must be between 0.0 and 0.5, got {contamination}"
            )

        if max_samples is not None and max_samples <= 0:
            raise ValueError(f"max_samples must be positive, got {max_samples}")

        self.algorithm = algorithm
        self.contamination = contamination
        self.random_state = random_state
        self.max_samples = max_samples if max_samples is not None else 10000

    def detect(self, df: object) -> list[GhostFinding]:
        """Detect anomalies using ML algorithms.

        Analyzes numeric columns in the DataFrame using machine learning
        algorithms to identify anomalous patterns. Works with both Pandas
        and Polars DataFrames.

        Args:
            df: DataFrame to analyze. Can be a pandas.DataFrame or
                polars.DataFrame. The backend is automatically detected.

        Returns:
            List of GhostFinding objects for columns containing ML-detected
            anomalies. Each finding includes:
            - ghost_type: "ml_anomaly"
            - column: Name of the column with anomalies (or "multiple" for
              multi-column analysis)
            - severity: "warning" if >5% anomalies, "info" otherwise
            - description: Human-readable description with anomaly counts
            - row_indices: List of row indices with anomalous values (Pandas only,
              None for Polars)
            - metadata: Dictionary with anomaly_count, total_count,
              anomaly_percentage, algorithm, contamination, and anomaly_scores

        Raises:
            ImportError: If scikit-learn or PyOD (depending on algorithm) is not
                installed. Install with: pip install lavendertown[ml]

        Note:
            For Polars DataFrames, row_indices will be None as Polars doesn't
            maintain index concepts. The finding will still include anomaly
            counts and statistics.
        """
        try:
            import sklearn  # noqa: F401
        except ImportError as e:
            raise ImportError(
                "scikit-learn is required for ML anomaly detection. "
                "Install with: pip install scikit-learn"
            ) from e

        backend = detect_dataframe_backend(df)

        if backend == "pandas":
            return self._detect_pandas(df)
        elif backend == "polars":
            return self._detect_polars(df)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def _detect_pandas(self, df: object) -> list[GhostFinding]:
        """Detect anomalies using Pandas API.

        Args:
            df: pandas.DataFrame to analyze.

        Returns:
            List of GhostFinding objects for columns containing anomalies.
        """
        import numpy as np

        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import OneClassSVM  # noqa: F401

        findings: list[GhostFinding] = []

        # Get numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()

        if not numeric_columns:
            return findings

        # Prepare data
        data = df[numeric_columns].dropna()

        if len(data) < 3:  # Need at least 3 samples
            return findings

        # Sample if too large
        if len(data) > self.max_samples:
            data = data.sample(n=self.max_samples, random_state=self.random_state)

        # Normalize features
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)

        # Train ML model
        model = self._create_model()
        anomaly_labels = model.fit_predict(data_scaled)

        # Convert labels: -1 = anomaly, 1 = normal
        anomaly_mask = anomaly_labels == -1
        anomaly_count = int(anomaly_mask.sum())

        if anomaly_count > 0:
            # Get anomaly scores if available
            # Both scikit-learn and PyOD models may have decision_scores_ or decision_function
            if hasattr(model, "decision_scores_"):
                # PyOD models store decision scores in decision_scores_ attribute
                anomaly_scores = model.decision_scores_
            elif hasattr(model, "decision_function"):
                # scikit-learn models use decision_function method
                anomaly_scores = model.decision_function(data_scaled)
                # For Isolation Forest, lower scores = more anomalous
                if self.algorithm in ("isolation_forest", "iforest"):
                    anomaly_scores = -anomaly_scores
            elif hasattr(model, "score_samples"):
                # Some models use score_samples
                anomaly_scores = model.score_samples(data_scaled)
            else:
                anomaly_scores = None

            # Get original indices for anomalies
            if len(data) == len(df):
                # No sampling, use original indices
                anomaly_indices = data[anomaly_mask].index.tolist()
            else:
                # Sampling was used, map back to original
                sampled_indices = data.index
                anomaly_indices = sampled_indices[anomaly_mask].tolist()

            anomaly_percentage = anomaly_count / len(data)

            # Determine severity
            if anomaly_percentage > 0.05:  # More than 5% anomalies
                severity = "warning"
            else:
                severity = "info"

            # Create finding for multi-column analysis
            finding = GhostFinding(
                ghost_type="ml_anomaly",
                column=", ".join(numeric_columns[:3])
                + (
                    f" (+{len(numeric_columns) - 3} more)"
                    if len(numeric_columns) > 3
                    else ""
                ),
                severity=severity,
                description=(
                    f"ML analysis detected {anomaly_count:,} anomalies "
                    f"({anomaly_percentage:.1%} of {len(data):,} rows) "
                    f"across {len(numeric_columns)} numeric columns using {self.algorithm}"
                ),
                row_indices=anomaly_indices,
                metadata={
                    "anomaly_count": anomaly_count,
                    "total_count": len(data),
                    "anomaly_percentage": float(anomaly_percentage),
                    "algorithm": self.algorithm,
                    "contamination": float(self.contamination),
                    "columns_analyzed": numeric_columns,
                    "anomaly_scores": (
                        anomaly_scores[anomaly_mask].tolist()
                        if anomaly_scores is not None
                        else None
                    ),
                },
            )
            findings.append(finding)

        return findings

    def _detect_polars(self, df: object) -> list[GhostFinding]:
        """Detect anomalies using Polars API.

        Args:
            df: polars.DataFrame to analyze.

        Returns:
            List of GhostFinding objects for columns containing anomalies.
            row_indices will be None for all findings.
        """
        import polars as pl

        from sklearn.ensemble import IsolationForest  # noqa: F401
        from sklearn.neighbors import LocalOutlierFactor  # noqa: F401
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import OneClassSVM  # noqa: F401

        findings: list[GhostFinding] = []

        # Get numeric columns
        numeric_columns = [
            col
            for col, dtype in df.schema.items()
            if dtype
            in [
                pl.Int8,
                pl.Int16,
                pl.Int32,
                pl.Int64,
                pl.UInt8,
                pl.UInt16,
                pl.UInt32,
                pl.UInt64,
                pl.Float32,
                pl.Float64,
            ]
        ]

        if not numeric_columns:
            return findings

        # Convert to pandas for ML processing
        data = df.select(numeric_columns).drop_nulls().to_pandas()

        if len(data) < 3:
            return findings

        # Sample if too large
        if len(data) > self.max_samples:
            data = data.sample(n=self.max_samples, random_state=self.random_state)

        # Normalize features
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)

        # Train ML model
        model = self._create_model()
        anomaly_labels = model.fit_predict(data_scaled)

        # Convert labels: PyOD and scikit-learn both use 1 = normal, -1/0 = anomaly

        anomaly_mask = (anomaly_labels == -1) | (anomaly_labels == 0)
        anomaly_count = int(anomaly_mask.sum())

        if anomaly_count > 0:
            # Get anomaly scores if available
            # Both scikit-learn and PyOD models may have decision_scores_ or decision_function
            if hasattr(model, "decision_scores_"):
                # PyOD models store decision scores in decision_scores_ attribute
                anomaly_scores = model.decision_scores_
            elif hasattr(model, "decision_function"):
                # scikit-learn models use decision_function method
                anomaly_scores = model.decision_function(data_scaled)
                # For Isolation Forest, lower scores = more anomalous
                if self.algorithm in ("isolation_forest", "iforest"):
                    anomaly_scores = -anomaly_scores
            elif hasattr(model, "score_samples"):
                # Some models use score_samples
                anomaly_scores = model.score_samples(data_scaled)
            else:
                anomaly_scores = None

            anomaly_percentage = anomaly_count / len(data)

            # Determine severity
            if anomaly_percentage > 0.05:
                severity = "warning"
            else:
                severity = "info"

            finding = GhostFinding(
                ghost_type="ml_anomaly",
                column=", ".join(numeric_columns[:3])
                + (
                    f" (+{len(numeric_columns) - 3} more)"
                    if len(numeric_columns) > 3
                    else ""
                ),
                severity=severity,
                description=(
                    f"ML analysis detected {anomaly_count:,} anomalies "
                    f"({anomaly_percentage:.1%} of {len(data):,} rows) "
                    f"across {len(numeric_columns)} numeric columns using {self.algorithm}"
                ),
                row_indices=None,  # Polars doesn't maintain indices
                metadata={
                    "anomaly_count": anomaly_count,
                    "total_count": len(data),
                    "anomaly_percentage": float(anomaly_percentage),
                    "algorithm": self.algorithm,
                    "contamination": float(self.contamination),
                    "columns_analyzed": numeric_columns,
                    "anomaly_scores": (
                        anomaly_scores[anomaly_mask].tolist()
                        if anomaly_scores is not None
                        else None
                    ),
                },
            )
            findings.append(finding)

        return findings

    def _create_model(self) -> object:
        """Create and return ML model instance.

        Returns:
            ML model instance (scikit-learn or PyOD estimator).

        Raises:
            ImportError: If required library (scikit-learn or PyOD) is not installed.
        """
        # Check if this is a PyOD algorithm
        pyod_algorithms = {
            "abod",
            "cblof",
            "hbos",
            "knn",
            "mcd",
            "pca",
            "iforest",
            "ocsvm",
        }

        if self.algorithm in pyod_algorithms:
            # Use PyOD
            try:
                import pyod  # noqa: F401
            except ImportError as e:
                raise ImportError(
                    "PyOD is required for PyOD algorithms. "
                    "Install with: pip install lavendertown[ml]"
                ) from e

            return self._create_pyod_model()

        # Use scikit-learn
        from sklearn.ensemble import IsolationForest
        from sklearn.neighbors import LocalOutlierFactor
        from sklearn.svm import OneClassSVM

        if self.algorithm == "isolation_forest":
            return IsolationForest(
                contamination=self.contamination,
                random_state=self.random_state,
            )
        elif self.algorithm == "lof":
            return LocalOutlierFactor(
                contamination=self.contamination,
                novelty=False,  # Using for outlier detection, not novelty
            )
        elif self.algorithm == "one_class_svm":
            return OneClassSVM(
                nu=self.contamination,
                gamma="scale",
            )
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")

    def _create_pyod_model(self) -> object:
        """Create PyOD model instance.

        Returns:
            PyOD detector instance.
        """
        # Import PyOD models
        from pyod.models.abod import ABOD
        from pyod.models.cblof import CBLOF
        from pyod.models.hbos import HBOS
        from pyod.models.knn import KNN
        from pyod.models.mcd import MCD
        from pyod.models.pca import PCA
        from pyod.models.iforest import IForest
        from pyod.models.ocsvm import OCSVM

        # Map algorithm names to PyOD classes
        algorithm_map = {
            "abod": ABOD,
            "cblof": CBLOF,
            "hbos": HBOS,
            "knn": KNN,
            "mcd": MCD,
            "pca": PCA,
            "iforest": IForest,
            "ocsvm": OCSVM,
        }

        model_class = algorithm_map[self.algorithm]

        # Create model with contamination parameter
        # Most PyOD models use contamination parameter
        if self.algorithm == "ocsvm":
            # OCSVM uses contamination
            return model_class(contamination=self.contamination)
        elif self.algorithm == "knn":
            # KNN uses contamination
            return model_class(contamination=self.contamination)
        elif self.algorithm == "iforest":
            # IForest supports random_state
            return model_class(
                contamination=self.contamination, random_state=self.random_state
            )
        else:
            # Most other PyOD models use contamination
            return model_class(contamination=self.contamination)
