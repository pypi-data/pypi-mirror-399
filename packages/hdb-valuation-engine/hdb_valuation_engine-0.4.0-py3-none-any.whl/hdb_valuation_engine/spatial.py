"""Spatial analysis module for MRT accessibility scoring.

This module provides geospatial analysis capabilities for computing MRT accessibility
scores using KDTree-based nearest-neighbor queries.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import logging
import os
import pickle

import numpy as np
import pandas as pd

try:
    from sklearn.neighbors import KDTree
except Exception:  # noqa: BLE001
    KDTree = None


class TransportScorer:
    """Compute MRT accessibility scores using spatial nearest-neighbor queries.

    This scorer loads a catalog of MRT station coordinates, strictly excluding
    all LRT stations using a regex filter '^(BP|S[WE]|P[WE])'. The pattern
    matches the line codes for Bukit Panjang (BP), Sengkang (SW/SE), and Punggol
    (PW/PE) LRT loops, ensuring that only heavy rail stations are retained.

    A KDTree (from scikit-learn) is used for vectorized nearest-neighbor
    computation across thousands of records instantly, avoiding Python loops.

    Accessibility score definition
    ------------------------------
    score = max(0, 10 - (dist_km * 2))
    where dist_km is the Euclidean distance in kilometers from the HDB listing
    coordinate to the nearest MRT station in the filtered catalog.
    """

    def __init__(self, stations_df: pd.DataFrame | None = None, cache_dir: str | None = None) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self._stations: pd.DataFrame | None = None
        self._tree: KDTree | None = None
        self._cache_dir = cache_dir or os.path.join(os.getcwd(), ".cache_transport")
        os.makedirs(self._cache_dir, exist_ok=True)
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("TransportScorer initialized with cache_dir=%s", self._cache_dir)
        if stations_df is not None:
            self.load_stations(stations_df)

    @staticmethod
    def _exclude_lrt(df: pd.DataFrame) -> pd.DataFrame:
        """Exclude LRT stations using strict regex on line codes.

        Excludes station rows whose `line_code` matches '^(BP|S[WE]|P[WE])'.
        Column expectations:
        - name: station name (str)
        - line_code: string line code such as 'NS', 'EW', 'DT', 'CC', 'BP', 'SW'
        - lat, lon: numeric coordinates in degrees
        """
        if "line_code" not in df.columns:
            return df
        mask = ~df["line_code"].astype(str).str.match(r"^(BP|S[WE]|P[WE])", na=False)
        return df.loc[mask].copy()

    def _cache_paths(self, tag: str) -> tuple[str, str]:
        key = hashlib.sha256(tag.encode("utf-8")).hexdigest()[:16]
        return (
            os.path.join(self._cache_dir, f"stations_{key}.pkl"),
            os.path.join(self._cache_dir, f"kdtree_{key}.pkl"),
        )

    def clear_cache(self) -> None:
        """Delete cached stations and KDTree files in the cache directory."""
        try:
            import glob

            for p in glob.glob(os.path.join(self._cache_dir, "*.pkl")):
                with contextlib.suppress(Exception):
                    os.remove(p)
            if self.logger.isEnabledFor(logging.INFO):
                self.logger.info("Cleared transport cache at %s", self._cache_dir)
        except Exception:
            pass

    def _try_load_cache(self, tag: str) -> bool:
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("Transport cache lookup tag=%s dir=%s", tag, self._cache_dir)
        stations_pkl, tree_pkl = self._cache_paths(tag)
        try:
            with open(stations_pkl, "rb") as f:
                self._stations = pickle.load(f)  # nosec B301
            with open(tree_pkl, "rb") as f:
                self._tree = pickle.load(f)  # nosec B301
            self.logger.info("Transport cache HIT: %s", tag)
            return True
        except Exception:
            self.logger.info("Transport cache MISS: %s", tag)
            return False

    def _save_cache(self, tag: str) -> None:
        if self._stations is None or self._tree is None:
            return
        stations_pkl, tree_pkl = self._cache_paths(tag)
        try:
            with open(stations_pkl, "wb") as f:
                pickle.dump(self._stations, f)
            with open(tree_pkl, "wb") as f:
                pickle.dump(self._tree, f)
            self.logger.info("Saved transport cache for %s", tag)
        except Exception:
            pass

    def load_stations(self, stations_df: pd.DataFrame) -> None:
        """Load station catalog, exclude LRT, and build KDTree index.

        Parameters
        ----------
        stations_df : pd.DataFrame
            DataFrame with columns: ['name', 'line_code', 'lat', 'lon'].
        """
        if KDTree is None:
            raise ImportError("scikit-learn not available. Install scikit-learn to use TransportScorer.")
        required = ["name", "lat", "lon"]
        missing = [c for c in required if c not in stations_df.columns]
        if missing:
            raise ValueError(f"Stations catalog missing columns: {missing}")

        df = stations_df.copy()
        # Normalize columns
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
        # Try cache based on a stable tag (hash of station rows)
        tag = "csv:" + hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()[:16]  # type: ignore[union-attr]
        if self._try_load_cache(tag):
            return
        if "line_code" in df.columns:
            df["line_code"] = df["line_code"].astype(str).str.upper()
        # Fallback: if line_code missing, try to infer non-LRT by name not containing 'LRT'
        df = self._exclude_lrt(df)
        if "line_code" not in df.columns:
            df = df[~df.get("name", pd.Series("")).astype(str).str.contains("LRT", case=False, na=False)]

        df = df.dropna(subset=["lat", "lon"]).reset_index(drop=True)

        if df.empty:
            raise ValueError("No MRT stations available after LRT exclusion.")

        coords = np.deg2rad(df[["lat", "lon"]].to_numpy(dtype=float))
        # Use haversine-compatible KDTree by projecting to radians and custom metric
        self._tree = KDTree(coords, metric="euclidean")
        self._stations = df
        self._save_cache(tag)
        self.logger.info("Loaded %d MRT stations (LRT excluded)", len(df))

    def load_stations_geojson(self, path: str) -> None:
        """Load MRT stations from an LTA Exit GeoJSON file and build KDTree.

        The GeoJSON is expected to be a FeatureCollection where each feature is
        a station exit with properties containing station information. This
        loader will:
        - Extract station name and line code from common property keys.
        - **CRITICAL**: Preserve the robust STATION_NA / STN_NAME / STN_NAM fallback
          logic for parsing station names from various GeoJSON schemas.
        - Strictly exclude LRT using the regex '^(BP|S[WE]|P[WE])' on line codes
          when available, and additionally filter out any stations with 'LRT' in
          the name as a safety fallback.
        - Build a KDTree over exit coordinates (lon, lat). Using exits provides
          accurate pedestrian access points for distance calculations.

        Parameters
        ----------
        path : str
            Path to the GeoJSON file.
        """
        if KDTree is None:
            raise ImportError("scikit-learn not available. Install scikit-learn to use TransportScorer.")
        # Cache by file mtime and size for stability
        try:
            stat = os.stat(path)
            tag = f"geojson:{os.path.basename(path)}:{int(stat.st_mtime)}:{stat.st_size}"
            if self._try_load_cache(tag):
                return
        except Exception:
            tag = f"geojson:{os.path.basename(path)}"
        try:
            with open(path, encoding="utf-8") as f:
                gj = json.load(f)
        except FileNotFoundError:
            raise
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("Failed to read GeoJSON: %s", path)
            raise ValueError(f"Failed to read GeoJSON: {path}") from exc

        features = gj.get("features", []) if isinstance(gj, dict) else []
        rows: list[tuple[str, str | None, float, float]] = []
        for feat in features:
            try:
                geom = feat.get("geometry", {})
                if not geom or geom.get("type") != "Point":
                    continue
                coords = geom.get("coordinates")
                if not coords or len(coords) < 2:
                    continue
                lon, lat = float(coords[0]), float(coords[1])
                props = feat.get("properties", {}) or {}
                # CRITICAL: Candidate keys for station name - preserving robust fallback
                name = (
                    props.get("STATION_NA")
                    or props.get("STN_NAME")
                    or props.get("STN_NAM")
                    or props.get("NAME")
                    or props.get("StationName")
                    or props.get("stn_name")
                    or props.get("station")
                )
                line_code = (
                    props.get("LINE")
                    or props.get("LINE_CODE")
                    or props.get("LINE_N")
                    or props.get("MRT_LINE")
                    or props.get("railLine")
                    or props.get("line")
                )
                if name is None:
                    # Some datasets store station at 'STN_NAM' with exit codes separate
                    continue
                name_str = str(name).strip()
                lc_str = str(line_code).strip().upper() if line_code is not None else None
                rows.append((name_str, lc_str, lat, lon))
            except Exception:  # noqa: BLE001
                continue

        if not rows:
            raise ValueError("No station exits parsed from GeoJSON.")

        df = pd.DataFrame(rows, columns=["name", "line_code", "lat", "lon"])
        # Exclude LRT by line_code regex when available; also filter names containing 'LRT'
        df = self._exclude_lrt(df)
        df = df[~df["name"].astype(str).str.contains("LRT", case=False, na=False)]
        df = df.dropna(subset=["lat", "lon"]).reset_index(drop=True)
        if df.empty:
            raise ValueError("No MRT stations available after parsing/exclusion.")

        coords = np.deg2rad(df[["lat", "lon"]].to_numpy(dtype=float))
        self._tree = KDTree(coords, metric="euclidean")
        self._stations = df
        self._save_cache(tag)
        self.logger.info("Loaded %d MRT exits from GeoJSON (LRT excluded)", len(df))

    @staticmethod
    def _haversine_meters(
        latlon1: np.ndarray[tuple[int, int], np.dtype[np.float64]],
        latlon2: np.ndarray[tuple[int, int], np.dtype[np.float64]],
    ) -> np.ndarray[tuple[int], np.dtype[np.float64]]:
        """Compute haversine distance in meters between arrays of points.

        Parameters
        ----------
        latlon1 : np.ndarray
            Array of shape (n, 2) with columns [lat_rad, lon_rad] in radians.
        latlon2 : np.ndarray
            Array of shape (n, 2) with columns [lat_rad, lon_rad] in radians.
        """
        earth_radius_m = 6371000.0  # meters
        dlat = latlon2[:, 0] - latlon1[:, 0]
        dlon = latlon2[:, 1] - latlon1[:, 1]
        a = np.sin(dlat / 2.0) ** 2 + np.cos(latlon1[:, 0]) * np.cos(latlon2[:, 0]) * np.sin(dlon / 2.0) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return earth_radius_m * c  # type: ignore[no-any-return]

    def calculate_accessibility_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Annotate DataFrame with nearest MRT and accessibility score.

        Adds columns:
        - Nearest_MRT: name of nearest heavy-rail MRT station
        - Dist_m: distance to nearest station in meters
        - Accessibility_Score: score = max(0, 10 - (dist_km * 2))

        Expectations: Input `df` must have 'lat' and 'lon' columns (degrees).
        """
        if self._tree is None or self._stations is None:
            raise RuntimeError("TransportScorer not initialized. Call load_stations first.")

        if not {"lat", "lon"}.issubset(set(df.columns)):
            # No-op if coords not present; add NaNs
            out = df.copy()
            out["Nearest_MRT"] = np.nan
            out["Dist_m"] = np.nan
            out["Accessibility_Score"] = np.nan
            return out

        pts = np.deg2rad(df[["lat", "lon"]].to_numpy(dtype=float))
        # KDTree query (k=1)
        dist_rad, ind = self._tree.query(pts, k=1)
        # Convert chord distance in radian-space to meters using haversine to nearest
        nearest_rad = self._stations[["lat", "lon"]].to_numpy(dtype=float)
        nearest_rad = np.deg2rad(nearest_rad[ind.flatten()])
        dist_m = self._haversine_meters(pts, nearest_rad)

        # Score: max(0, 10 - 2 * km)
        dist_km = dist_m / 1000.0
        score = np.maximum(0.0, 10.0 - (dist_km * 2.0))

        out = df.copy()
        out["Nearest_MRT"] = self._stations.loc[ind.flatten(), "name"].to_numpy()
        out["Dist_m"] = dist_m
        out["Accessibility_Score"] = score
        return out
