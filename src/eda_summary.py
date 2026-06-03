from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


PROCESSED_FILE = Path("data/processed/hospital_general_info_clean.csv")
REPORTS_DIR = Path("reports")
FIGURES_DIR = Path("outputs/figures")


def load_data() -> pd.DataFrame:
    """Load the cleaned CMS hospital dataset."""
    if not PROCESSED_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {PROCESSED_FILE}. Run src/clean_data.py first."
        )

    return pd.read_csv(PROCESSED_FILE)


def save_summary_tables(df: pd.DataFrame) -> None:
    """Create CSV summary tables for exploratory analysis."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Missing values report
    missing_values = (
        df.isna()
        .sum()
        .rename_axis("column")
        .reset_index(name="missing_count")
    )

    missing_values["missing_percentage"] = (
        missing_values["missing_count"] / len(df) * 100
    ).round(2)

    missing_values = missing_values.sort_values(
        "missing_count",
        ascending=False
    )

    missing_values.to_csv(
        REPORTS_DIR / "missing_values_report.csv",
        index=False
    )

    # Hospital count by state
    if "state" in df.columns:
        hospitals_by_state = (
            df["state"]
            .value_counts()
            .rename_axis("state")
            .reset_index(name="hospital_count")
            .sort_values("hospital_count", ascending=False)
        )

        hospitals_by_state.to_csv(
            REPORTS_DIR / "hospital_count_by_state.csv",
            index=False
        )

    # Overall rating distribution
    if "hospital_overall_rating" in df.columns:
        rating_distribution = (
            df["hospital_overall_rating"]
            .value_counts(dropna=False)
            .rename_axis("hospital_overall_rating")
            .reset_index(name="hospital_count")
            .sort_values("hospital_overall_rating")
        )

        rating_distribution.to_csv(
            REPORTS_DIR / "overall_rating_distribution.csv",
            index=False
        )

    # Average rating by state
    if {"state", "hospital_overall_rating"}.issubset(df.columns):
        average_rating_by_state = (
            df.dropna(subset=["hospital_overall_rating"])
            .groupby("state", as_index=False)
            .agg(
                average_overall_rating=("hospital_overall_rating", "mean"),
                rated_hospital_count=("hospital_overall_rating", "count")
            )
            .sort_values("average_overall_rating", ascending=False)
        )

        average_rating_by_state["average_overall_rating"] = (
            average_rating_by_state["average_overall_rating"].round(2)
        )

        average_rating_by_state.to_csv(
            REPORTS_DIR / "average_rating_by_state.csv",
            index=False
        )

    # Average rating by hospital type
    if {"hospital_type", "hospital_overall_rating"}.issubset(df.columns):
        average_rating_by_type = (
            df.dropna(subset=["hospital_overall_rating"])
            .groupby("hospital_type", as_index=False)
            .agg(
                average_overall_rating=("hospital_overall_rating", "mean"),
                rated_hospital_count=("hospital_overall_rating", "count")
            )
            .sort_values("average_overall_rating", ascending=False)
        )

        average_rating_by_type["average_overall_rating"] = (
            average_rating_by_type["average_overall_rating"].round(2)
        )

        average_rating_by_type.to_csv(
            REPORTS_DIR / "average_rating_by_hospital_type.csv",
            index=False
        )

    # Average rating by hospital ownership
    if {"hospital_ownership", "hospital_overall_rating"}.issubset(df.columns):
        average_rating_by_ownership = (
            df.dropna(subset=["hospital_overall_rating"])
            .groupby("hospital_ownership", as_index=False)
            .agg(
                average_overall_rating=("hospital_overall_rating", "mean"),
                rated_hospital_count=("hospital_overall_rating", "count")
            )
            .sort_values("average_overall_rating", ascending=False)
        )

        average_rating_by_ownership["average_overall_rating"] = (
            average_rating_by_ownership["average_overall_rating"].round(2)
        )

        average_rating_by_ownership.to_csv(
            REPORTS_DIR / "average_rating_by_ownership.csv",
            index=False
        )

def save_charts(df: pd.DataFrame) -> None:
    """Create simple EDA charts."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Top states by hospital count
    if "state" in df.columns:
        top_states = df["state"].value_counts().head(15)

        plt.figure(figsize=(10, 6))
        top_states.sort_values().plot(kind="barh")
        plt.title("Top 15 States by Number of Hospitals")
        plt.xlabel("Hospital Count")
        plt.ylabel("State")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "top_states_by_hospital_count.png", dpi=300)
        plt.close()

    # Hospital overall rating distribution
    if "hospital_overall_rating" in df.columns:
        rating_counts = (
            df["hospital_overall_rating"]
            .value_counts(dropna=False)
            .sort_index()
        )

        plt.figure(figsize=(8, 5))
        rating_counts.plot(kind="bar")
        plt.title("Hospital Overall Rating Distribution")
        plt.xlabel("Overall Rating")
        plt.ylabel("Hospital Count")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "overall_rating_distribution.png", dpi=300)
        plt.close()

    # Average rating by hospital type
    if {"hospital_type", "hospital_overall_rating"}.issubset(df.columns):
        avg_by_type = (
            df.dropna(subset=["hospital_overall_rating"])
            .groupby("hospital_type")["hospital_overall_rating"]
            .mean()
            .sort_values()
        )

        plt.figure(figsize=(10, 6))
        avg_by_type.plot(kind="barh")
        plt.title("Average Overall Rating by Hospital Type")
        plt.xlabel("Average Overall Rating")
        plt.ylabel("Hospital Type")
        plt.tight_layout()
        plt.savefig(FIGURES_DIR / "average_rating_by_hospital_type.png", dpi=300)
        plt.close()


def main() -> None:
    """Run exploratory analysis workflow."""
    df = load_data()

    print("EDA started.")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    save_summary_tables(df)
    save_charts(df)

    print("EDA complete.")
    print(f"Summary tables saved to: {REPORTS_DIR}")
    print(f"Charts saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()