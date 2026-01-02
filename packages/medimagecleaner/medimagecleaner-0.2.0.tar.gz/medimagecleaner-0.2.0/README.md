# medimagecleaner

**Comprehensive Python package for removing Protected Health Information (PHI) from medical images**

[![PyPI version](https://badge.fury.io/py/medimagecleaner.svg)](https://badge.fury.io/py/medimagecleaner)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-akinboye%2Fmedimagecleaner-blue)](https://github.com/akinboye/medimagecleaner)

## Overview

`medimagecleaner` is a production-ready package for de-identifying medical images with a focus on DICOM files. It provides comprehensive tools for metadata removal, burned-in text detection, face detection, risk assessment, and compliance validation.

### Key Features

🔒 **Complete De-identification**
- Remove/anonymize 50+ PHI tags from DICOM metadata
- Detect and remove burned-in text using OCR
- Detect and remove faces from clinical photos
- Convert DICOM to standard formats (PNG, JPEG, TIFF, NumPy)

✅ **Validation & Compliance**
- Automated PHI detection and validation
- Re-identification risk assessment (K-anonymity, L-diversity)
- HIPAA-compliant de-identification (Safe Harbor & Expert Determination)
- Complete audit trails for regulatory compliance

⚡ **Performance & UX**
- Batch processing with progress tracking
- Real-time ETA and status updates
- Comprehensive reporting and analytics
- Command-line interface for easy integration

## Quick Start

### Installation

```bash
# Basic installation
pip install medimagecleaner

# With OCR support (recommended)
pip install medimagecleaner[ocr]

# Full installation (all features)
pip install medimagecleaner[all]
```

**Note:** OCR features require Tesseract. Install via:
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`
- Windows: [Download installer](https://github.com/UB-Mannheim/tesseract/wiki)

### Basic Usage

```python
from medimagecleaner import BatchProcessor

# Initialize processor
processor = BatchProcessor(
    log_dir="./logs",
    enable_logging=True,
    enable_validation=True
)

# Process entire directory
results = processor.process_directory(
    input_dir="./raw_dicoms",
    output_dir="./deidentified",
    remove_metadata=True,
    remove_burned_text=True,
    validate_output=True
)

# Generate comprehensive report
report = processor.generate_complete_report(
    results,
    output_path="./deidentification_report.txt"
)

print(f"Processed: {results['successful']}/{results['total_files']} files")
```

### Command Line

```bash
# Basic de-identification
medimagecleaner --input ./raw --output ./clean

# With all features
medimagecleaner \
  --input ./raw \
  --output ./clean \
  --remove-text \
  --validate \
  --format png \
  --log-dir ./logs
```

## Core Features

### 1. DICOM Metadata De-identification

Remove or anonymize 50+ PHI tags including patient info, physician names, dates, and device identifiers.

```python
from medimagecleaner import DicomDeidentifier

deidentifier = DicomDeidentifier(
    hash_patient_id=True,      # Hash instead of removing
    date_offset_days=365,      # Offset dates by 1 year
    preserve_age=True,         # Keep age information
    preserve_sex=True          # Keep sex information
)

result = deidentifier.deidentify(
    input_path="scan.dcm",
    output_path="anonymized.dcm",
    remove_private_tags=True
)
```

### 2. Burned-in Text Removal

Detect and remove patient information embedded in image pixels.

```python
from medimagecleaner import TextRemover

text_remover = TextRemover(ocr_enabled=True)

# OCR-based detection
result = text_remover.process_dicom(
    "input.dcm",
    "output.dcm",
    method="ocr"
)

# Region-based cropping
result = text_remover.process_dicom(
    "input.dcm",
    "output.dcm",
    method="crop",
    crop_top=0.1  # Remove top 10%
)
```

### 3. Face Detection & Removal

Protect patient privacy by detecting and removing faces from clinical images.

```python
from medimagecleaner import FaceRemover

face_remover = FaceRemover(method="blur", blur_strength=25)

result = face_remover.process_image(
    "patient_photo.jpg",
    "deidentified.jpg"
)

print(f"Detected {result['faces_detected']} faces")
```

### 4. Re-identification Risk Assessment

Assess the risk that de-identified data could be re-identified.

```python
from medimagecleaner import RiskAssessment

risk = RiskAssessment(strict_mode=True)

# Assess entire dataset
assessment = risk.assess_dataset("./deidentified")

print(f"Risk Level: {assessment['overall_risk_level']}")
print(f"K-anonymity: {assessment['k_anonymity']['k_value']}")

# Generate detailed report
report = risk.generate_report(assessment, "risk_report.txt")
```

### 5. Format Conversion

Convert de-identified DICOM files to standard image formats.

```python
from medimagecleaner import FormatConverter

converter = FormatConverter(
    normalize=True,
    apply_windowing=True
)

# Convert to PNG
converter.dicom_to_png("scan.dcm", "scan.png")

# Batch conversion
results = converter.batch_convert(
    input_dir="./dicoms",
    output_dir="./images",
    output_format="png"
)
```

### 6. Validation

Automated validation ensures PHI has been properly removed.

```python
from medimagecleaner import DeidentificationValidator

validator = DeidentificationValidator(strict_mode=True)

# Validate single file
validation = validator.validate_dicom("output.dcm")

# Batch validation
results = validator.validate_batch(
    input_dir="./deidentified",
    sample_rate=0.2  # Validate 20%
)

# Generate report
report = validator.generate_report(results, "validation_report.txt")
```

### 7. Progress Tracking

Real-time progress updates for long-running operations.

```python
from medimagecleaner import ProgressTracker, with_progress

# Progress bar
with ProgressTracker(100, "Processing") as tracker:
    for i in range(100):
        # Do work
        tracker.update()

# Iterator wrapper
for file in with_progress(files, "Converting"):
    process(file)
```

## Module Reference

| Module | Description |
|--------|-------------|
| `DicomDeidentifier` | Remove PHI from DICOM metadata |
| `TextRemover` | Remove burned-in text from images |
| `FaceRemover` | Detect and remove faces |
| `FormatConverter` | Convert DICOM to standard formats |
| `DeidentificationValidator` | Validate PHI removal |
| `RiskAssessment` | Assess re-identification risk |
| `AuditLogger` | Maintain compliance audit trails |
| `BatchProcessor` | Orchestrate complete workflows |
| `ProgressTracker` | Real-time progress tracking |

## Compliance

This package supports HIPAA de-identification requirements:

- **Safe Harbor Method (§164.514(b))**: Removes all 18 HIPAA identifiers
- **Expert Determination**: Provides validation framework and risk assessment
- **Audit Requirements**: Comprehensive logging for regulatory compliance

**Disclaimer**: This software is provided as-is. Users are responsible for validating that de-identification meets their specific compliance requirements.

## Best Practices

1. ✅ Never overwrite originals - Always save to different location
2. ✅ Enable validation - Always validate de-identified files
3. ✅ Use audit logging - Maintain compliance trails
4. ✅ Test on samples - Verify workflow before full batch
5. ✅ Manual review - Spot-check validation failures
6. ✅ Assess risk - Run risk assessment before sharing
7. ✅ Secure storage - Keep originals and mappings separate

## License

MIT License - See [LICENSE](LICENSE) file for details

## Changelog

### v0.2.0 (2025-12-28)
- ✨ Added face detection and removal
- ✨ Added re-identification risk assessment (K-anonymity, L-diversity)
- ✨ Added progress tracking and status logging
- 📚 Enhanced documentation with feature roadmap
- 🎯 Improved PyPI packaging

### v0.1.0 (2025-12-22)
- 🎉 Initial release
- ✅ DICOM metadata de-identification
- ✅ Burned-in text removal
- ✅ Format conversion
- ✅ Validation and audit logging

---

**medimagecleaner** - Comprehensive medical image de-identification for HIPAA compliance
