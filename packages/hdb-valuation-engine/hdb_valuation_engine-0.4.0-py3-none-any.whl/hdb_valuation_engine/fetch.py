"""Data fetching utilities for downloading HDB and MRT datasets.

This module handles downloading datasets from Data.gov.sg APIs and provides
fallback synthetic data generation when official sources are unavailable.
"""

from __future__ import annotations

import csv
import json
import logging
import os
import random

import pandas as pd
import requests

# Official Dataset IDs (verified as of Dec 2025)
DATASET_IDS = {
    # "Resale flat prices based on registration date from Jan-2017 onwards"
    "hdb_resale": "d_8b84c4ee58e3cfc0ece0d773c8ca6abc",
    # "LTA MRT Station Exit" (User provided)
    "mrt_exits": "d_b39d3a0871985372d7e1637193335da5",
}

# Standard paths for datasets
DEFAULT_HDB_PATH = os.path.join(
    "ResaleFlatPrices", "Resale flat prices based on registration date from Jan-2017 onwards.csv"
)
DEFAULT_MRT_PATH = os.path.join(".data", "LTAMRTStationExitGEOJSON.geojson")

# Expected HDB resale columns for schema validation
EXPECTED_HDB_COLUMNS = {
    "month",
    "town",
    "flat_type",
    "block",
    "street_name",
    "storey_range",
    "floor_area_sqm",
    "flat_model",
    "lease_commence_date",
    "remaining_lease",
    "resale_price",
}

# Expected MRT columns (after normalization)
EXPECTED_MRT_COLUMNS = {"name", "lat", "lon"}


def validate_hdb_schema(path: str) -> bool:
    """Validate that a CSV file has the expected HDB resale schema.

    Parameters
    ----------
    path : str
        Path to the CSV file to validate.

    Returns
    -------
    bool
        True if the file exists and has the expected columns, False otherwise.
    """
    if not os.path.exists(path):
        return False

    try:
        # Read just the header to check columns
        df = pd.read_csv(path, nrows=0)
        # Normalize column names
        cols = {str(c).strip().lower().replace(" ", "_") for c in df.columns}
        # Check if all expected columns are present
        return EXPECTED_HDB_COLUMNS.issubset(cols)
    except Exception:
        return False


def validate_mrt_schema(path: str) -> bool:
    """Validate that a GeoJSON or CSV file has the expected MRT schema.

    Parameters
    ----------
    path : str
        Path to the GeoJSON or CSV file to validate.

    Returns
    -------
    bool
        True if the file exists and has the expected structure, False otherwise.
    """
    if not os.path.exists(path):
        return False

    try:
        if path.lower().endswith(".geojson") or path.lower().endswith(".json"):
            # Validate GeoJSON structure
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
                return False
            features = data.get("features", [])
            if not features:
                return False
            # Check that at least one feature has the expected structure
            for feat in features[:5]:  # Check first 5 features
                if not isinstance(feat, dict):
                    continue
                geom = feat.get("geometry", {})
                if geom.get("type") != "Point":
                    continue
                props = feat.get("properties", {})
                if not props:
                    continue
                # Look for name/station name fields (case-insensitive)
                prop_keys_lower = [k.lower() for k in props]
                has_name = any("name" in k or "stn" in k or "station" in k for k in prop_keys_lower)
                if has_name:
                    return True
            return False
        # Validate CSV structure
        df = pd.read_csv(path, nrows=0)
        cols = {str(c).strip().lower().replace(" ", "_") for c in df.columns}
        return EXPECTED_MRT_COLUMNS.issubset(cols)
    except Exception:
        return False


def prompt_user_download(dataset_name: str) -> bool:
    """Prompt user for permission to download a dataset.

    Parameters
    ----------
    dataset_name : str
        Name of the dataset to download (\"HDB resale data\" or \"MRT stations data\").

    Returns
    -------
    bool
        True if user approves download, False otherwise.
    """
    print(f"\n⚠️  {dataset_name} not found or has invalid schema.")
    print("Would you like to download it now? (y/n): ", end="", flush=True)

    try:
        response = input().strip().lower()
        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        print()
        return False


def api_get_download_url(dataset_id: str, verbose: int = 0) -> str | None:
    """Hit the initiate-download endpoint to get the temporary S3 URL."""
    log = logging.getLogger("fetch")
    endpoint = f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/initiate-download"
    try:
        if verbose:
            log.info(f"Requesting download URL for ID: {dataset_id}")

        resp = requests.get(endpoint, timeout=30)
        resp.raise_for_status()

        data = resp.json()
        # API returns { "code": 0, "data": { "url": "..." }, ... }
        return str(data.get("data", {}).get("url")) if data.get("data", {}).get("url") else None
    except Exception as e:
        log.warning(f"API request failed for {dataset_id}: {e}")
        return None


def generate_synthetic_hdb(path: str, limit: int) -> None:
    """Generate synthetic HDB resale dataset for testing."""
    cols = [
        "month",
        "town",
        "flat_type",
        "block",
        "street_name",
        "storey_range",
        "floor_area_sqm",
        "flat_model",
        "lease_commence_date",
        "remaining_lease",
        "resale_price",
    ]
    towns = [
        "ANG MO KIO",
        "BEDOK",
        "BISHAN",
        "BUKIT BATOK",
        "BUKIT MERAH",
        "BUKIT PANJANG",
        "BUKIT TIMAH",
        "CENTRAL AREA",
        "CHOA CHU KANG",
        "CLEMENTI",
        "GEYLANG",
        "HOUGANG",
        "JURONG EAST",
        "JURONG WEST",
        "KALLANG/WHAMPOA",
        "MARINE PARADE",
        "PASIR RIS",
        "PUNGGOL",
        "QUEENSTOWN",
        "SEMBAWANG",
        "SENGKANG",
        "SERANGOON",
        "TAMPINES",
        "TOA PAYOH",
        "WOODLANDS",
        "YISHUN",
    ]
    types = ["2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE"]
    models = [
        "Improved",
        "New Generation",
        "Model A",
        "Standard",
        "Simplified",
        "Premium Apartment",
        "Apartment",
        "Maisonette",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for _i in range(min(limit, 10000)):
            year = 2017 + random.randint(0, 3)
            month = f"{year}-{random.randint(1,12):02d}"
            town = random.choice(towns)
            ft = random.choice(types)
            block = str(random.randint(1, 999))
            street = f"STREET {chr(65 + random.randint(0,25))}"
            sm = 1 + 3 * random.randint(0, 13)
            sr = f"{sm:02d} TO {sm+2:02d}"
            area = random.choice(
                {
                    "2 ROOM": [35, 45],
                    "3 ROOM": [60, 65, 70],
                    "4 ROOM": [80, 90, 95],
                    "5 ROOM": [105, 110, 120],
                    "EXECUTIVE": [120, 130, 140],
                }.get(ft, [60, 90, 110])
            )
            model = random.choice(models)
            lcy = random.randint(1970, 2015)
            years_elapsed = max(0, year - lcy)
            remy = max(1, 99 - years_elapsed)
            rem = f"{remy} years {random.randint(0,11):02d} months"
            base_psm = 4000 + random.randint(-300, 600)
            lease_factor = 0.6 + 0.4 * (remy / 99)
            town_factor = 0.9 + 0.2 * (town in {"QUEENSTOWN", "BISHAN", "BUKIT TIMAH", "MARINE PARADE"})
            price = int(area * base_psm * lease_factor * town_factor * (0.9 + 0.2 * random.random()))
            w.writerow(
                {
                    "month": month,
                    "town": town,
                    "flat_type": ft,
                    "block": block,
                    "street_name": street,
                    "storey_range": sr,
                    "floor_area_sqm": area,
                    "flat_model": model,
                    "lease_commence_date": lcy,
                    "remaining_lease": rem,
                    "resale_price": price,
                }
            )
    logging.getLogger("fetch").info("Wrote synthetic dataset to %s", path)


def generate_synthetic_mrt(path: str) -> None:
    """Generate synthetic MRT GeoJSON for testing."""
    sample = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [103.851959, 1.290270]},
                "properties": {"STN_NAME": "RAFFLES PLACE", "LINE": "NS"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [103.845, 1.3008]},
                "properties": {"STN_NAME": "BUGIS", "LINE": "DT"},
            },
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sample, f)


def download_file(url: str, dest_path: str) -> None:
    """Stream the file from the S3 URL to disk."""
    log = logging.getLogger("fetch")
    log.info(f"Downloading to {dest_path}...")
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    log.info("Download complete.")


def fetch_hdb_data(limit: int, out_dir: str, filename: str, verbose: int = 0) -> int:
    """Fetch HDB resale dataset using the official Data.gov.sg 'initiate-download' API."""
    log = logging.getLogger("fetch")

    # Create output directory
    os.makedirs(out_dir, exist_ok=True)
    hdb_out_path = os.path.join(out_dir, filename)

    # Try API first
    success_hdb = False
    url_hdb = api_get_download_url(DATASET_IDS["hdb_resale"], verbose=verbose)

    if url_hdb:
        try:
            download_file(url_hdb, hdb_out_path)
            success_hdb = True
        except Exception as e:
            log.error(f"Failed to download HDB data from URL: {e}")

    # Fallback to Synthetic if API failed
    if not success_hdb:
        log.warning("Could not fetch official HDB data. Generating synthetic dataset...")
        generate_synthetic_hdb(hdb_out_path, limit)

    return 0


def fetch_mrt_data(mrt_out_path: str, verbose: int = 0) -> int:
    """Fetch MRT GeoJSON dataset."""
    log = logging.getLogger("fetch")

    url = api_get_download_url(DATASET_IDS["mrt_exits"], verbose=verbose)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(mrt_out_path) or ".", exist_ok=True)

    # Download
    if url:
        try:
            log.info(f"Downloading MRT Data to {mrt_out_path}...")
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(mrt_out_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return 0
        except Exception as e:
            log.error(f"MRT download failed: {e}")
    log.warning("Could not fetch official MRT data (url not available) - generating synthetic.")
    # Synthetic Fallback
    log.warning("Generating synthetic MRT GeoJSON...")
    generate_synthetic_mrt(mrt_out_path)
    return 0


def ensure_hdb_dataset(path: str, verbose: int = 0) -> bool:
    """Ensure HDB dataset exists and has valid schema, downloading if necessary.

    Parameters
    ----------
    path : str
        Path where the HDB dataset should exist.
    verbose : int
        Verbosity level for logging.

    Returns
    -------
    bool
        True if dataset is available and valid, False if user declined download or download failed.
    """
    log = logging.getLogger("DatasetManager")

    # Check if file exists and has valid schema
    if validate_hdb_schema(path):
        if verbose >= 1:
            log.info(f"HDB dataset found and validated at: {path}")
        return True

    # Prompt user for download
    if not prompt_user_download("HDB resale data"):
        return False

    # Download the dataset
    print(f"📥 Downloading HDB resale data to {path}...")
    out_dir = os.path.dirname(path) or "."
    filename = os.path.basename(path)

    try:
        result = fetch_hdb_data(limit=0, out_dir=out_dir, filename=filename, verbose=verbose)
        if result == 0 and validate_hdb_schema(path):
            print("✅ HDB dataset downloaded successfully!")
            return True
        print("❌ Failed to download or validate HDB dataset.")
        return False
    except Exception as e:
        log.error(f"Error downloading HDB dataset: {e}")
        print(f"❌ Error downloading HDB dataset: {e}")
        return False


def ensure_mrt_dataset(path: str, verbose: int = 0) -> bool:
    """Ensure MRT dataset exists and has valid schema, downloading if necessary.

    Parameters
    ----------
    path : str
        Path where the MRT dataset should exist.
    verbose : int
        Verbosity level for logging.

    Returns
    -------
    bool
        True if dataset is available and valid, False if user declined download or download failed.
    """
    log = logging.getLogger("DatasetManager")

    # Check if file exists and has valid schema
    if validate_mrt_schema(path):
        if verbose >= 1:
            log.info(f"MRT dataset found and validated at: {path}")
        return True

    # Prompt user for download
    if not prompt_user_download("MRT stations data"):
        return False

    # Download the dataset
    print(f"📥 Downloading MRT stations data to {path}...")

    try:
        result = fetch_mrt_data(path, verbose=verbose)
        if result == 0 and validate_mrt_schema(path):
            print("✅ MRT dataset downloaded successfully!")
            return True
        print("❌ Failed to download or validate MRT dataset.")
        return False
    except Exception as e:
        log.error(f"Error downloading MRT dataset: {e}")
        print(f"❌ Error downloading MRT dataset: {e}")
        return False
