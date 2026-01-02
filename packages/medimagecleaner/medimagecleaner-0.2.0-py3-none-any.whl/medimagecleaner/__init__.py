"""
medimagecleaner - A comprehensive package for removing PHI from medical images

This package provides tools to:
- De-identify DICOM metadata
- Remove burned-in text from images
- Remove faces from medical images
- Convert DICOM to standard image formats
- Validate de-identification
- Assess re-identification risk
- Detect patient information (PHI)
- Audit and log anonymization steps
- Track progress for batch operations
"""

__version__ = "0.2.0"
__author__ = "Akinboye Yusuff"
__email__ = "mailakinboye@gmail.com"

from .dicom_deidentifier import DicomDeidentifier
from .text_remover import TextRemover
from .format_converter import FormatConverter
from .validator import DeidentificationValidator
from .audit_logger import AuditLogger
from .batch_processor import BatchProcessor
from .face_remover import FaceRemover
from .risk_assessment import RiskAssessment
from .progress import ProgressTracker, StatusLogger, Timer, with_progress
from .phi_detector import PHIDetector

__all__ = [
    "DicomDeidentifier",
    "TextRemover",
    "FormatConverter",
    "DeidentificationValidator",
    "AuditLogger",
    "BatchProcessor",
    "FaceRemover",
    "RiskAssessment",
    "ProgressTracker",
    "StatusLogger",
    "Timer",
    "with_progress",
    "PHIDetector",
]
