# Changelog

All notable changes to the medimagecleaner project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-12-28

### Added
- **Face Detection and Removal Module** (`face_remover.py`)
  - Multiple removal methods: blur, pixelate, black box, intelligent removal
  - Haar Cascade face detection (works out-of-the-box)
  - Optional DNN support for improved accuracy
  - Batch processing for entire directories
  - Support for both DICOM and standard image formats

- **Re-identification Risk Assessment Module** (`risk_assessment.py`)
  - K-anonymity calculation for dataset privacy assessment
  - L-diversity analysis for sensitive attributes
  - Uniqueness detection to identify risky records
  - Individual file and dataset-level risk scoring
  - Comprehensive risk reports with recommendations
  - Support for quasi-identifier analysis

- **Progress Tracking and UX Module** (`progress.py`)
  - Real-time progress bars with ETA calculation
  - Status logging with timestamps and log levels
  - Operation timing and profiling
  - Context manager support for clean syntax
  - Iterator wrappers for easy integration
  - Multi-progress tracker for concurrent operations

### Changed
- Updated package version from 0.1.0 to 0.2.0
- Enhanced `__init__.py` to export new modules
- Improved PyPI packaging with `pyproject.toml`
- Updated README with comprehensive feature documentation
- Enhanced setup.py with better metadata and keywords

### Documentation
- Added FEATURE_ROADMAP.md with 50+ suggested future features
- Added NEW_FEATURES.md summarizing v0.2.0 additions
- Added DEPLOYMENT.md with complete PyPI deployment guide
- Added advanced_features_example.py demonstrating new capabilities
- Created comprehensive CHANGELOG.md
- Added .gitignore for cleaner repository
- Added LICENSE file (MIT)
- Added MANIFEST.in for proper package distribution

### Infrastructure
- Added pyproject.toml for modern Python packaging
- Created .pypirc.template for PyPI configuration
- Improved package structure for PyPI distribution

## [0.1.0] - 2025-12-22

### Added
- **Core De-identification Modules**
  - `DicomDeidentifier`: Remove/anonymize 50+ PHI tags from DICOM metadata
  - `TextRemover`: Remove burned-in text using OCR, cropping, or edge detection
  - `FormatConverter`: Convert DICOM to PNG, JPEG, TIFF, NumPy formats
  - `DeidentificationValidator`: Automated PHI detection and validation
  - `AuditLogger`: Comprehensive audit trails for compliance
  - `BatchProcessor`: End-to-end workflow orchestration

- **Features**
  - Date offsetting for temporal anonymization
  - Patient ID hashing for reversible anonymization
  - Selective field preservation (age, sex)
  - Custom PHI tag lists
  - Private tag removal
  - Overlay and curve data removal
  - DICOM windowing/leveling support
  - Validation sampling
  - Comprehensive reporting

- **Command-Line Interface**
  - Full CLI with argument parsing
  - Support for all major operations
  - Progress indicators
  - Report generation

- **Documentation**
  - README.md with installation and usage
  - USAGE_GUIDE.md with API reference
  - PACKAGE_SUMMARY.md with feature overview
  - INSTALLATION.md with setup instructions
  - Complete example scripts

- **Build Infrastructure**
  - setup.py for package installation
  - requirements.txt for dependencies
  - Example scripts demonstrating all features

### Dependencies
- pydicom >= 2.3.0
- numpy >= 1.20.0
- opencv-python >= 4.5.0
- Pillow >= 9.0.0
- pytesseract >= 0.3.9 (optional)

## [Unreleased]

### Planned for v0.3.0
- GPU acceleration for OCR and image processing
- Machine learning-based PHI detection
- Handwritten text detection
- PACS integration
- Visual validation dashboard
- REST API server
- NIFTI format support
- PDF report de-identification

### Under Consideration
- Distributed processing (Dask, Spark)
- Cloud storage integration (AWS, GCP, Azure)
- FHIR integration
- Multi-language OCR support
- Differential privacy
- Blockchain audit trails

---

## Version History

- **v0.2.0** (2025-12-28) - Face detection, risk assessment, progress tracking
- **v0.1.0** (2025-12-22) - Initial release with core de-identification features

## Links

- [PyPI Package](https://pypi.org/project/medimagecleaner/)
- [GitHub Repository](https://github.com/akinboye/medimagecleaner)
- [Documentation](https://github.com/akinboye/medimagecleaner#readme)
- [Issue Tracker](https://github.com/akinboye/medimagecleaner/issues)
