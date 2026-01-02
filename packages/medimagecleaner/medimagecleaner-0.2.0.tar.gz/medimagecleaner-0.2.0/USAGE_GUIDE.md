# medimagecleaner - Complete Usage Guide

## Overview

medimagecleaner is a comprehensive Python package for de-identifying medical images. It provides:

- **Metadata De-identification**: Removes 50+ PHI tags from DICOM headers
- **Burned-in Text Removal**: OCR-based and region-based text removal
- **Format Conversion**: DICOM to PNG/JPEG/TIFF/NPY
- **Validation**: Automated PHI detection and verification
- **Audit Logging**: Complete compliance trail
- **Batch Processing**: Complete workflow orchestration

## Installation

```bash
pip install -e .              # Basic
pip install -e .[ocr]         # With OCR
pip install -e .[dev,ocr]     # Development
```

## Quick Reference

### Command Line
```bash
medimagecleaner --input ./raw --output ./clean --remove-text --validate
```

### Python API
```python
from medimagecleaner import BatchProcessor
processor = BatchProcessor()
results = processor.process_directory("./raw", "./clean",
    remove_metadata=True, remove_burned_text=True, validate_output=True)
```

See full documentation in the package for detailed usage examples.
