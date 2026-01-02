# DICOM Test File Generator

This script generates sample DICOM files with and without PHI for testing the medimagecleaner package.

## Overview

The generator creates realistic test DICOM files in three categories:
1. **Files WITH PHI** - Contains patient information for detection testing
2. **Files WITHOUT PHI** - Clean, de-identified files for validation
3. **Mixed Directory** - Combination for batch processing tests

## Requirements

```bash
pip install pydicom pillow numpy
```

## Usage

### Basic Usage

```bash
python generate_test_dicoms.py
```

This will create:
```
./sample_dicoms/
├── with_phi/        # 10 files with various PHI types
├── no_phi/          # 10 clean, de-identified files
└── mixed/           # 10 files (5 with PHI, 5 clean)
```

### Programmatic Usage

```python
from generate_test_dicoms import DICOMGenerator

# Initialize generator
generator = DICOMGenerator(output_dir="./my_test_files")

# Generate complete test dataset
files = generator.generate_test_dataset()

# Or generate individual files
phi_file = generator.generate_dicom_with_phi(
    filename="test_with_phi.dcm",
    include_burned_text=True,
    include_face=True
)

clean_file = generator.generate_dicom_without_phi(
    filename="test_clean.dcm"
)
```

## Generated PHI Types

### Files WITH PHI Include:

**Metadata PHI (ALL files):**
- PatientName (e.g., "Doe^John")
- PatientID (e.g., "12345678")
- PatientBirthDate (e.g., "19800515")
- PatientSex (e.g., "M")
- PatientAddress
- PatientTelephoneNumbers
- InstitutionName
- ReferringPhysicianName
- PerformingPhysicianName
- StudyDate, StudyTime
- AccessionNumber
- DeviceSerialNumber
- StationName

**Burned-in Text (50% of files):**
- Patient name, ID, and DOB visible in image pixels
- Located at top-left corner
- Example: "Doe^John | 12345678 | DOB: 19800515"

**Faces (33% of files):**
- Simple face representation in image
- Located at top-right corner
- Detectable by face detection algorithms

### Files WITHOUT PHI:

- PatientName: "ANONYMIZED"
- PatientID: "ANON123456"
- PatientBirthDate: Empty
- PatientSex: "O" (Other/Unknown)
- No burned-in text
- No faces
- Minimal study information
- No physician or institution details

## Test Scenarios

### 1. PHI Detection Test

```python
from medimagecleaner import PHIDetector

detector = PHIDetector(
    enable_ocr=True,
    enable_face_detection=True,
    enable_risk_assessment=True
)

# Check single file
report = detector.check_file('./sample_dicoms/with_phi/patient_001_with_phi.dcm')

print(f"PHI Detected: {report['phi_detected']}")
print(f"Metadata PHI: {report['summary']['has_metadata_phi']}")
print(f"Burned-in Text: {report['summary']['has_burned_text']}")
print(f"Faces: {report['summary']['has_faces']}")
print(f"Risk Level: {report['summary']['overall_risk']}")
```

### 2. Batch Detection Test

```python
from medimagecleaner import PHIDetector

detector = PHIDetector()

# Check entire directory
results = detector.check_directory('./sample_dicoms/mixed')

print(f"Total Files: {results['total_files']}")
print(f"Files with PHI: {results['files_with_phi']}")
print(f"Clean Files: {results['files_clean']}")
print(f"Metadata PHI: {results['summary']['metadata_phi_count']}")
print(f"Burned Text: {results['summary']['burned_text_count']}")
print(f"Faces: {results['summary']['faces_count']}")

# Generate report
report = detector.generate_report(results, "batch_check_report.txt")
```

### 3. De-identification Workflow

```python
from medimagecleaner import BatchProcessor, PHIDetector

# Step 1: Check for PHI
detector = PHIDetector()
check_results = detector.check_directory('./sample_dicoms/with_phi')

print(f"Files with PHI: {check_results['files_with_phi']}")

# Step 2: De-identify
processor = BatchProcessor(log_dir="./logs")
deidentify_results = processor.process_directory(
    input_dir='./sample_dicoms/with_phi',
    output_dir='./deidentified',
    remove_metadata=True,
    remove_burned_text=True,
    validate_output=True
)

print(f"Processed: {deidentify_results['successful']} files")

# Step 3: Verify PHI removed
verify_results = detector.check_directory('./deidentified')

if verify_results['files_with_phi'] == 0:
    print("✓ All PHI successfully removed!")
else:
    print(f"⚠ PHI still found in {verify_results['files_with_phi']} files")
```

### 4. Validation Test

```python
from medimagecleaner import DeidentificationValidator

validator = DeidentificationValidator(strict_mode=True)

# Validate clean file
result = validator.validate_dicom('./sample_dicoms/no_phi/patient_001_no_phi.dcm')

print(f"Passed Validation: {result['passed']}")
print(f"Remaining PHI: {result['remaining_phi']}")
print(f"Suspicious Tags: {result['suspicious_tags']}")

# Validate file with PHI (should fail)
result_phi = validator.validate_dicom('./sample_dicoms/with_phi/patient_001_with_phi.dcm')

print(f"Passed Validation: {result_phi['passed']}")  # Should be False
print(f"Failures: {len(result_phi['failures'])}")
```

### 5. Face Detection Test

```python
from medimagecleaner import FaceRemover
import pydicom

face_remover = FaceRemover()

# Load DICOM with face
ds = pydicom.dcmread('./sample_dicoms/with_phi/patient_001_with_phi.dcm')
pixel_array = ds.pixel_array

# Detect faces
faces = face_remover.detect_faces_haar(pixel_array)

print(f"Detected {len(faces)} face(s)")
for i, (x, y, w, h) in enumerate(faces, 1):
    print(f"  Face {i}: Location ({x}, {y}), Size {w}x{h}")

# Remove faces
result = face_remover.process_dicom(
    './sample_dicoms/with_phi/patient_001_with_phi.dcm',
    './output_no_face.dcm'
)

print(f"Faces removed: {result['faces_detected']}")
```

### 6. Risk Assessment Test

```python
from medimagecleaner import RiskAssessment

risk = RiskAssessment(strict_mode=True)

# Assess single file
assessment = risk.assess_dicom_file('./sample_dicoms/with_phi/patient_001_with_phi.dcm')

print(f"Risk Score: {assessment['risk_score']}/100")
print(f"Risk Level: {assessment['risk_level']}")
print(f"Remaining PHI: {assessment['remaining_phi']}")
print(f"Risk Factors: {assessment['risk_factors']}")

# Assess entire dataset
dataset_risk = risk.assess_dataset('./sample_dicoms/with_phi')

print(f"\nDataset Assessment:")
print(f"Overall Risk: {dataset_risk['overall_risk_level']}")
print(f"K-anonymity: {dataset_risk['k_anonymity']['k_value']}")
print(f"High Risk Files: {dataset_risk['file_risk_distribution']['high']}")

# Generate report
report = risk.generate_report(dataset_risk, "risk_report.txt")
```

## File Specifications

### Image Properties
- **Size**: 512x512 pixels
- **Bit Depth**: 16-bit (DICOM standard)
- **Photometric Interpretation**: MONOCHROME2
- **Modality**: CT (Computed Tomography)

### Metadata
- All files have valid DICOM structure
- Proper UIDs (SOPInstanceUID, StudyInstanceUID, SeriesInstanceUID)
- Transfer Syntax: Implicit VR Little Endian
- SOP Class: CT Image Storage

### Pixel Data
- Random noise simulating tissue
- Circular structure simulating organ/anatomy
- Optional burned-in text (top-left)
- Optional face representation (top-right)

## Sample Patients

The generator uses 3 sample patients with realistic but fake information:

1. **Patient 1**: Doe^John (Male, DOB: 1980-05-15)
2. **Patient 2**: Smith^Jane (Female, DOB: 1992-03-08)
3. **Patient 3**: Johnson^Robert (Male, DOB: 1975-09-20)

## Generated Files Breakdown

### with_phi/ (10 files)
- **patient_001_with_phi.dcm**: Metadata + burned text + face
- **patient_002_with_phi.dcm**: Metadata + burned text
- **patient_003_with_phi.dcm**: Metadata + face
- **patient_004_with_phi.dcm**: Metadata + burned text + face
- **patient_005_with_phi.dcm**: Metadata + burned text
- **patient_006_with_phi.dcm**: Metadata + face
- **patient_007_with_phi.dcm**: Metadata + burned text + face
- **patient_008_with_phi.dcm**: Metadata + burned text
- **patient_009_with_phi.dcm**: Metadata + face
- **patient_010_with_phi.dcm**: Metadata + burned text + face

### no_phi/ (10 files)
- All files completely de-identified
- No metadata PHI
- No burned-in text
- No faces
- Safe for sharing/testing validation

### mixed/ (10 files)
- **scan_001_phi.dcm** to **scan_005_phi.dcm**: With PHI
- **scan_006_clean.dcm** to **scan_010_clean.dcm**: Clean
- Ideal for batch processing tests

## Advanced Usage

### Custom Patient Data

```python
from generate_test_dicoms import DICOMGenerator

generator = DICOMGenerator()

# Add custom patient
custom_patient = {
    "name": "Custom^Patient",
    "id": "99999999",
    "dob": "20000101",
    "sex": "F",
    "address": "Custom Address",
    "phone": "(555) 000-0000",
}

generator.sample_patients.append(custom_patient)

# Generate with custom patient
ds = generator.create_base_dicom(modality="MR")
ds = generator.add_phi_metadata(ds, custom_patient)
```

### Different Modalities

```python
# Generate MR instead of CT
ds = generator.create_base_dicom(modality="MR")

# Other modalities
ds_xr = generator.create_base_dicom(modality="XR")  # X-Ray
ds_us = generator.create_base_dicom(modality="US")  # Ultrasound
ds_mg = generator.create_base_dicom(modality="MG")  # Mammography
```

### Custom Image Content

```python
# Create image with specific text
custom_image = generator.create_image_with_text(
    width=1024,
    height=1024,
    text_content="CONFIDENTIAL PATIENT DATA",
    include_face=True
)

# Add to DICOM
ds = generator.add_pixel_data(ds, custom_image)
```

## Verification

After generation, verify files:

```bash
# List generated files
ls -lh sample_dicoms/with_phi/
ls -lh sample_dicoms/no_phi/
ls -lh sample_dicoms/mixed/

# Check DICOM validity
python -c "import pydicom; ds = pydicom.dcmread('sample_dicoms/with_phi/patient_001_with_phi.dcm'); print(f'Patient: {ds.PatientName}')"

# View image
python -c "import pydicom; import matplotlib.pyplot as plt; ds = pydicom.dcmread('sample_dicoms/with_phi/patient_001_with_phi.dcm'); plt.imshow(ds.pixel_array, cmap='gray'); plt.show()"
```

## Cleanup

```bash
# Remove generated files
rm -rf sample_dicoms/
```

## Notes

- All patient data is **synthetic and fake**
- Generated for **testing purposes only**
- Files are **valid DICOM** but not real medical data
- Use for **development and testing** of PHI detection/removal tools
- Safe to commit to version control (no real PHI)

## Integration with medimagecleaner

This generator is specifically designed to test all features of medimagecleaner:

1. ✅ **PHI Detection** - Files contain detectable PHI
2. ✅ **Metadata De-identification** - Test metadata removal
3. ✅ **Text Removal** - Test OCR-based text detection
4. ✅ **Face Removal** - Test face detection algorithms
5. ✅ **Validation** - Test validation against clean files
6. ✅ **Risk Assessment** - Test risk calculation
7. ✅ **Batch Processing** - Test directory processing

## License

MIT License - Same as medimagecleaner package

---

**Generated by**: DICOM Test File Generator v1.0  
**For**: medimagecleaner package testing  
**Date**: December 2025
