"""Financial modeling module for HDB valuation.

This module contains the core valuation logic including:
- Bala's Curve implementation for non-linear lease depreciation
- Feature engineering for price efficiency metrics
- Valuation scoring with growth potential analysis
"""

from __future__ import annotations

import logging
import re
from typing import Any

import numpy as np
import pandas as pd

from hdb_valuation_engine.loader import Schema


class LeaseDepreciationModel:
    """Non-linear lease depreciation model (Bala's Curve Approximation).

    This model implements an economically rigorous depreciation curve for HDB leases,
    recognizing that a 99-year lease does not depreciate linearly. The value holds
    well for the first 30-40 years and then accelerates downward as lease expiry approaches.

    Mathematical Model
    ------------------
    The depreciation factor is computed using a sigmoid-like curve:

        factor = exp(-k * ((99 - remaining) / 99)^n)

    Where:
    - remaining: years of lease remaining
    - k: decay rate parameter (default: 3.0)
    - n: curve steepness (default: 2.5)

    This produces:
    - Factor ≈ 1.0 for remaining > 80 years (minimal depreciation)
    - Factor ≈ 0.8-0.9 for remaining = 50-80 years (moderate depreciation)
    - Factor ≈ 0.3-0.7 for remaining = 20-50 years (accelerating depreciation)
    - Factor ≈ 0.0-0.2 for remaining < 20 years (severe depreciation)

    References
    ----------
    This approximates the observed market behavior described in academic literature
    on HDB lease decay, including Bala's studies on Singapore public housing valuation.
    """

    def __init__(self, max_lease: float = 99.0, decay_rate: float = 3.0, steepness: float = 2.5) -> None:
        """Initialize the lease depreciation model.

        Parameters
        ----------
        max_lease : float
            Maximum lease period in years (default: 99.0 for HDB).
        decay_rate : float
            Controls overall depreciation intensity (higher = more aggressive decay).
        steepness : float
            Controls curve shape (higher = sharper decline near end of lease).
        """
        self.max_lease = max_lease
        self.decay_rate = decay_rate
        self.steepness = steepness
        self.logger = logging.getLogger(self.__class__.__name__)

    def compute_depreciation_factor(self, remaining_years: pd.Series | float) -> pd.Series | float:
        """Compute non-linear depreciation factor for given remaining lease years.

        Parameters
        ----------
        remaining_years : pd.Series | float
            Remaining lease in years (can be Series or scalar).

        Returns
        -------
        pd.Series | float
            Depreciation factor between 0 and 1, where 1 = no depreciation.
        """
        # Handle both Series and scalar inputs
        is_scalar = not isinstance(remaining_years, pd.Series)

        if is_scalar:
            remaining: Any = np.array([remaining_years])
        else:
            remaining = remaining_years.values  # type: ignore[union-attr]

        # Compute normalized age (0 = new, 1 = expired)
        normalized_age = (self.max_lease - np.clip(remaining, 0, self.max_lease)) / self.max_lease

        # Apply non-linear decay curve: exp(-k * age^n)
        with np.errstate(over="ignore", invalid="ignore"):
            factor = np.exp(-self.decay_rate * np.power(normalized_age, self.steepness))

        # Ensure factor is in valid range [0, 1]
        factor = np.clip(factor, 0.0, 1.0)

        # Handle NaN inputs
        factor = np.where(np.isnan(remaining), np.nan, factor)

        if is_scalar:
            return float(factor[0])
        return pd.Series(factor, index=remaining_years.index)  # type: ignore[union-attr]

    def adjust_price_efficiency(self, base_efficiency: pd.Series, remaining_years: pd.Series) -> pd.Series:
        """Adjust price efficiency using non-linear lease depreciation.

        The adjusted efficiency accounts for the non-linear loss of value over time.
        Lower depreciation factors increase the effective price per area-year, making
        properties with shorter leases appear more expensive on a value-adjusted basis.

        Parameters
        ----------
        base_efficiency : pd.Series
            Base price efficiency (price / (area * remaining_years)).
        remaining_years : pd.Series
            Remaining lease years for each property.

        Returns
        -------
        pd.Series
            Lease-adjusted price efficiency.
        """
        factor = self.compute_depreciation_factor(remaining_years)

        # Adjust efficiency: divide by depreciation factor
        # Lower factor (more depreciation) increases the effective price
        with np.errstate(divide="ignore", invalid="ignore"):
            adjusted = base_efficiency / factor

        # Handle edge cases
        return adjusted.mask(~np.isfinite(adjusted), np.nan)


class FeatureEngineer:
    """Engineer features required for valuation.

    Responsibilities
    ---------------
    - Parse remaining lease strings of the form "85 years 3 months" into a float
      in units of years (e.g., 85.25) with robust handling of edge cases.
    - Compute price efficiency as: resale_price / (floor_area_sqm * remaining_lease_years)
    - Apply non-linear lease depreciation adjustment via LeaseDepreciationModel

    Mathematical Notes
    ------------------
    Price efficiency penalizes larger prices per effective area-year. By dividing
    price by both floor area (sqm) and remaining lease (years), the metric
    naturally adjusts for lease decay. The non-linear depreciation model further
    refines this by accounting for the accelerating loss of value as lease expiry approaches.
    """

    _LEASE_YEARS_RE = re.compile(r"(?P<years>\d+)\s*year")
    _LEASE_MONTHS_RE = re.compile(r"(?P<months>\d+)\s*month")

    def __init__(
        self,
        schema: Schema | None = None,
        use_lease_depreciation: bool = True,
        depreciation_model: LeaseDepreciationModel | None = None,
    ) -> None:
        """Initialize FeatureEngineer with optional lease depreciation model.

        Parameters
        ----------
        schema : Schema | None
            Schema definition for column names.
        use_lease_depreciation : bool
            Whether to apply non-linear lease depreciation adjustment (default: True).
        depreciation_model : LeaseDepreciationModel | None
            Custom depreciation model. If None and use_lease_depreciation=True,
            creates default LeaseDepreciationModel.
        """
        self.schema = schema or Schema()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.use_lease_depreciation = use_lease_depreciation
        self.depreciation_model: LeaseDepreciationModel | None

        if use_lease_depreciation:
            self.depreciation_model = depreciation_model or LeaseDepreciationModel()
        else:
            self.depreciation_model = None

    def _parse_lease_text(self, text: str | float | None) -> float | None:
        """Parse a remaining lease string into float years.

        Examples
        --------
        - "85 years 3 months" -> 85.25
        - "99 years" -> 99.0
        - "8 months" -> 0.666...
        - "less than 1 year" -> 0.5 (conservative placeholder)

        Parameters
        ----------
        text : str | float | int | None
            Raw value from the dataset.

        Returns
        -------
        Optional[float]
            Parsed years as float, or None if parsing fails.
        """
        if text is None or (isinstance(text, float) and np.isnan(text)):
            return None

        # If already numeric (rare), accept positive values
        if isinstance(text, (int, float)):
            try:
                val = float(text)
                return val if val >= 0 else None
            except Exception:  # noqa: BLE001
                return None

        s = str(text).strip().lower()
        if s in {"na", "n/a", "nan", "", "none"}:
            return None

        if "less than 1 year" in s:
            # Conservative assumption when qualitative
            return 0.5

        years = 0.0
        months = 0.0

        try:
            y_match = self._LEASE_YEARS_RE.search(s)
            m_match = self._LEASE_MONTHS_RE.search(s)
            if y_match:
                years = float(y_match.group("years"))
            if m_match:
                months = float(m_match.group("months"))
            if years == 0.0 and months == 0.0:
                # Try a pure-number fallback (e.g., "85")
                try:
                    return float(s)
                except Exception:  # noqa: BLE001
                    return None
            return years + months / 12.0
        except Exception:  # noqa: BLE001
            return None

    def _infer_remaining_lease_from_commence(self, df: pd.DataFrame, assumed_lease_years: float = 99.0) -> pd.Series:
        """Infer remaining lease (years) from `lease_commence_date` and `month` columns.

        Mathematics
        -----------
        remaining_years = assumed_lease_years - ((year + month/12) - lease_commence_year)
        where (year, month) come from the transaction month string "YYYY-MM".

        Values are clipped to [0, assumed_lease_years]. Non-parsable rows yield NaN.
        """
        year_month = df.get("month")
        commence = df.get("lease_commence_date")
        out = pd.Series(np.nan, index=df.index, dtype="float64")
        if year_month is None or commence is None:
            return out

        # Coerce commence to numeric year
        commence_year = pd.to_numeric(commence, errors="coerce")

        # Parse year and month from YYYY-MM
        ym = year_month.astype(str).str.strip()
        year = pd.to_numeric(ym.str.slice(0, 4), errors="coerce")
        mon = pd.to_numeric(ym.str.slice(5, 7), errors="coerce")
        frac_year = year + (mon.fillna(1) - 1) / 12.0

        rem = assumed_lease_years - (frac_year - commence_year)
        rem = rem.where(np.isfinite(rem))
        return rem.clip(lower=0.0, upper=assumed_lease_years)

    def parse_remaining_lease(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add a `remaining_lease_years` float column to the DataFrame.

        The method attempts to parse the canonical `remaining_lease` column if
        present. If a numeric-looking `remaining_lease_years` already exists,
        it is respected. If missing, it falls back to inferring from
        (`lease_commence_date`, `month`) assuming a 99-year lease.
        All parsing errors coerce to NaN.

        Parameters
        ----------
        df : pd.DataFrame
            Input dataframe.

        Returns
        -------
        pd.DataFrame
            DataFrame with an added/updated `remaining_lease_years` column.
        """
        col_raw = self.schema.remaining_lease_raw
        col_years = self.schema.remaining_lease_years

        self.logger.info("Parsing remaining lease into years")
        if col_years in df.columns:
            df[col_years] = pd.to_numeric(df[col_years], errors="coerce")
            return df

        parsed: pd.Series | None = None
        if col_raw in df.columns:
            parsed_list: list[float | None] = []
            for val in df[col_raw].tolist():
                try:
                    parsed_list.append(self._parse_lease_text(val))
                except Exception:  # noqa: BLE001
                    parsed_list.append(None)
            parsed = pd.Series(parsed_list, index=df.index, dtype="float64")

        # Fallback inference when parsed is missing or largely NaN
        if parsed is None or parsed.isna().mean() > 0.5:
            self.logger.info("Inferring remaining lease from lease_commence_date and month (99-year assumption)")
            inferred = self._infer_remaining_lease_from_commence(df, assumed_lease_years=99.0)
            parsed = inferred if parsed is None else parsed.fillna(inferred)

        if parsed is None:
            self.logger.warning("No remaining lease information available; creating NaN column")
            df[col_years] = np.nan
        else:
            df[col_years] = pd.to_numeric(parsed, errors="coerce")
        return df

    def compute_price_efficiency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute price efficiency metric with optional non-linear lease depreciation.

        Formula (Base)
        --------------
        price_efficiency = resale_price / (floor_area_sqm * remaining_lease_years)

        Formula (With Depreciation Adjustment)
        ---------------------------------------
        price_efficiency_adjusted = base_efficiency / depreciation_factor(remaining_lease)

        where depreciation_factor ∈ [0, 1] computed via Bala's Curve.

        Interpretation
        --------------
        Lower values indicate better cost per area-year. The non-linear depreciation
        adjustment increases the effective price for properties with shorter leases,
        reflecting the accelerating loss of market value as lease expiry approaches.
        This makes the valuation economically rigorous and market-realistic.
        """
        s = self.schema
        missing = [c for c in [s.resale_price, s.floor_area, s.remaining_lease_years] if c not in df.columns]
        if missing:
            self.logger.error("Missing required columns for price efficiency: %s", missing)
            df[s.price_efficiency] = np.nan
            return df

        self.logger.info("Computing price efficiency (lease depreciation: %s)", self.use_lease_depreciation)

        # Compute base efficiency
        denom = df[s.floor_area] * df[s.remaining_lease_years]
        with np.errstate(divide="ignore", invalid="ignore"):
            base_efficiency = df[s.resale_price] / denom
        base_efficiency = base_efficiency.mask(~np.isfinite(base_efficiency), np.nan)

        # Apply non-linear lease depreciation adjustment if enabled
        if self.use_lease_depreciation and self.depreciation_model is not None:
            self.logger.debug("Applying non-linear lease depreciation adjustment (Bala's Curve)")
            df[s.price_efficiency] = self.depreciation_model.adjust_price_efficiency(
                base_efficiency, df[s.remaining_lease_years]
            )
        else:
            df[s.price_efficiency] = base_efficiency

        return df


class ValuationEngine:
    """Compute group-wise Z-Scores, growth potential, and a final valuation score.

    Methodology
    -----------
    1) Compute Z-Score of `price_efficiency` within groups defined by configurable
       grouping keys (default: (town, flat_type)). The Z-Score is defined as:

           z = (x - mu) / sigma

       where x is the observation's price_efficiency, mu is the group mean,
       and sigma is the group standard deviation. If sigma == 0 or NaN, z is set to 0.

    2) Define Valuation_Score = -Z_Price_Efficiency so that higher scores indicate
       better (cheaper-than-peers) properties.

    3) Compute Growth_Potential metric based on Price-per-Sqm vs Town Average:
       - Deep Value (High Growth): Unit PSM < 0.85 × Town Avg PSM
       - Fair Value (Moderate Growth): 0.85 ≤ Unit PSM < 1.0 × Town Avg PSM
       - Premium (Low Growth): Unit PSM ≥ 1.0 × Town Avg PSM

    This civic value metric identifies properties trading significantly below their
    peer average, suggesting potential for price appreciation or representing
    exceptional value for money.
    """

    def __init__(self, schema: Schema | None = None) -> None:
        self.schema = schema or Schema()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _groupwise_zscore(self, series: pd.Series, groups: pd.Series) -> pd.Series:
        """Compute group-wise Z-Score with robust handling of zero std.

        Parameters
        ----------
        series : pd.Series
            Numeric series to standardize.
        groups : pd.Series
            Group labels of same length as series.

        Returns
        -------
        pd.Series
            Group-wise z-scores with NaN-safe handling; zeros where std is 0 or NaN.
        """
        df = pd.DataFrame({"x": series, "g": groups})
        # Compute mean and std per group using transform for alignment
        means = df.groupby("g")["x"].transform("mean")
        stds = df.groupby("g")["x"].transform("std")

        z = (series - means) / stds
        return z.mask(~np.isfinite(z), 0.0)

    def _compute_growth_potential(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute future appreciation potential based on price-per-sqm vs town average.

        This civic finance heuristic identifies "deep value" properties trading
        significantly below their peer group average, which may indicate:
        1. Undervaluation relative to neighborhood
        2. Higher potential for price appreciation
        3. Exceptional value-for-money opportunities

        The metric uses vectorized pandas operations for performance.

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame with resale_price, floor_area_sqm, town, and flat_type.

        Returns
        -------
        pd.DataFrame
            DataFrame with added columns:
            - price_per_sqm: Unit price per square meter
            - town_avg_psm: Average PSM for (town, flat_type) peer group
            - psm_ratio: Unit PSM / Town Avg PSM
            - growth_potential: Categorical score (High/Moderate/Low)
        """
        s = self.schema

        # Compute price per sqm
        with np.errstate(divide="ignore", invalid="ignore"):
            df["price_per_sqm"] = df[s.resale_price] / df[s.floor_area]
        df["price_per_sqm"] = df["price_per_sqm"].mask(~np.isfinite(df["price_per_sqm"]), np.nan)

        # Compute town + flat_type average PSM using vectorized groupby transform
        group_cols = [s.town, s.flat_type]
        if all(c in df.columns for c in group_cols):
            df["town_avg_psm"] = df.groupby(group_cols)["price_per_sqm"].transform("mean")

            # Compute ratio: unit PSM / average PSM
            with np.errstate(divide="ignore", invalid="ignore"):
                df["psm_ratio"] = df["price_per_sqm"] / df["town_avg_psm"]
            df["psm_ratio"] = df["psm_ratio"].mask(~np.isfinite(df["psm_ratio"]), np.nan)

            # Categorize growth potential using vectorized operations
            # High Growth: PSM < 0.85 × Town Avg (Deep Value)
            # Moderate Growth: 0.85 ≤ PSM < 1.0 × Town Avg (Fair Value)
            # Low Growth: PSM ≥ 1.0 × Town Avg (Premium)
            conditions = [
                df["psm_ratio"] < 0.85,
                (df["psm_ratio"] >= 0.85) & (df["psm_ratio"] < 1.0),
                df["psm_ratio"] >= 1.0,
            ]
            choices = ["High", "Moderate", "Low"]
            df["growth_potential"] = np.select(conditions, choices, default="Unknown")

            self.logger.info("Growth potential computed: %s", df["growth_potential"].value_counts().to_dict())
        else:
            self.logger.warning("Missing columns for growth potential; setting to Unknown")
            df["town_avg_psm"] = np.nan
            df["psm_ratio"] = np.nan
            df["growth_potential"] = "Unknown"

        return df

    def score(self, df: pd.DataFrame, group_by: list[str] | None = None) -> pd.DataFrame:
        """Add Z-Score, Valuation Score, and Growth Potential columns to the DataFrame.

        Adds the following columns:
        - z_price_efficiency: group-wise Z-Score of price_efficiency within selected groups
        - valuation_score: -z_price_efficiency, so higher is more undervalued
        - price_per_sqm: Price per square meter
        - town_avg_psm: Average PSM for peer group (town, flat_type)
        - psm_ratio: Unit PSM / Town Average PSM
        - growth_potential: Categorical (High/Moderate/Low) appreciation potential

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame containing required columns.
        group_by : Optional[List[str]]
            Column names to define peer groups. Defaults to [town, flat_type].

        Returns
        -------
        pd.DataFrame
            DataFrame with added score columns.
        """
        s = self.schema
        default_groups = [s.town, s.flat_type]
        group_cols = group_by or default_groups

        required = group_cols + [s.price_efficiency]
        missing = [c for c in required if c not in df.columns]
        if missing:
            self.logger.error("Missing columns for valuation: %s", missing)
            df[s.z_price_efficiency] = np.nan
            df[s.valuation_score] = np.nan
            return df

        self.logger.info("Computing group-wise z-scores over groups: %s", group_cols)
        # Create tuple keys for groups to allow multiple columns grouping
        groups = list(zip(*[df[c] for c in group_cols], strict=False)) if group_cols else [()] * len(df)
        group_keys = pd.Series(groups, index=df.index, dtype="object")

        z = self._groupwise_zscore(df[s.price_efficiency], group_keys)
        df[s.z_price_efficiency] = z
        df[s.valuation_score] = -z

        # Compute growth potential (civic value metric)
        df = self._compute_growth_potential(df)

        return df
