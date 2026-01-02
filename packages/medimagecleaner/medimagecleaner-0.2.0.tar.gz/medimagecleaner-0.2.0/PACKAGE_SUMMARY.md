# medimagecleaner Package Summary

## 📦 Package Structure

```
medimagecleaner/
├── medimagecleaner/              # Main package
│   ├── __init__.py               # Package initialization
│   ├── dicom_deidentifier.py    # DICOM metadata de-identification
│   ├── text_remover.py           # Burned-in text removal
│   ├── format_converter.py       # DICOM to image format conversion
│   ├── validator.py              # De-identification validation
│   ├── audit_logger.py           # Audit logging and compliance
│   ├── batch_processor.py        # Complete workflow orchestration
│   └── cli.py                    # Command-line interface
├── examples/
│   └── complete_example.py       # Comprehensive usage examples
├── setup.py                      # Package installation script
├── requirements.txt              # Dependencies
├── README.md                     # Package documentation
└── USAGE_GUIDE.md               # Quick reference guide
```

## 🎯 Core Features

### 1. **DicomDeidentifier** - Metadata De-identification
- Removes/anonymizes **50+ PHI tags** (HIPAA-compliant)
- Patient info: Name, ID, DOB, Address, Phone
- Institution info: Name, Address, Department
- Physician info: Name, Address, Phone
- Study info: Dates, Times, IDs
- Device info: Serial numbers, IDs
- Options: Date offsetting, ID hashing, selective preservation
- Batch processing support

### 2. **TextRemover** - Burned-in Text Removal
- **OCR-based detection** using Tesseract
- **Region-based cropping** for fixed locations
- **Edge detection** for automatic text identification
- Configurable confidence thresholds
- Works with DICOM and standard images
- Preserves image quality

### 3. **FormatConverter** - Format Conversion
- Convert DICOM to: **PNG**, **JPEG**, **TIFF**, **NumPy**
- Automatic windowing/leveling
- Normalization and resizing
- Photometric interpretation handling
- Batch conversion support

### 4. **DeidentificationValidator** - Validation
- **PHI pattern detection** (names, dates, SSN, phone, email, MRN)
- Private tag detection
- Suspicious value identification
- Configurable strictness levels
- Batch validation with sampling
- Comprehensive validation reports

### 5. **AuditLogger** - Compliance & Auditing
- Complete operation logging
- Patient ID mapping (reversible anonymization)
- Session reports
- Export capabilities for secure storage
- Compliance-ready audit trails

### 6. **BatchProcessor** - Workflow Orchestration
- **Complete end-to-end workflows**
- Single-file and batch processing
- Multi-step pipelines
- Integrated validation
- Comprehensive reporting
- Progress tracking

## 🚀 Usage Examples

### Quick Start (Command Line)
```bash
# Basic usage
medimagecleaner --input ./raw_dicoms --output ./deidentified

# Complete workflow
medimagecleaner \
  --input ./raw_dicoms \
  --output ./deidentified \
  --remove-text \
  --validate \
  --format png
```

### Quick Start (Python)
```python
from medimagecleaner import BatchProcessor

processor = BatchProcessor(log_dir="./logs")
results = processor.process_directory(
    input_dir="./raw_dicoms",
    output_dir="./deidentified",
    remove_metadata=True,
    remove_burned_text=True,
    validate_output=True
)

report = processor.generate_complete_report(results, "./report.txt")
```

### Individual Module Usage

#### Metadata De-identification
```python
from medimagecleaner import DicomDeidentifier

deidentifier = DicomDeidentifier(
    hash_patient_id=True,
    date_offset_days=365,
    preserve_age=True
)
result = deidentifier.deidentify("input.dcm", "output.dcm")
```

#### Text Removal
```python
from medimagecleaner import TextRemover

text_remover = TextRemover(ocr_enabled=True)
result = text_remover.process_dicom(
    "input.dcm", "output.dcm", method="ocr"
)
```

#### Format Conversion
```python
from medimagecleaner import FormatConverter

converter = FormatConverter()
converter.dicom_to_png("input.dcm", "output.png")
```

#### Validation
```python
from medimagecleaner import DeidentificationValidator

validator = DeidentificationValidator(strict_mode=True)
validation = validator.validate_dicom("output.dcm")
```

## 📋 Key Capabilities

### PHI Tags Removed (50+ tags)
✅ Patient: Name, ID, DOB, Sex, Age, Weight, Address, Phone  
✅ Institution: Name, Address, Department, Station  
✅ Physician: Name, Address, Phone, Identification  
✅ Study: Date, Time, ID, Accession Number  
✅ Series: Date, Time, Description  
✅ Device: Serial Number, ID, Gantry ID  
✅ Comments: Image comments, Study comments  
✅ Private tags (optional)  
✅ Overlay data (optional)  
✅ Curve data (optional)

### Text Removal Methods
1. **OCR-based**: Automatic detection using Tesseract
2. **Region cropping**: Remove known fixed locations
3. **Edge detection**: Automatic contour-based detection

### Validation Checks
✅ PHI pattern detection (regex-based)  
✅ Private tag presence  
✅ Suspicious tag values  
✅ Expected anonymization verification  
✅ Batch sampling capability

### Output Formats
✅ DICOM (de-identified)  
✅ PNG  
✅ JPEG  
✅ TIFF  
✅ NumPy arrays (.npy)

## 🔒 Security & Compliance

### HIPAA Compliance
- **Safe Harbor Method**: Removes all 18 HIPAA identifiers
- **Expert Determination**: Provides validation framework
- Comprehensive audit trails
- Re-identification prevention

### Best Practices
1. ✅ Never overwrite original files
2. ✅ Always enable audit logging
3. ✅ Validate all de-identified files
4. ✅ Test on samples first
5. ✅ Manual spot-check validation failures
6. ✅ Store originals separately and securely
7. ✅ Encrypt ID mapping files
8. ✅ Limit access to sensitive logs

## 📊 Workflow Examples

### Workflow 1: Basic Metadata Only
```python
deidentifier = DicomDeidentifier()
deidentifier.batch_deidentify("./raw", "./clean")
```

### Workflow 2: Metadata + Text Removal
```python
processor = BatchProcessor()
processor.process_directory(
    "./raw", "./clean",
    remove_metadata=True,
    remove_burned_text=True
)
```

### Workflow 3: Complete with Validation
```python
processor = BatchProcessor(enable_logging=True)
results = processor.process_directory(
    "./raw", "./clean",
    remove_metadata=True,
    remove_burned_text=True,
    validate_output=True
)
```

### Workflow 4: With Format Conversion
```python
processor = BatchProcessor()
results = processor.process_directory(
    "./raw", "./clean",
    remove_metadata=True,
    remove_burned_text=True,
    convert_format="png",
    validate_output=True
)
```

## 🛠️ Installation

### From Source
```bash
git clone https://github.com/akinboye/medimagecleaner.git
cd medimagecleaner
pip install -e .[ocr]
```

### Dependencies
**Required:**
- pydicom >= 2.3.0
- numpy >= 1.20.0
- opencv-python >= 4.5.0
- Pillow >= 9.0.0

**Optional (for OCR):**
- pytesseract >= 0.3.9
- tesseract-ocr (system package)

### Install Tesseract
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Verify
tesseract --version
```

## 📈 Advanced Features

### Custom PHI Tags
```python
deidentifier = DicomDeidentifier(
    custom_phi_tags=["MyCustomTag1", "MyCustomTag2"]
)
```

### Date Offsetting (Instead of Removal)
```python
deidentifier = DicomDeidentifier(date_offset_days=365)
```

### Selective Preservation
```python
deidentifier = DicomDeidentifier(
    preserve_age=True,
    preserve_sex=True
)
```

### Patient ID Hashing
```python
deidentifier = DicomDeidentifier(hash_patient_id=True)
# Creates reversible mapping: original -> hash
```

### Validation Sampling
```python
validator = DeidentificationValidator()
results = validator.validate_batch(
    "./output",
    sample_rate=0.2  # Validate 20%
)
```

## 🎓 Example Workflows

See `examples/complete_example.py` for comprehensive demonstrations including:
- Basic metadata removal
- Burned-in text removal (OCR, crop, edge detection)
- Format conversion
- Validation
- Complete workflows
- Audit logging
- Custom multi-step processing

## ⚠️ Important Notes

### What This Package Does
✅ Removes PHI from DICOM metadata (50+ tags)  
✅ Removes burned-in text from images  
✅ Validates de-identification  
✅ Provides audit trails  
✅ Converts to standard formats

### What You Must Do
⚠️ Review validation failures manually  
⚠️ Verify sample files before full deployment  
⚠️ Store original data securely  
⚠️ Consult legal/compliance experts  
⚠️ Test workflows on sample data first  
⚠️ Secure ID mapping files  
⚠️ Maintain audit logs

### Limitations
- Cannot guarantee 100% PHI removal (manual review required)
- OCR accuracy depends on image quality
- Some edge cases may require manual intervention
- Burned-in text in poor quality images may be missed
- Users responsible for compliance verification

## 📚 Documentation

- **README.md**: Package overview and installation
- **USAGE_GUIDE.md**: Quick reference
- **examples/complete_example.py**: 7 comprehensive examples
- **Module docstrings**: Detailed API documentation

## 🔧 Troubleshooting

### OCR not working
```bash
sudo apt-get install tesseract-ocr
python -c "import pytesseract; print('OK')"
```

### Memory issues
Process in smaller batches (100 files at a time)

### DICOM read errors
```python
ds = pydicom.dcmread("file.dcm", force=True)
```

## 📄 License

MIT License - See LICENSE file

## ⚖️ Disclaimer

This software is provided as-is. Users are responsible for:
- Validating de-identification effectiveness
- Ensuring compliance with applicable regulations
- Consulting legal/compliance experts
- Testing before production use
- Maintaining proper security practices

## 🙏 Acknowledgments

Built with:
- pydicom - DICOM file handling
- OpenCV - Image processing
- Tesseract - OCR capabilities
- NumPy - Array operations
- Pillow - Image format conversion

---

**Version**: 0.1.0  
**Author**: Akinboye Yusuff  
**Email**: mailakinboye@gmail.com  
**Website**: https://akinboye.dev/  
**Python**: 3.8+  
**License**: MIT
