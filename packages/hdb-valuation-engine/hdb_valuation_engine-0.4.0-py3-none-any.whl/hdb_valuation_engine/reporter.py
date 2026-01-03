"""Reporting module for filtering and presenting valuation results.

This module handles filtering, ranking, and formatting of valuation results
for display and export.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from hdb_valuation_engine.loader import Schema


class ReportGenerator:
    """Filter, rank, and render a clean buy list table to console.

    Filtering
    ---------
    - Optional exact/partial `town` filter.
    - Optional `budget` filter for maximum resale price.
    - Extended filters: flat_model, flat_type (exact or partial), storey_min/max,
      area_min/max, lease_min/max.

    Ranking
    -------
    - Sort by `valuation_score` descending (highest implies most undervalued),
      with ties broken by lowest price_efficiency and then lowest resale_price.
    - Display the top N results (default: 10).

    Rendering
    ---------
    - Human-friendly table using pandas' built-in formatting.
    """

    def __init__(self, schema: Schema | None = None) -> None:
        self.schema = schema or Schema()
        self.logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def _parse_storey_range(sr: str) -> tuple[int | None, int | None]:
        """Parse HDB storey range strings like "07 TO 09" into (min, max).

        Non-parsable inputs return (None, None).
        """
        try:
            s = str(sr).strip()
            parts = s.split("TO") if "TO" in s else s.split("-")
            parts = [p.strip() for p in parts]
            if len(parts) == 2:
                return int(parts[0]), int(parts[1])
            # Sometimes raw single like "10" or "01"
            v = int(s)
            return v, v
        except Exception:  # noqa: BLE001
            return None, None

    def _apply_filters(
        self,
        df: pd.DataFrame,
        town: str | None = None,
        town_like: str | None = None,
        budget: float | None = None,
        flat_type: str | None = None,
        flat_type_like: str | None = None,
        flat_model: str | None = None,
        flat_model_like: str | None = None,
        storey_min: int | None = None,
        storey_max: int | None = None,
        area_min: float | None = None,
        area_max: float | None = None,
        lease_min: float | None = None,
        lease_max: float | None = None,
    ) -> pd.DataFrame:
        """Apply user-specified filters to DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            The scored dataset.
        town : Optional[str]
            Town name for exact case-insensitive filtering.
        town_like : Optional[str]
            Substring case-insensitive match for town.
        budget : Optional[float]
            Maximum resale price.
        flat_type : Optional[str]
            Exact match filter for flat_type (case-insensitive).
        flat_type_like : Optional[str]
            Substring match for flat_type.
        flat_model : Optional[str]
            Exact match filter for flat_model.
        flat_model_like : Optional[str]
            Substring match for flat_model.
        storey_min, storey_max : Optional[int]
            Min/max storey number filter (overlap with storey_range).
        area_min, area_max : Optional[float]
            Floor area filters.
        lease_min, lease_max : Optional[float]
            Remaining lease (years) filters.
        """
        s = self.schema
        out = df.copy()

        # Town filters
        if town:
            if s.town not in out.columns:
                self.logger.warning("Town column '%s' not found; skipping town filter", s.town)
            else:
                out = out[out[s.town].astype(str).str.lower() == town.strip().lower()]
        if town_like:
            if s.town not in out.columns:
                self.logger.warning("Town column '%s' not found; skipping town_like filter", s.town)
            else:
                out = out[out[s.town].astype(str).str.contains(town_like, case=False, na=False)]

        # Budget filter
        if budget is not None:
            if s.resale_price not in out.columns:
                self.logger.warning("Resale price column '%s' not found; skipping budget filter", s.resale_price)
            else:
                out = out[pd.to_numeric(out[s.resale_price], errors="coerce") <= float(budget)]

        # Flat type filters
        if flat_type and s.flat_type in out.columns:
            out = out[out[s.flat_type].astype(str).str.lower() == flat_type.strip().lower()]
        if flat_type_like and s.flat_type in out.columns:
            out = out[out[s.flat_type].astype(str).str.contains(flat_type_like, case=False, na=False)]

        # Flat model filters
        if flat_model and "flat_model" in out.columns:
            out = out[out["flat_model"].astype(str).str.lower() == flat_model.strip().lower()]
        if flat_model_like and "flat_model" in out.columns:
            out = out[out["flat_model"].astype(str).str.contains(flat_model_like, case=False, na=False)]

        # Area filters
        if area_min is not None and s.floor_area in out.columns:
            out = out[pd.to_numeric(out[s.floor_area], errors="coerce") >= float(area_min)]
        if area_max is not None and s.floor_area in out.columns:
            out = out[pd.to_numeric(out[s.floor_area], errors="coerce") <= float(area_max)]

        # Lease filters
        if lease_min is not None and s.remaining_lease_years in out.columns:
            out = out[pd.to_numeric(out[s.remaining_lease_years], errors="coerce") >= float(lease_min)]
        if lease_max is not None and s.remaining_lease_years in out.columns:
            out = out[pd.to_numeric(out[s.remaining_lease_years], errors="coerce") <= float(lease_max)]

        # Storey overlap filters via storey_range string
        if (storey_min is not None or storey_max is not None) and "storey_range" in out.columns:
            mins, maxs = [], []
            for v in out["storey_range"].tolist():
                mn, mx = self._parse_storey_range(v)
                mins.append(mn)
                maxs.append(mx)
            out = out.assign(__sr_min=pd.Series(mins, dtype="Int64"), __sr_max=pd.Series(maxs, dtype="Int64"))
            if storey_min is not None:
                out = out[(out["__sr_max"].fillna(-np.inf) >= int(storey_min))]
            if storey_max is not None:
                out = out[(out["__sr_min"].fillna(np.inf) <= int(storey_max))]
            out = out.drop(columns=["__sr_min", "__sr_max"])

        return out

    def generate_dataframe(
        self,
        df: pd.DataFrame,
        town: str | None = None,
        town_like: str | None = None,
        budget: float | None = None,
        flat_type: str | None = None,
        flat_type_like: str | None = None,
        flat_model: str | None = None,
        flat_model_like: str | None = None,
        storey_min: int | None = None,
        storey_max: int | None = None,
        area_min: float | None = None,
        area_max: float | None = None,
        lease_min: float | None = None,
        lease_max: float | None = None,
        top_n: int = 10,
        full: bool = False,
    ) -> pd.DataFrame:
        """Produce the filtered, sorted DataFrame for display/export.

        If full is True, returns all rows after sorting; otherwise, returns the top_n rows.
        """
        s = self.schema
        filtered = self._apply_filters(
            df,
            town=town,
            town_like=town_like,
            budget=budget,
            flat_type=flat_type,
            flat_type_like=flat_type_like,
            flat_model=flat_model,
            flat_model_like=flat_model_like,
            storey_min=storey_min,
            storey_max=storey_max,
            area_min=area_min,
            area_max=area_max,
            lease_min=lease_min,
            lease_max=lease_max,
        )

        cols_pref = [
            s.town,
            s.flat_type,
            "flat_model" if "flat_model" in filtered.columns else None,
            "storey_range" if "storey_range" in filtered.columns else None,
            s.resale_price,
            s.floor_area,
            s.remaining_lease_years,
            "price_per_sqm" if "price_per_sqm" in filtered.columns else None,
            s.price_efficiency,
            s.z_price_efficiency,
            s.valuation_score,
            "growth_potential" if "growth_potential" in filtered.columns else None,
            "psm_ratio" if "psm_ratio" in filtered.columns else None,
            "Nearest_MRT" if "Nearest_MRT" in filtered.columns else None,
            "Dist_m" if "Dist_m" in filtered.columns else None,
            "Accessibility_Score" if "Accessibility_Score" in filtered.columns else None,
        ]
        cols_exist = [c for c in cols_pref if c is not None and c in filtered.columns]

        display = filtered[cols_exist].copy()
        if s.valuation_score in display.columns:
            display = display.dropna(subset=[s.valuation_score])

        sort_cols: list[str] = []
        ascending: list[bool] = []
        if s.valuation_score in display.columns:
            sort_cols.append(s.valuation_score)
            ascending.append(False)
        if s.price_efficiency in display.columns:
            sort_cols.append(s.price_efficiency)
            ascending.append(True)
        if s.resale_price in display.columns:
            sort_cols.append(s.resale_price)
            ascending.append(True)
        if sort_cols:
            display = display.sort_values(by=sort_cols, ascending=ascending)

        # Round for presentation but keep raw dtype for export (we'll round a copy for printing)
        if full:
            return display
        return display.head(top_n)

    def render(
        self,
        df: pd.DataFrame,
        town: str | None = None,
        town_like: str | None = None,
        budget: float | None = None,
        flat_type: str | None = None,
        flat_type_like: str | None = None,
        flat_model: str | None = None,
        flat_model_like: str | None = None,
        storey_min: int | None = None,
        storey_max: int | None = None,
        area_min: float | None = None,
        area_max: float | None = None,
        lease_min: float | None = None,
        lease_max: float | None = None,
        top_n: int = 10,
    ) -> str:
        """Generate the formatted table for the buy list.

        The table prioritizes the most undervalued units by sorting on
        `valuation_score` desc, breaking ties by `price_efficiency` asc and
        `resale_price` asc.
        """
        s = self.schema
        self.logger.info("Preparing report (filters: town=%s town_like=%s budget=%s)", town, town_like, budget)

        display = self.generate_dataframe(
            df,
            town=town,
            town_like=town_like,
            budget=budget,
            flat_type=flat_type,
            flat_type_like=flat_type_like,
            flat_model=flat_model,
            flat_model_like=flat_model_like,
            storey_min=storey_min,
            storey_max=storey_max,
            area_min=area_min,
            area_max=area_max,
            lease_min=lease_min,
            lease_max=lease_max,
            top_n=top_n,
        ).copy()

        # Round numeric columns for presentation
        for col, nd in [
            (s.resale_price, 0),
            (s.floor_area, 2),
            (s.remaining_lease_years, 2),
            ("price_per_sqm", 2),
            (s.price_efficiency, 6),
            (s.z_price_efficiency, 3),
            (s.valuation_score, 3),
            ("psm_ratio", 3),
        ]:
            if col in display.columns:
                display[col] = pd.to_numeric(display[col], errors="coerce").round(nd)

        if display.empty:
            return "No results match the given filters or insufficient data to score."

        return display.to_string(index=False)
