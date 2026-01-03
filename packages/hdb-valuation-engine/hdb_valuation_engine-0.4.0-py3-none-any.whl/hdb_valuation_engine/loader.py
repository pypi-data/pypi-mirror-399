"""Data loading module for HDB Valuation Engine.

This module handles CSV ingestion and schema normalization for HDB resale data.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Schema:
    """Canonical column names expected by the pipeline.

    This class centralizes schema expectations while allowing flexible mapping
    from real-world datasets where names may vary slightly in case or spacing.
    """

    town: str = "town"
    flat_type: str = "flat_type"
    resale_price: str = "resale_price"
    floor_area: str = "floor_area_sqm"
    remaining_lease_raw: str = "remaining_lease"

    # Engineered fields
    remaining_lease_years: str = "remaining_lease_years"
    price_efficiency: str = "price_efficiency"
    z_price_efficiency: str = "z_price_efficiency"
    valuation_score: str = "valuation_score"


class HDBLoader:
    """Load and normalize HDB resale CSV data.

    The loader focuses on robust file I/O and schema normalization. It lowercases
    and strips column names to mitigate schema drift and attempts to coerce core
    numeric columns into numeric dtype with proper NA handling.
    """

    def __init__(self, schema: Schema | None = None) -> None:
        self.schema = schema or Schema()
        self.logger = logging.getLogger(self.__class__.__name__)

    def load(self, path: str) -> pd.DataFrame:
        """Load CSV into a pandas DataFrame with normalized column names.

        Parameters
        ----------
        path : str
            Path to the CSV file.

        Returns
        -------
        pd.DataFrame
            DataFrame with normalized columns and raw types preserved where possible.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the CSV cannot be parsed.
        """
        self.logger.info("Loading CSV file: %s", path)
        try:
            df = pd.read_csv(path)
        except FileNotFoundError:
            self.logger.error("File not found: %s", path)
            raise
        except Exception as exc:  # noqa: BLE001
            self.logger.exception("Failed to read CSV: %s", path)
            raise ValueError(f"Failed to read CSV: {path}") from exc

        # Normalize column names: lowercase, strip, replace spaces with underscore
        df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
        self.logger.debug("Normalized columns: %s", df.columns.tolist())

        # Coerce common numeric fields when present
        for col in [self.schema.resale_price, self.schema.floor_area]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df
