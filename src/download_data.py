from pathlib import Path

import pandas as pd
import requests


DATASET_ID = "xubh-q36u"

METADATA_URL = (
    "https://data.cms.gov/provider-data/api/1/metastore/schemas/"
    f"dataset/items/{DATASET_ID}?show-reference-ids=false"
)

RAW_DIR = Path("data/raw")
RAW_FILE = RAW_DIR / "hospital_general_info.csv"


def get_csv_download_url() -> str:
    """Get the current CSV download URL from CMS metadata."""
    print("Fetching CMS metadata...")

    response = requests.get(METADATA_URL, timeout=30)
    response.raise_for_status()

    metadata = response.json()

    for item in metadata.get("distribution", []):
        data = item.get("data", item)
        download_url = data.get("downloadURL")
        media_type = data.get("mediaType", "")

        if download_url and "csv" in media_type.lower():
            return download_url

    raise ValueError("Could not find a CSV download URL in the CMS metadata.")


def download_hospital_data() -> None:
    """Download CMS hospital data and save it locally."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    csv_url = get_csv_download_url()

    print("Downloading CMS hospital data...")
    df = pd.read_csv(csv_url)

    df.to_csv(RAW_FILE, index=False)

    print(f"Saved {len(df):,} rows to {RAW_FILE}")
    print(f"Dataset shape: {df.shape[0]:,} rows x {df.shape[1]:,} columns")

    print("\nFirst 10 columns:")
    for col in df.columns[:10]:
        print(f"- {col}")


if __name__ == "__main__":
    download_hospital_data()