
import pandas as pd

# Load the original CSV files
facilities = pd.read_csv("data/raw/facilities_master.csv")
population = pd.read_csv("data/raw/population_state.csv")
beds = pd.read_csv("data/raw/hospital_beds.csv")

# Display dataset sizes
print("Facilities:", facilities.shape)
print("Population:", population.shape)
print("Hospital beds:", beds.shape)

# Display column names
print("\nFacilities columns:")
print(facilities.columns.tolist())

print("\nPopulation columns:")
print(population.columns.tolist())

print("\nHospital beds columns:")
print(beds.columns.tolist())

# Check missing values
print("\nFacilities missing values:")
print(facilities.isnull().sum())

print("\nPopulation missing values:")
print(population.isnull().sum())

print("\nHospital beds missing values:")
print(beds.isnull().sum())


# STEP 3: Inspect facilities dataset

print("\n===== FACILITY STATUS =====")
print(facilities["STATUS"].value_counts(dropna=False))

print("\n===== FACILITY SECTORS =====")
print(facilities["SEKTOR"].value_counts(dropna=False))

print("\n===== FACILITY CATEGORIES =====")
print(facilities["KATEGORI_FASILITI"].value_counts(dropna=False))

print("\n===== FACILITY TYPES =====")
print(facilities["JENIS_FASILITI"].value_counts(dropna=False))

print("\n===== STATES =====")
print(facilities["NEGERI"].value_counts(dropna=False))

print("\n===== DUPLICATE FACILITY CODES =====")
print(facilities["KOD_FASILITI"].duplicated().sum())

print("\n===== COORDINATE SUMMARY =====")
print(facilities[["LATITUD", "LONGITUD"]].describe())

print("\n===== SAMPLE FACILITIES =====")
print(facilities[[
    "KOD_FASILITI",
    "STATUS",
    "NEGERI",
    "KATEGORI_FASILITI",
    "NAMA",
    "LATITUD",
    "LONGITUD"
]].head(10).to_string(index=False))


# STEP 4: Investigate problematic facility records

# Identify coordinates outside a broad Malaysia bounding box
invalid_coordinates = facilities[
    ~(
        facilities["LATITUD"].between(0.5, 8.0) &
        facilities["LONGITUD"].between(99.0, 120.0)
    )
]

print("\n===== SUSPICIOUS COORDINATES =====")
print("Total:", len(invalid_coordinates))

print(
    invalid_coordinates[
        ["KOD_FASILITI", "NEGERI", "NAMA",
         "LATITUD", "LONGITUD"]
    ].to_string(index=False)
)

# Investigate combined Kuala Lumpur / Putrajaya records
combined_state = facilities[
    facilities["NEGERI"] ==
    "WILAYAH PERSEKUTUAN KUALA LUMPUR DAN PUTRAJAYA"
]

print("\n===== COMBINED STATE RECORDS =====")
print(
    combined_state[
        ["KOD_FASILITI", "NAMA", "ALAMAT",
         "LATITUD", "LONGITUD"]
    ].to_string(index=False)
)

# Check whether different facilities share coordinates
duplicate_coordinates = facilities[
    facilities.duplicated(
        subset=["LATITUD", "LONGITUD"],
        keep=False
    )
]

print("\n===== SHARED COORDINATES =====")
print("Total records:", len(duplicate_coordinates))

print(
    duplicate_coordinates[
        ["KOD_FASILITI", "NAMA", "LATITUD", "LONGITUD"]
    ].head(20).to_string(index=False)
)


# STEP 5: Clean facilities data

from pathlib import Path

# Work on a copy to preserve the original data
facilities_clean = facilities.copy()

# Remove columns not needed for our visualisations
columns_to_keep = [
    "KOD_FASILITI",
    "STATUS",
    "SEKTOR",
    "NEGERI",
    "DAERAH",
    "KATEGORI_FASILITI",
    "JENIS_FASILITI",
    "NAMA",
    "ALAMAT",
    "LATITUD",
    "LONGITUD"
]

facilities_clean = facilities_clean[columns_to_keep].copy()

# Clean whitespace and line breaks in text columns
text_columns = [
    "NEGERI", "DAERAH", "KATEGORI_FASILITI",
    "JENIS_FASILITI", "NAMA", "ALAMAT"
]

for col in text_columns:
    facilities_clean[col] = (
        facilities_clean[col]
        .astype("string")
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

# Standardise combined KL/Putrajaya geographical labels
combined = (
    facilities_clean["NEGERI"] ==
    "WILAYAH PERSEKUTUAN KUALA LUMPUR DAN PUTRAJAYA"
)

putrajaya_code = "91-16010001"

facilities_clean.loc[
    combined & (
        facilities_clean["KOD_FASILITI"] == putrajaya_code
    ),
    "NEGERI"
] = "WILAYAH PERSEKUTUAN PUTRAJAYA"

facilities_clean.loc[
    combined & (
        facilities_clean["KOD_FASILITI"] != putrajaya_code
    ),
    "NEGERI"
] = "WILAYAH PERSEKUTUAN KUALA LUMPUR"

# Convert coordinates to numeric values
facilities_clean["LATITUD"] = pd.to_numeric(
    facilities_clean["LATITUD"], errors="coerce"
)

facilities_clean["LONGITUD"] = pd.to_numeric(
    facilities_clean["LONGITUD"], errors="coerce"
)

# Flag coordinates outside the broad Malaysia bounding box
valid_coordinates = (
    facilities_clean["LATITUD"].between(0.5, 8.0)
    & facilities_clean["LONGITUD"].between(99.0, 120.0)
)

# Preserve all records, but mark coordinate validity
facilities_clean["VALID_COORDINATES"] = valid_coordinates

# Save the cleaned dataset
Path("data/cleaned").mkdir(parents=True, exist_ok=True)

facilities_clean.to_csv(
    "data/cleaned/facilities_cleaned.csv",
    index=False
)

# Save a separate dataset for mapping
facilities_map = facilities_clean[
    facilities_clean["VALID_COORDINATES"]
].copy()

facilities_map.to_csv(
    "data/cleaned/facilities_map.csv",
    index=False
)

print("\n===== STEP 5 RESULTS =====")
print("Total cleaned facilities:", len(facilities_clean))
print("Map-ready facilities:", len(facilities_map))
print("Excluded from map:", len(facilities_clean) - len(facilities_map))
print("Unique state labels:", facilities_clean["NEGERI"].nunique())


# STEP 6: Inspect population dataset

print("\n===== POPULATION DATE RANGE =====")
print("Earliest:", population["date"].min())
print("Latest:", population["date"].max())

print("\n===== SEX CATEGORIES =====")
print(population["sex"].unique())

print("\n===== AGE CATEGORIES =====")
print(population["age"].unique())

print("\n===== ETHNICITY CATEGORIES =====")
print(population["ethnicity"].unique())

print("\n===== STATE NAMES =====")
print(population["state"].unique())

print("\n===== POPULATION SAMPLE =====")
print(population.head(15).to_string(index=False))

print("\n===== POPULATION VALUE SUMMARY =====")
print(population["population"].describe())

print("\n===== DUPLICATE ROWS =====")
print(population.duplicated().sum())


# STEP 7: Clean population dataset

# Make a copy to preserve the original
population_clean = population.copy()

# Select overall population only
population_clean = population_clean[
    (population_clean["sex"] == "both") &
    (population_clean["age"] == "overall") &
    (population_clean["ethnicity"] == "overall")
].copy()

# Convert date to year
population_clean["year"] = pd.to_datetime(
    population_clean["date"]
).dt.year

# Convert population from thousands to persons
population_clean["population"] = (
    population_clean["population"] * 1000
).round().astype(int)

# Standardise state names
population_clean["state"] = (
    population_clean["state"]
    .str.replace("W.P. ", "WILAYAH PERSEKUTUAN ", regex=False)
    .str.upper()
    .str.strip()
)

# Keep only required columns
population_clean = population_clean[
    ["state", "year", "population"]
].copy()

# Sort by year and state
population_clean = population_clean.sort_values(
    ["year", "state"]
)

# Check for duplicate state-year combinations
duplicates = population_clean.duplicated(
    subset=["state", "year"]
).sum()

print("\n===== STEP 7 RESULTS =====")
print("Total records:", len(population_clean))
print("Number of states:", population_clean["state"].nunique())
print("Earliest year:", population_clean["year"].min())
print("Latest year:", population_clean["year"].max())
print("Duplicate state-year records:", duplicates)

# Display population for 2024
print("\n===== POPULATION 2024 =====")
print(
    population_clean[
        population_clean["year"] == 2024
    ].to_string(index=False)
)

# Save cleaned dataset
population_clean.to_csv(
    "data/cleaned/population_cleaned.csv",
    index=False
)

print("\nSaved: data/cleaned/population_cleaned.csv")


# STEP 8: Inspect hospital beds dataset

print("\n===== HOSPITAL BED DATE RANGE =====")
print("Earliest:", beds["date"].min())
print("Latest:", beds["date"].max())

print("\n===== HOSPITAL BED TYPES =====")
print(beds["type"].value_counts(dropna=False))

print("\n===== HOSPITAL BED STATES =====")
print(beds["state"].unique())

print("\n===== HOSPITAL BED DISTRICTS =====")
print("Unique districts:", beds["district"].nunique())
print(beds["district"].head(20).to_string(index=False))

print("\n===== HOSPITAL BED SAMPLE =====")
print(beds.head(20).to_string(index=False))

print("\n===== HOSPITAL BED VALUE SUMMARY =====")
print(beds["beds"].describe())

print("\n===== DUPLICATE HOSPITAL BED RECORDS =====")
print(beds.duplicated().sum())

print("\n===== RECORDS BY YEAR =====")
beds_inspect = beds.copy()
beds_inspect["year"] = pd.to_datetime(
    beds_inspect["date"]
).dt.year

print(
    beds_inspect.groupby("year")
    .size()
    .to_string()
)


# STEP 9: Clean hospital beds dataset

# Preserve the original data
beds_clean = beds.copy()

# Convert date to year
beds_clean["year"] = pd.to_datetime(
    beds_clean["date"]
).dt.year

# Keep state-level totals only
beds_clean = beds_clean[
    (beds_clean["state"] != "Malaysia") &
    (beds_clean["district"] == "All Districts")
].copy()

# Standardise state names
beds_clean["state"] = (
    beds_clean["state"]
    .str.replace(
        "W.P. ",
        "WILAYAH PERSEKUTUAN ",
        regex=False
    )
    .str.upper()
    .str.strip()
)

# Keep the required columns
beds_clean = beds_clean[
    ["state", "year", "type", "beds"]
].copy()

# Check uniqueness
duplicates = beds_clean.duplicated(
    subset=["state", "year", "type"]
).sum()

print("\n===== STEP 9 RESULTS =====")
print("Total records:", len(beds_clean))
print("Number of states:", beds_clean["state"].nunique())
print("Earliest year:", beds_clean["year"].min())
print("Latest year:", beds_clean["year"].max())
print("Duplicate state-year-type records:", duplicates)

print("\n===== HOSPITAL BEDS 2024 =====")
print(
    beds_clean[
        (beds_clean["year"] == 2024) &
        (beds_clean["type"] == "all")
    ].sort_values("state").to_string(index=False)
)

# Save cleaned dataset
beds_clean.to_csv(
    "data/cleaned/hospital_beds_cleaned.csv",
    index=False
)

print("\nSaved: data/cleaned/hospital_beds_cleaned.csv")


# STEP 10: Combine hospital beds and population

# Select total hospital beds only
beds_total = beds_clean[
    beds_clean["type"] == "all"
].copy()

# Rename the beds column
beds_total = beds_total.rename(
    columns={"beds": "hospital_beds"}
)

# Merge beds with population by state and year
healthcare = pd.merge(
    beds_total[["state", "year", "hospital_beds"]],
    population_clean[["state", "year", "population"]],
    on=["state", "year"],
    how="left",
    validate="one_to_one"
)

# Check missing or invalid population values
missing_population = (
    healthcare["population"].isna()
    | (healthcare["population"] <= 0)
)

print("\n===== MERGE VALIDATION =====")
print("Total records:", len(healthcare))
print("Missing or invalid population:",
      missing_population.sum())

if missing_population.any():
    print(healthcare.loc[
        missing_population, ["state", "year", "population"]
    ].to_string(index=False))
    raise ValueError("Population data requires investigation.")

# Calculate beds per 10,000 residents
healthcare["beds_per_10000"] = (
    healthcare["hospital_beds"]
    / healthcare["population"]
    * 10000
).round(2)

# Sort by year and state
healthcare = healthcare.sort_values(
    ["year", "state"]
)

# Save combined dataset
healthcare.to_csv(
    "data/cleaned/healthcare_beds_population.csv",
    index=False
)

print("\n===== STEP 10 RESULTS =====")
print("Total records:", len(healthcare))
print("States:", healthcare["state"].nunique())
print("Years:", healthcare["year"].min(),
      "-", healthcare["year"].max())

print("\n===== 2024 BEDS PER 10,000 =====")
print(
    healthcare[
        healthcare["year"] == 2024
    ].sort_values(
        "beds_per_10000", ascending=False
    ).to_string(index=False)
)

print("\nSaved: data/cleaned/healthcare_beds_population.csv")


# STEP 11: Validate hospital bed totals

beds_check = beds_clean.pivot(
    index=["state", "year"],
    columns="type",
    values="beds"
).reset_index()

# Sum the individual bed categories
beds_check["calculated_total"] = (
    beds_check["hospital_moh"]
    + beds_check["hospital_non_moh"]
    + beds_check["special_medical_institution"]
)

# Compare with the reported total
beds_check["difference"] = (
    beds_check["all"]
    - beds_check["calculated_total"]
)

mismatches = beds_check[
    beds_check["difference"] != 0
]

print("\n===== STEP 11 VALIDATION =====")
print("State-year combinations:", len(beds_check))
print("Mismatched totals:", len(mismatches))

if len(mismatches) > 0:
    print("\n===== MISMATCH DETAILS =====")
    print(mismatches.to_string(index=False))
else:
    print("All hospital bed totals are consistent.")


# STEP 12: Prepare 2024 data for Vega-Lite

# Select 2024 records
healthcare_2024 = healthcare[
    healthcare["year"] == 2024
].copy()

# Sort states by beds per 10,000 residents
healthcare_2024 = healthcare_2024.sort_values(
    "beds_per_10000",
    ascending=False
)

# Create the folder for website data
from pathlib import Path

Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

# Export to JSON for Vega-Lite
healthcare_2024.to_json(
    "data/processed/beds_per_10000_2024.json",
    orient="records",
    indent=2
)

print("\n===== STEP 12 RESULTS =====")
print("Records exported:", len(healthcare_2024))
print("Year:", healthcare_2024["year"].unique())
print("States:", healthcare_2024["state"].nunique())
print(
    "Saved: data/processed/beds_per_10000_2024.json"
)
