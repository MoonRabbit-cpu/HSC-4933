#####################################################
# Bryan Hernandez Rodriguez                         #
# AI_code_clean.py: AI code debug                   #
#####################################################

#!/usr/bin/env python3
"""
Clean healthcare_dataset.csv, compute summary statistics with NumPy, pseudonymize
patient names, and encrypt the complete cleaned dataset with Fernet.

Install:
    pip install pandas numpy cryptography

Run:
    python clean_encrypt_healthcare.py --input healthcare_dataset.csv --outdir secure_output

Security notes:
- The encrypted CSV is the deliverable containing all cleaned patient records.
- The key file is highly sensitive. Store it separately from the encrypted data,
  restrict access, and back it up securely. Anyone with the key can decrypt the data.
- Replacing names with IDs is pseudonymization, not guaranteed anonymization:
  other fields may still permit re-identification.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import stat
from pathlib import Path

import numpy as np
import pandas as pd
from cryptography.fernet import Fernet


DATE_COLUMNS = ["Date of Admission", "Discharge Date"]
REQUIRED_COLUMNS = [
    "Name", "Age", "Gender", "Blood Type", "Medical Condition",
    "Date of Admission", "Doctor", "Hospital", "Insurance Provider",
    "Billing Amount", "Room Number", "Admission Type", "Discharge Date",
    "Medication", "Test Results",
]


def load_or_create_key(key_path: Path) -> bytes:
    """Load an existing Fernet key or create one without overwriting an existing key."""
    key_path.parent.mkdir(parents=True, exist_ok=True)
    if key_path.exists():
        key = key_path.read_bytes().strip()
        # Validate key early; Fernet raises ValueError for malformed keys.
        Fernet(key)
        return key

    key = Fernet.generate_key()
    fd = os.open(str(key_path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(key + b"\n")
    try:
        os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    return key


def canonical_case(s: pd.Series) -> pd.Series:
    """Collapse whitespace and map case-variants to their most common spelling."""
    s = s.astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
    key = s.str.casefold()
    best = (
        pd.DataFrame({"key": key, "val": s}).dropna()
        .groupby(["key", "val"]).size().reset_index(name="n")
        .sort_values("n", ascending=False)
        .drop_duplicates("key")
        .set_index("key")["val"]
    )
    return key.map(best).astype("string")





def clean_data(input_path: Path) -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(input_path, low_memory=False)
    original_rows = len(df)
    original_columns = list(df.columns)

    df.columns = [str(c).strip() for c in df.columns]
    missing_columns = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_columns:
        raise ValueError("Input file is missing expected columns: " + ", ".join(missing_columns))

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()
        df[col] = df[col].replace("", pd.NA)

    # --- Numeric fields (count unparseable AND out-of-range separately) ---
    def to_numeric(col):
        raw = df[col]
        coerced = pd.to_numeric(raw, errors="coerce")
        unparseable = int((raw.notna() & coerced.isna()).sum())
        return coerced, unparseable

    df["Age"], unparseable_age = to_numeric("Age")
    invalid_age = df["Age"].notna() & ~df["Age"].between(0, 120)
    df.loc[invalid_age, "Age"] = np.nan
    df["Age"] = df["Age"].round().astype("Int64")

    df["Billing Amount"], unparseable_billing = to_numeric("Billing Amount")
    invalid_billing = df["Billing Amount"].notna() & (
        ~np.isfinite(df["Billing Amount"]) | (df["Billing Amount"] < 0)
    )
    df.loc[invalid_billing, "Billing Amount"] = np.nan

    df["Room Number"], unparseable_room = to_numeric("Room Number")
    invalid_room = df["Room Number"].notna() & (
        (df["Room Number"] < 0) | (df["Room Number"] % 1 != 0)
    )
    df.loc[invalid_room, "Room Number"] = np.nan
    df["Room Number"] = df["Room Number"].astype("Int64")

    # --- Dates (count unparseable) ---
    unparseable_dates = {}
    for col in DATE_COLUMNS:
        raw = df[col]
        df[col] = pd.to_datetime(raw, errors="coerce")
        unparseable_dates[col] = int((raw.notna() & df[col].isna()).sum())

    invalid_date_order = (
        df["Date of Admission"].notna()
        & df["Discharge Date"].notna()
        & (df["Discharge Date"] < df["Date of Admission"])
    )
    invalid_date_order_count = int(invalid_date_order.sum())
    df.loc[invalid_date_order, "Discharge Date"] = pd.NaT

    # --- Normalize text BEFORE deduplication ---
    df["Blood Type"] = df["Blood Type"].str.upper()
    # Names are pseudonymized later, so mangled casing doesn't matter,
    # but normalizing lets "bOb" and "Bob" duplicates be caught.
    df["Name"] = df["Name"].str.replace(r"\s+", " ", regex=True).str.title()
    for col in ["Gender", "Medical Condition", "Admission Type", "Test Results"]:
        df[col] = df[col].str.replace(r"\s+", " ", regex=True).str.title()
    for col in ["Insurance Provider", "Medication", "Doctor", "Hospital"]:
        df[col] = canonical_case(df[col])

    # --- Deduplicate on the normalized data ---
    rows_before_dedup = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    duplicates_removed = rows_before_dedup - len(df)

    report = {
        "input_file": input_path.name,
        "original_rows": int(original_rows),
        "rows_after_cleaning": int(len(df)),
        "duplicates_removed": int(duplicates_removed),
        "unparseable_age_values_set_missing": unparseable_age,
        "unparseable_billing_values_set_missing": unparseable_billing,
        "unparseable_room_numbers_set_missing": unparseable_room,
        "unparseable_dates_set_missing": unparseable_dates,
        "invalid_age_values_set_missing": int(invalid_age.sum()),
        "invalid_billing_values_set_missing": int(invalid_billing.sum()),
        "invalid_room_numbers_set_missing": int(invalid_room.sum()),
        "invalid_date_order_discharge_dates_set_missing": invalid_date_order_count,
        "columns_in_input": original_columns,
        "missing_values_by_column": {str(k): int(v) for k, v in df.isna().sum().items()},
    }
    return df, report


def add_patient_ids(df: pd.DataFrame, key: bytes) -> pd.DataFrame:
    """Replace names with keyed, stable pseudonymous IDs."""
    from cryptography.fernet import Fernet  # validates key format
    Fernet(key)

    # Derive an HMAC key from the Fernet key material. IDs are deterministic for
    # a given key; never publish the key or the ID mapping.
    import hashlib
    import hmac

    hmac_key = base64.urlsafe_b64decode(key)
    result = df.copy()
    names = result["Name"].fillna("UNKNOWN").astype(str)
    # Include the row position so different records for people with the same
    # name do not automatically receive the same pseudonymous ID. IDs are
    # stable only while the cleaned row order and key remain unchanged.
    result["Patient_ID"] = [
        hmac.new(
            hmac_key, f"{i}|{name.casefold()}".encode("utf-8"), hashlib.sha256
        ).hexdigest()[:20]
        for i, name in enumerate(names.tolist())
    ]
    result = result.drop(columns=["Name"])
    # Put the pseudonymous identifier first.
    cols = ["Patient_ID"] + [c for c in result.columns if c != "Patient_ID"]
    return result[cols]


def make_statistics(df: pd.DataFrame, cleaning_report: dict) -> dict:
    """Return aggregate statistics; do not include row-level patient data."""
    stats = dict(cleaning_report)

    def numeric_summary(series: pd.Series) -> dict:
        values = pd.to_numeric(series, errors="coerce").dropna().to_numpy(dtype=float)
        if values.size == 0:
            return {
                "n": 0, "mean": None, "median": None, "std_population": None,
                "min": None, "max": None, "q1": None, "q3": None,
            }
        return {
            "n": int(values.size),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std_population": float(np.std(values, ddof=0)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "q1": float(np.percentile(values, 25)),
            "q3": float(np.percentile(values, 75)),
        }

    stats["age"] = numeric_summary(df["Age"])
    stats["billing_amount"] = numeric_summary(df["Billing Amount"])
    stats["category_counts"] = {}
    for col in [
        "Gender", "Blood Type", "Medical Condition", "Insurance Provider",
        "Admission Type", "Medication", "Test Results",
    ]:
        stats["category_counts"][col] = {
            str(k): int(v) for k, v in
            df[col].value_counts(dropna=False).items()
        }

    valid_dates = df["Date of Admission"].notna() & df["Discharge Date"].notna()
    if valid_dates.any():
        stay_days = (
            df.loc[valid_dates, "Discharge Date"]
            - df.loc[valid_dates, "Date of Admission"]
        ).dt.total_seconds().to_numpy(dtype=float) / 86400.0
        stats["length_of_stay_days"] = numeric_summary(pd.Series(stay_days))
    else:
        stats["length_of_stay_days"] = numeric_summary(pd.Series(dtype=float))

    return stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("healthcare_dataset.csv"))
    parser.add_argument("--outdir", type=Path, default=Path("secure_output"))
    parser.add_argument(
        "--key-file", type=Path, default=None,
        help="Path to Fernet key. Defaults to OUTDIR/fernet.key.",
    )
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Input file not found: {args.input}")

    args.outdir.mkdir(parents=True, exist_ok=True)
    key_path = args.key_file or (args.outdir / "fernet.key")
    key = load_or_create_key(key_path)

    cleaned, cleaning_report = clean_data(args.input)
    stats = make_statistics(cleaned, cleaning_report)
    pseudonymized = add_patient_ids(cleaned, key)

    # Serialize the entire cleaned dataset to CSV in memory, then encrypt all bytes.
    # No plaintext patient CSV is written to disk.
    plaintext_csv = pseudonymized.to_csv(index=False, date_format="%Y-%m-%d").encode("utf-8")
    encrypted_bytes = Fernet(key).encrypt(plaintext_csv)
    encrypted_path = args.outdir / "patient_data.csv.fernet"
    encrypted_path.write_bytes(encrypted_bytes)
    try:
        os.chmod(encrypted_path, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass

    stats_path = args.outdir / "summary_statistics.json"
    stats_path.write_text(json.dumps(stats, indent=2, allow_nan=False), encoding="utf-8")

    print(f"Rows read: {cleaning_report['original_rows']:,}")
    print(f"Rows retained: {len(pseudonymized):,}")
    print(f"Exact duplicates removed: {cleaning_report['duplicates_removed']:,}")
    print(f"Encrypted patient data: {encrypted_path}")
    print(f"Aggregate statistics: {stats_path}")
    print(f"Fernet key: {key_path}")
    print("\nIMPORTANT: move the key to a separate, access-controlled location and back it up.")
    print("Do not email, commit, or upload the key alongside the encrypted data.")


if __name__ == "__main__":
    main()
