from pathlib import Path

import pandas as pd


RAW_FILE = Path("data/raw/hospital_general_info.csv")
PROCESSED_DIR = Path("data/processed")
PROCESSED_FILE = PROCESSED_DIR / "hospital_general_info_clean.csv"


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Convert column names to lowercase snake_case."""
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("/", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
        .str.replace("__", "_", regex=False)
    )

    return df


def clean_hospital_data() -> None:
    """Clean the CMS hospital general information dataset."""
    print("Loading raw hospital data...")
    df = pd.read_csv(RAW_FILE)

    print(f"Original shape: {df.shape[0]:,} rows x {df.shape[1]:,} columns")

    # Clean column names
    df = clean_column_names(df)

    # Standardize missing values
    df = df.replace(
        {
            "Not Available": pd.NA,
            "Not Applicable": pd.NA,
            "None": pd.NA,
            "": pd.NA,
        }
    )

    # Keep ID-style columns as text
    id_columns = ["facility_id", "zip_code", "telephone_number", "phone_number"]

    for col in id_columns:
        if col in df.columns:
            df[col] = df[col].astype("string")

    # Convert rating to numeric
    if "hospital_overall_rating" in df.columns:
        df["hospital_overall_rating"] = pd.to_numeric(
            df["hospital_overall_rating"],
            errors="coerce"
        )

    # Remove exact duplicate rows
    duplicate_count = df.duplicated().sum()
    df = df.drop_duplicates()

    # Create processed folder if needed
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save cleaned data
    df.to_csv(PROCESSED_FILE, index=False)

    print(f"Removed {duplicate_count:,} duplicate rows")
    print(f"Cleaned shape: {df.shape[0]:,} rows x {df.shape[1]:,} columns")
    print(f"Saved cleaned data to: {PROCESSED_FILE}")

    print("\nFirst 10 cleaned columns:")
    for col in df.columns[:10]:
        print(f"- {col}")

    print("\nMissing values by column:")
    missing_values = df.isna().sum()
    missing_values = missing_values[missing_values > 0].sort_values(ascending=False)

    if missing_values.empty:
        print("No missing values found.")
    else:
        print(missing_values)


if __name__ == "__main__":
    clean_hospital_data()