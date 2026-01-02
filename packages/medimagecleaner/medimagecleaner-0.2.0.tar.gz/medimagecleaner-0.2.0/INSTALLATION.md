# Installation and Testing Guide

## Quick Installation

### Step 1: Install the Package
```bash
cd /path/to/medimagecleaner
pip install -e .
```

### Step 2: Install with OCR Support (Recommended)
```bash
pip install -e .[ocr]
```

### Step 3: Install Tesseract (for OCR)
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Verify installation
tesseract --version
```

## Testing the Package

### Test 1: Command Line Interface
```bash
# Show help
medimagecleaner --help

# Show version
medimagecleaner --version
```

### Test 2: Python Import
```python
import medimagecleaner
print(f"Version: {medimagecleaner.__version__}")

# Test imports
from medimagecleaner import (
    DicomDeidentifier,
    TextRemover,
    FormatConverter,
    DeidentificationValidator,
    AuditLogger,
    BatchProcessor
)
print("✓ All modules imported successfully")
```

### Test 3: Run Examples
```bash
cd examples
python complete_example.py
```

## Sample Usage (No DICOM files needed)

```python
from medimagecleaner import DicomDeidentifier

# Create de-identifier
deidentifier = DicomDeidentifier(
    replacement_value="ANONYMIZED",
    hash_patient_id=True,
    preserve_age=True,
    preserve_sex=True
)

print("✓ DicomDeidentifier created successfully")
print(f"✓ Default PHI tags: {len(deidentifier.DEFAULT_PHI_TAGS)}")
```

## Full Workflow Test (With DICOM Files)

### Prepare Test Data
```bash
# Create directories
mkdir -p test_data/raw
mkdir -p test_data/output

# Place your DICOM files in test_data/raw/
```

### Run Complete Workflow
```python
from medimagecleaner import BatchProcessor

processor = BatchProcessor(
    log_dir="./test_logs",
    enable_logging=True,
    enable_validation=True
)

results = processor.process_directory(
    input_dir="test_data/raw",
    output_dir="test_data/output",
    remove_metadata=True,
    remove_burned_text=False,  # Set to True if OCR is working
    validate_output=True
)

print(f"Processed: {results['successful']}/{results['total_files']}")

# Generate report
report = processor.generate_complete_report(
    results,
    "test_data/report.txt"
)
print(report)
```

## Troubleshooting

### Issue: Module not found
```bash
# Ensure you're in the package directory
cd /path/to/medimagecleaner
pip install -e .
```

### Issue: OCR not working
```bash
# Install Tesseract
sudo apt-get install tesseract-ocr

# Install pytesseract
pip install pytesseract

# Test
python -c "import pytesseract; print('OCR OK')"
```

### Issue: DICOM read errors
```python
import pydicom
# Use force=True for non-compliant files
ds = pydicom.dcmread("file.dcm", force=True)
```

## Validation Checklist

Before using in production:

- [ ] Package installed successfully
- [ ] All modules import without errors
- [ ] Command-line interface works
- [ ] Tested on sample DICOM files
- [ ] Validation reports reviewed
- [ ] Audit logs created and accessible
- [ ] Original data backed up separately
- [ ] Manual spot-check performed

## Next Steps

1. Review the PACKAGE_SUMMARY.md for feature overview
2. Check examples/complete_example.py for detailed usage
3. Read USAGE_GUIDE.md for API reference
4. Test on your own DICOM files
5. Review validation reports
6. Implement in your workflow

## Support

For issues or questions:
- Check documentation in README.md
- Review examples in examples/
- Check module docstrings
- Create GitHub issue (if applicable)
