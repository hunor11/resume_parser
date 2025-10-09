import os
import zipfile

import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ZIP_PATH = os.path.join(DATA_DIR, "UpdatedResumeDataSet.csv.zip")
CSV_PATH = os.path.join(DATA_DIR, "UpdatedResumeDataSet.csv")
RESUMES_DIR = os.path.join(DATA_DIR, "resumes")

# Unzip the CSV file if not already present
if not os.path.exists(CSV_PATH):
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(DATA_DIR)
    print(f"Extracted {ZIP_PATH} to {DATA_DIR}")
else:
    print(f"{CSV_PATH} already exists.")

# Create resumes directory
os.makedirs(RESUMES_DIR, exist_ok=True)

# Read CSV and write resumes to text files
print("Reading CSV and writing resumes...")
data = pd.read_csv(CSV_PATH)
for i, resume in enumerate(data["Resume"]):
    with open(os.path.join(RESUMES_DIR, f"resume_{i}.txt"), "w") as f:
        f.write(str(resume))
print(f"Wrote {len(data['Resume'])} resumes to {RESUMES_DIR}")
