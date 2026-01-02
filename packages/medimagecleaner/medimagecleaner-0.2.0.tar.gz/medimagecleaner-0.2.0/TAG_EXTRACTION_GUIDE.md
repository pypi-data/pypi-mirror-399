# DICOM Tag Extraction Tools

Complete guide for extracting, analyzing, and exporting DICOM tags using medimagecleaner.

## Overview

This package includes **2 tag extraction tools**:

1. **`dicom_tag_extractor.py`** - Comprehensive tag processor with PHI detection
2. **`dicom_tags.py`** - Simple command-line tag reader

## Tool 1: Comprehensive Tag Processor

### Features
- Extract all DICOM tags
- Identify PHI tags automatically
- Organize tags by category (Patient, Study, Series, Image, Equipment)
- Compare tags before/after de-identification
- Export to JSON, CSV, or TXT

### Usage

```python
from dicom_tag_extractor import DicomTagProcessor

processor = DicomTagProcessor()

# Read all tags
all_tags = processor.read_all_tags("scan.dcm")
processor.print_tags_summary(all_tags)

# Get only PHI tags
phi_tags = processor.get_phi_tags("scan.dcm")
print(f"PHI Tags Found: {phi_tags['phi_count']}")

# Get organized standard tags
standard_tags = processor.get_standard_tags("scan.dcm")

# Compare before/after de-identification
comparison = processor.compare_tags_before_after(
    "original.dcm",
    "deidentified.dcm"
)

# Export results
processor.export_tags_json(phi_tags, "phi_tags.json")
processor.export_tags_csv(all_tags, "all_tags.csv")
processor.export_tags_txt(comparison, "comparison.txt")
```

### Methods

#### `read_all_tags(dicom_path)`
Returns all DICOM tags with metadata.

**Returns:**
```python
{
    "file_path": "/path/to/file.dcm",
    "total_tags": 150,
    "tags": [
        {
            "tag": "(0010, 0010)",
            "tag_name": "PatientName",
            "vr": "PN",
            "value": "Doe^John",
            "keyword": "PatientName",
            "is_private": false
        },
        # ... more tags
    ]
}
```

#### `get_phi_tags(dicom_path)`
Returns only PHI-related tags.

**Returns:**
```python
{
    "file_path": "/path/to/file.dcm",
    "phi_count": 15,
    "phi_tags_found": [
        {
            "tag": "(0010, 0010)",
            "tag_name": "PatientName",
            "vr": "PN",
            "value": "Doe^John",
            "keyword": "PatientName"
        },
        # ... more PHI tags
    ]
}
```

#### `get_standard_tags(dicom_path)`
Returns commonly used tags organized by category.

**Returns:**
```python
{
    "file_path": "/path/to/file.dcm",
    "patient": {
        "name": "Doe^John",
        "id": "12345678",
        "birth_date": "19800515",
        "sex": "M",
        "age": "045Y"
    },
    "study": {
        "instance_uid": "1.2.840...",
        "date": "20240101",
        "time": "120000",
        "description": "CT CHEST",
        "accession_number": "ACC123456"
    },
    "series": {
        "instance_uid": "1.2.840...",
        "number": "1",
        "description": "AXIAL",
        "modality": "CT"
    },
    "image": {
        "sop_instance_uid": "1.2.840...",
        "rows": "512",
        "columns": "512"
    },
    "equipment": {
        "manufacturer": "SIEMENS",
        "model_name": "Somatom Force"
    },
    "institution": {
        "name": "General Hospital"
    },
    "physicians": {
        "referring": "Smith^John^MD",
        "performing": "Johnson^Jane^MD"
    }
}
```

#### `compare_tags_before_after(original_path, deidentified_path)`
Compares PHI tags before and after de-identification.

**Returns:**
```python
{
    "original_file": "/path/to/original.dcm",
    "deidentified_file": "/path/to/deidentified.dcm",
    "original_phi_count": 15,
    "deidentified_phi_count": 2,
    "phi_removed": 13,
    "removed_tags": [
        {"tag_name": "PatientName", "value": "Doe^John"},
        # ... tags that were removed
    ],
    "remaining_tags": [
        {"tag_name": "PatientSex", "value": "M"},
        # ... tags still present
    ]
}
```

### PHI Tags Detected

The processor automatically identifies these PHI tags:

**Patient Information:**
- PatientName
- PatientID
- PatientBirthDate
- PatientBirthTime
- PatientSex
- PatientAge
- PatientAddress
- PatientTelephoneNumbers
- PatientMotherBirthName
- MedicalRecordLocator

**Institution & Personnel:**
- InstitutionName
- InstitutionAddress
- ReferringPhysicianName
- PerformingPhysicianName
- OperatorsName

**Study & Series:**
- StudyDate
- SeriesDate
- AcquisitionDate
- StudyTime
- SeriesTime
- AccessionNumber
- StudyID

**Equipment:**
- DeviceSerialNumber
- StationName

And 20+ more tags...

---

## Tool 2: Simple Command-Line Tag Reader

### Features
- Quick tag extraction
- Filter by PHI tags
- View organized standard tags
- Export to JSON, CSV, TXT
- Simple command-line interface

### Installation

```bash
chmod +x dicom_tags.py
```

### Usage

#### Display All Tags
```bash
python dicom_tags.py scan.dcm
```

Output:
```
================================================================================
DICOM File: scan.dcm
================================================================================
Total Tags: 150

--------------------------------------------------------------------------------
Tag             Name                           VR    Value
--------------------------------------------------------------------------------
(0008, 0005)    SpecificCharacterSet          CS    ISO_IR 100
(0008, 0016)    SOPClassUID                   UI    1.2.840.10008.5.1.4.1.1.2
(0008, 0018)    SOPInstanceUID                UI    1.2.840...
(0010, 0010)    PatientName                   PN    Doe^John
(0010, 0020)    PatientID                     LO    12345678
...
================================================================================
```

#### Show Only PHI Tags
```bash
python dicom_tags.py scan.dcm --phi-only
```

Output:
```
================================================================================
DICOM File: scan.dcm
================================================================================
PHI Tags: 15

--------------------------------------------------------------------------------
Tag             Name                           VR    Value
--------------------------------------------------------------------------------
(0010, 0010)    PatientName                   PN    Doe^John
(0010, 0020)    PatientID                     LO    12345678
(0010, 0030)    PatientBirthDate              DA    19800515
(0010, 0040)    PatientSex                    CS    M
...
================================================================================
```

#### Show Organized Standard Tags
```bash
python dicom_tags.py scan.dcm --standard
```

Output:
```
================================================================================
DICOM File: scan.dcm
================================================================================

PATIENT INFORMATION:
----------------------------------------
  Name                : Doe^John
  Id                  : 12345678
  Birth Date          : 19800515
  Sex                 : M
  Age                 : 045Y

STUDY INFORMATION:
----------------------------------------
  Date                : 20240101
  Time                : 120000
  Description         : CT CHEST
  Modality            : CT
  Accession           : ACC123456

IMAGE INFORMATION:
----------------------------------------
  Rows                : 512
  Columns             : 512
  Bits Allocated      : 16

INSTITUTION:
----------------------------------------
  Name                : General Hospital
================================================================================
```

#### Export to JSON
```bash
python dicom_tags.py scan.dcm --format json --output tags.json
```

#### Export PHI Tags to CSV
```bash
python dicom_tags.py scan.dcm --phi-only --format csv --output phi_tags.csv
```

#### Export to Text File
```bash
python dicom_tags.py scan.dcm --format txt --output report.txt
```

### Command-Line Options

```
usage: dicom_tags.py [-h] [--phi-only] [--standard] [--format {json,csv,txt}]
                     [--output OUTPUT]
                     dicom_file

positional arguments:
  dicom_file            Path to DICOM file

optional arguments:
  -h, --help            show this help message and exit
  --phi-only            Show only PHI tags
  --standard            Show standard organized tags
  --format {json,csv,txt}
                        Export format
  --output OUTPUT, -o OUTPUT
                        Output file path
```

---

## Complete Workflow Example

### Step 1: Generate Test DICOM Files
```bash
python generate_test_dicoms.py
```

### Step 2: Check Original Tags
```bash
# View all tags
python dicom_tags.py sample_dicoms/with_phi/patient_001_with_phi.dcm

# Export PHI tags
python dicom_tags.py sample_dicoms/with_phi/patient_001_with_phi.dcm \
    --phi-only --format json --output original_phi.json
```

### Step 3: De-identify Using medimagecleaner
```python
from medimagecleaner import DicomDeidentifier

deidentifier = DicomDeidentifier(
    hash_patient_id=True,
    date_offset_days=365
)

result = deidentifier.deidentify(
    "sample_dicoms/with_phi/patient_001_with_phi.dcm",
    "deidentified.dcm"
)
```

### Step 4: Compare Tags
```python
from dicom_tag_extractor import DicomTagProcessor

processor = DicomTagProcessor()

comparison = processor.compare_tags_before_after(
    "sample_dicoms/with_phi/patient_001_with_phi.dcm",
    "deidentified.dcm"
)

print(f"PHI Removed: {comparison['phi_removed']} tags")

# Export comparison
processor.export_tags_json(comparison, "comparison.json")
processor.export_tags_txt(comparison, "comparison_report.txt")
```

### Step 5: Verify De-identification
```bash
# Check remaining PHI
python dicom_tags.py deidentified.dcm --phi-only

# Should show minimal or no PHI
```

---

## Integration with medimagecleaner

### Detect PHI Before Processing
```python
from dicom_tag_extractor import DicomTagProcessor
from medimagecleaner import BatchProcessor

processor = DicomTagProcessor()

# Check what PHI exists
phi_tags = processor.get_phi_tags("scan.dcm")

if phi_tags['phi_count'] > 0:
    print(f"Found {phi_tags['phi_count']} PHI tags")
    
    # De-identify
    batch_processor = BatchProcessor()
    batch_processor.process_directory("./input", "./output")
```

### Validate De-identification
```python
from medimagecleaner import DeidentificationValidator
from dicom_tag_extractor import DicomTagProcessor

# Validate
validator = DeidentificationValidator()
validation = validator.validate_dicom("deidentified.dcm")

# Get remaining tags for manual review
if not validation['passed']:
    processor = DicomTagProcessor()
    remaining = processor.get_phi_tags("deidentified.dcm")
    
    print("Remaining PHI tags:")
    for tag in remaining['phi_tags_found']:
        print(f"  • {tag['tag_name']}: {tag['value']}")
```

---

## Export Formats

### JSON Format
```json
{
  "file_path": "/path/to/scan.dcm",
  "phi_count": 15,
  "phi_tags_found": [
    {
      "tag": "(0010, 0010)",
      "tag_name": "PatientName",
      "vr": "PN",
      "value": "Doe^John",
      "keyword": "PatientName"
    }
  ]
}
```

### CSV Format
```csv
tag,tag_name,vr,value,keyword
"(0010, 0010)",PatientName,PN,Doe^John,PatientName
"(0010, 0020)",PatientID,LO,12345678,PatientID
```

### TXT Format
```
================================================================================
DICOM TAGS REPORT
================================================================================

File: /path/to/scan.dcm
PHI Tags: 15

--------------------------------------------------------------------------------
TAGS
--------------------------------------------------------------------------------

Tag: (0010, 0010)
  Name: PatientName
  VR: PN
  Value: Doe^John
  Keyword: PatientName
```

---

## Use Cases

### 1. PHI Audit
Extract and document all PHI before sharing data:
```bash
python dicom_tags.py scan.dcm --phi-only --format json --output audit.json
```

### 2. Data Quality Check
Verify required fields are present:
```bash
python dicom_tags.py scan.dcm --standard
```

### 3. De-identification Verification
Compare before/after to ensure PHI removal:
```python
processor.compare_tags_before_after("original.dcm", "clean.dcm")
```

### 4. Metadata Export
Export all tags for documentation:
```bash
python dicom_tags.py scan.dcm --format csv --output metadata.csv
```

### 5. Batch Tag Extraction
Process multiple files:
```bash
for file in *.dcm; do
    python dicom_tags.py "$file" --phi-only --format json --output "${file%.dcm}_phi.json"
done
```

---

## Tips & Best Practices

1. **Always check PHI** before sharing DICOM files
2. **Export tags** for audit trails
3. **Compare before/after** de-identification
4. **Use JSON format** for programmatic processing
5. **Use CSV format** for spreadsheet analysis
6. **Use TXT format** for human-readable reports

---

## Troubleshooting

### Issue: "pydicom not installed"
```bash
pip install pydicom
```

### Issue: "Cannot read DICOM file"
Ensure file is valid DICOM format:
```python
import pydicom
ds = pydicom.dcmread("file.dcm")  # Will raise error if invalid
```

### Issue: "No PHI tags found"
File may already be de-identified. Check with:
```bash
python dicom_tags.py file.dcm --standard
```

---

## Requirements

- Python 3.8+
- pydicom >= 2.3.0
- medimagecleaner (for integration features)

---

**Author**: Akinboye Yusuff  
**Email**: mailakinboye@gmail.com  
**Website**: https://akinboye.dev/  
**Package**: medimagecleaner v0.2.0
