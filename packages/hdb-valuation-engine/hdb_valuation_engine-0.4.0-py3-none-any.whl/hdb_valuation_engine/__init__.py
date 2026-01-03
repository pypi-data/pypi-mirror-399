# Package initializer for hdb_valuation_engine
"""
HDB Valuation Engine - A Python library for analyzing Singapore HDB resale properties.

This package provides both a CLI tool and a programmatic API for identifying undervalued
HDB properties using lease-adjusted price efficiency metrics and group-wise z-scores.

Quick Start (Module Usage)
---------------------------
>>> from hdb_valuation_engine import HDBValuationEngineApp
>>>
>>> app = HDBValuationEngineApp()
>>> results = app.process(
...     input_path="resale.csv",
...     town="PUNGGOL",
...     budget=600000,
...     top_n=10
... )
>>> print(results)

Quick Start (Individual Components)
------------------------------------
>>> from hdb_valuation_engine import HDBLoader, FeatureEngineer, ValuationEngine
>>>
>>> loader = HDBLoader()
>>> df = loader.load("resale.csv")
>>>
>>> engineer = FeatureEngineer()
>>> df = engineer.parse_remaining_lease(df)
>>> df = engineer.compute_price_efficiency(df)
>>>
>>> engine = ValuationEngine()
>>> df = engine.score(df)
>>> print(df[['town', 'flat_type', 'valuation_score']].head())

Main Classes
------------
- HDBValuationEngineApp : High-level orchestrator for the complete pipeline
- HDBLoader : Load and normalize HDB resale CSV data
- FeatureEngineer : Parse remaining lease and compute price efficiency
- LeaseDepreciationModel : Bala's Curve implementation for lease depreciation
- ValuationEngine : Compute group-wise z-scores and valuation scores
- TransportScorer : Calculate MRT accessibility scores
- ReportGenerator : Filter, rank, and format results
- Schema : Column name definitions for the pipeline
"""

# Import from new modular structure
from hdb_valuation_engine.cli import HDBValuationEngineApp, build_parser, main
from hdb_valuation_engine.loader import HDBLoader, Schema
from hdb_valuation_engine.models import (
    FeatureEngineer,
    LeaseDepreciationModel,
    ValuationEngine,
)
from hdb_valuation_engine.reporter import ReportGenerator
from hdb_valuation_engine.spatial import TransportScorer
from hdb_valuation_engine.utils import __version__, configure_logging

__all__ = [
    # Main application
    "HDBValuationEngineApp",
    "main",
    "build_parser",
    # Core classes
    "HDBLoader",
    "FeatureEngineer",
    "LeaseDepreciationModel",
    "ValuationEngine",
    "TransportScorer",
    "ReportGenerator",
    # Schema and utilities
    "Schema",
    "configure_logging",
    # Version
    "__version__",
]
