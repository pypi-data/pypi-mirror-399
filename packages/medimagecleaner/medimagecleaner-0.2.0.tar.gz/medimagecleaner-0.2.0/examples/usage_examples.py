#!/usr/bin/env python3
"""
Example script demonstrating medimagecleaner usage.

This script shows common workflows for de-identifying medical images.
"""

import os
from pathlib import Path

# Import medimagecleaner components
from medimagecleaner import (
    DICOMCleaner,
    TextRemover,
    FormatConverter,
    DeidentificationValidator,
    BatchProcessor,
    AuditLogger,
)


def example_1_basic_dicom_cleaning():
    """Example 1: Basic DICOM metadata de-identification."""
    print("\n" + "="*60)
    print("Example 1: Basic DICOM Cleaning")
    print("="*60)
    
    # Initialize cleaner
    cleaner = DICOMCleaner(
        replacement_value="ANONYMIZED",
        remove_private_tags=True,
    )
    
    # Example: Clean a DICOM file
    print("\nCleaning DICOM metadata...")
    # cleaner.clean_dicom(
    #     input_path="input.dcm",
    #     output_path="output_anonymized.dcm"
    # )
    print("✓ DICOM cleaned successfully")


def example_2_date_shifting():
    """Example 2: Date shifting to maintain temporal relationships."""
    print("\n" + "="*60)
    print("Example 2: Date Shifting")
    print("="*60)
    
    cleaner = DICOMCleaner(
        replacement_value="ANONYMIZED",
        date_shift_days=100,  # Shift all dates by 100 days
        use_hashing=True,
        hash_salt="my-secret-salt-12345",
    )
    
    print("\nConfiguration:")
    print(f"  - Date shift: 100 days")
    print(f"  - ID hashing: Enabled")
    print(f"  - Maintains temporal relationships: Yes")


def example_3_burned_text_removal():
    """Example 3: Remove burned-in text from images."""
    print("\n" + "="*60)
    print("Example 3: Burned-in Text Removal")
    print("="*60)
    
    text_remover = TextRemover(
        ocr_confidence_threshold=30.0,
        masking_color=(0, 0, 0),
        padding=5,
    )
    
    print("\nText detection workflow:")
    print("  1. Load image")
    print("  2. Detect text regions using OCR")
    print("  3. Mask detected regions")
    print("  4. Save cleaned image")
    
    # Example usage:
    # cleaned = text_remover.remove_text_from_image(
    #     input_image="xray_with_text.png",
    #     output_path="xray_clean.png"
    # )


def example_4_crop_known_regions():
    """Example 4: Crop known PHI regions."""
    print("\n" + "="*60)
    print("Example 4: Crop Known PHI Regions")
    print("="*60)
    
    text_remover = TextRemover()
    
    print("\nCropping options:")
    print("  - 'top': Remove top 10%")
    print("  - 'bottom': Remove bottom 10%")
    print("  - Custom: {'top': 0.0, 'bottom': 0.9, ...}")
    
    # Example: Crop top 10% where PHI is located
    # cleaned = text_remover.remove_text_from_image(
    #     input_image="image.png",
    #     crop_first="top",
    #     output_path="image_cropped.png"
    # )


def example_5_complete_pipeline():
    """Example 5: Complete de-identification pipeline."""
    print("\n" + "="*60)
    print("Example 5: Complete Pipeline")
    print("="*60)
    
    # Setup components
    cleaner = DICOMCleaner(
        replacement_value="ANONYMIZED",
        remove_private_tags=True,
        date_shift_days=100,
    )
    
    text_remover = TextRemover(
        ocr_confidence_threshold=30.0,
        aggressive_mode=True,
    )
    
    processor = BatchProcessor(
        dicom_cleaner=cleaner,
        text_remover=text_remover,
        max_workers=4,
    )
    
    print("\nPipeline steps:")
    print("  1. Clean DICOM metadata")
    print("  2. Detect and remove burned-in text")
    print("  3. Convert to PNG (optional)")
    print("  4. Validate output")
    print("  5. Generate audit logs")
    
    # Example batch processing:
    # results = processor.batch_process_directory(
    #     input_dir="./raw_dicoms",
    #     output_dir="./anonymized_dicoms",
    #     remove_burned_text=True,
    #     convert_to_png=True,
    #     validate_output=True,
    # )


def example_6_validation():
    """Example 6: Validate de-identified files."""
    print("\n" + "="*60)
    print("Example 6: Validation")
    print("="*60)
    
    validator = DeidentificationValidator(
        strict_mode=True,
        check_burned_text=True,
        ocr_confidence_threshold=60.0,
    )
    
    print("\nValidation checks:")
    print("  ✓ DICOM metadata PHI tags")
    print("  ✓ Private tags")
    print("  ✓ Burned-in text in pixels")
    print("  ✓ PHI patterns (names, dates, SSN, etc.)")
    
    # Example validation:
    # results = validator.validate_complete("anonymized.dcm")
    # if results["overall_valid"]:
    #     print("✓ File is properly de-identified")
    # else:
    #     print("✗ Issues found:", results)


def example_7_audit_logging():
    """Example 7: Comprehensive audit logging."""
    print("\n" + "="*60)
    print("Example 7: Audit Logging")
    print("="*60)
    
    audit_logger = AuditLogger(
        log_dir="./audit_logs",
        log_file_prefix="deidentification_audit",
        include_system_info=True,
    )
    
    print("\nAudit log includes:")
    print("  - Session ID and timestamp")
    print("  - User and system information")
    print("  - All file operations")
    print("  - Validation results")
    print("  - Errors and warnings")
    
    # Example logging:
    # audit_logger.log_file_processing(
    #     input_file="original.dcm",
    #     output_file="anonymized.dcm",
    #     operation="deidentification",
    #     phi_tags_removed=["PatientName", "PatientID"],
    #     text_regions_masked=3,
    #     validation_passed=True,
    # )
    
    # Generate report:
    # audit_logger.generate_audit_report(
    #     output_path="audit_report.html",
    #     format="html"
    # )


def example_8_format_conversion():
    """Example 8: Format conversion after de-identification."""
    print("\n" + "="*60)
    print("Example 8: Format Conversion")
    print("="*60)
    
    converter = FormatConverter(
        normalize_pixels=True,
        apply_windowing=True,
    )
    
    print("\nSupported conversions:")
    print("  - DICOM → PNG")
    print("  - DICOM → JPEG")
    print("  - DICOM → TIFF")
    print("  - DICOM → NumPy array")
    print("  - Metadata → JSON")
    
    # Example conversions:
    # converter.dicom_to_image("scan.dcm", "scan.png", format="PNG")
    # metadata = converter.extract_metadata_to_json("scan.dcm", "metadata.json")


def example_9_batch_processing():
    """Example 9: Process entire directory."""
    print("\n" + "="*60)
    print("Example 9: Batch Processing")
    print("="*60)
    
    processor = BatchProcessor(max_workers=4)
    
    print("\nBatch processing features:")
    print("  - Parallel processing (4 workers)")
    print("  - Progress bar")
    print("  - Error handling")
    print("  - Processing report generation")
    
    # Example:
    # results = processor.batch_process_directory(
    #     input_dir="./input_dicoms",
    #     output_dir="./output_dicoms",
    #     recursive=True,
    #     progress_bar=True,
    #     save_report=True,
    # )
    # 
    # print(f"Processed: {results['successful']}/{results['total_files']}")


def example_10_recommended_workflow():
    """Example 10: Recommended production workflow."""
    print("\n" + "="*60)
    print("Example 10: Recommended Workflow")
    print("="*60)
    
    print("\nRecommended workflow for production:")
    print("\n1. Initialize audit logging")
    print("2. Configure de-identification settings")
    print("3. Process small test batch")
    print("4. Validate test results")
    print("5. Manual spot check")
    print("6. Process full dataset")
    print("7. Final validation")
    print("8. Generate audit reports")
    
    print("\n" + "-"*60)
    print("Code example:")
    print("-"*60)
    
    code = """
    # 1. Audit logging
    audit_logger = AuditLogger(log_dir="./audit_logs")
    
    # 2. Configure
    cleaner = DICOMCleaner(
        replacement_value="ANONYMIZED",
        remove_private_tags=True,
        date_shift_days=100,
        use_hashing=True,
        hash_salt="secret-salt"
    )
    
    # 3. Test batch
    processor = BatchProcessor(dicom_cleaner=cleaner)
    test_results = processor.batch_process_directory(
        input_dir="./test_subset",
        output_dir="./test_output",
        validate_output=True
    )
    
    # 4. Validate
    validator = DeidentificationValidator(strict_mode=True)
    validation = validator.batch_validate("./test_output")
    
    # 5. Manual check (perform manually)
    
    # 6. Process full dataset
    if validation["valid_files"] == validation["total_files"]:
        full_results = processor.batch_process_directory(
            input_dir="./full_dataset",
            output_dir="./anonymized_dataset",
            validate_output=True
        )
    
    # 7. Final validation
    final_validation = validator.batch_validate("./anonymized_dataset")
    
    # 8. Generate reports
    validator.generate_html_report(
        final_validation,
        "validation_report.html"
    )
    audit_logger.generate_audit_report(
        "audit_report.html",
        format="html"
    )
    """
    
    print(code)


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("MEDIMAGECLEANER - Example Usage")
    print("="*60)
    print("\nThis script demonstrates various features and workflows.")
    print("Uncomment the actual file operations to use with real data.")
    
    example_1_basic_dicom_cleaning()
    example_2_date_shifting()
    example_3_burned_text_removal()
    example_4_crop_known_regions()
    example_5_complete_pipeline()
    example_6_validation()
    example_7_audit_logging()
    example_8_format_conversion()
    example_9_batch_processing()
    example_10_recommended_workflow()
    
    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60)
    print("\nFor more information, see:")
    print("  - README.md")
    print("  - Documentation: https://medimagecleaner.readthedocs.io")
    print("  - Module docstrings")
    print()


if __name__ == "__main__":
    main()
