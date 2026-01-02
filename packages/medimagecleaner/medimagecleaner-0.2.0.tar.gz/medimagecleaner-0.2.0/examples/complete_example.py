"""
Complete Example: De-identifying Medical Images

This example demonstrates a complete workflow for de-identifying
medical images using the medimagecleaner package.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from medimagecleaner import (
    DicomDeidentifier,
    TextRemover,
    FormatConverter,
    DeidentificationValidator,
    AuditLogger,
    BatchProcessor,
)


def example_1_basic_metadata_removal():
    """Example 1: Basic DICOM metadata de-identification"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Metadata De-identification")
    print("=" * 60)
    
    # Initialize de-identifier
    deidentifier = DicomDeidentifier(
        replacement_value="ANONYMIZED",
        hash_patient_id=True,
        preserve_age=True,
        preserve_sex=True
    )
    
    # De-identify a single file
    # Note: Replace with actual file path
    # result = deidentifier.deidentify(
    #     input_path="sample_data/patient_scan.dcm",
    #     output_path="output/anonymized_scan.dcm",
    #     remove_private_tags=True
    # )
    
    # print(f"✓ Modified {len(result['changes']['tags_modified'])} tags")
    # print(f"✓ Removed {result['changes']['private_tags_removed']} private tags")
    
    print("✓ Example code ready (add your DICOM files to test)")


def example_2_burned_text_removal():
    """Example 2: Remove burned-in text from images"""
    print("\n" + "=" * 60)
    print("Example 2: Burned-in Text Removal")
    print("=" * 60)
    
    # Initialize text remover with OCR
    text_remover = TextRemover(
        ocr_enabled=True,
        confidence_threshold=30.0,
        padding=5
    )
    
    # Method 1: OCR-based text detection
    # result = text_remover.process_dicom(
    #     input_path="sample_data/scan_with_text.dcm",
    #     output_path="output/scan_no_text.dcm",
    #     method="ocr"
    # )
    
    # Method 2: Crop known regions
    # result = text_remover.process_dicom(
    #     input_path="sample_data/scan.dcm",
    #     output_path="output/cropped.dcm",
    #     method="crop",
    #     crop_top=0.1,  # Remove top 10%
    #     crop_bottom=0.05
    # )
    
    print("✓ Example code ready for text removal")


def example_3_format_conversion():
    """Example 3: Convert DICOM to standard formats"""
    print("\n" + "=" * 60)
    print("Example 3: Format Conversion")
    print("=" * 60)
    
    # Initialize converter
    converter = FormatConverter(
        normalize=True,
        apply_windowing=True,
        resize=(512, 512)  # Optional
    )
    
    # Convert to PNG
    # converter.dicom_to_png(
    #     input_path="output/anonymized_scan.dcm",
    #     output_path="output/scan.png"
    # )
    
    # Convert to JPEG
    # converter.dicom_to_jpg(
    #     input_path="output/anonymized_scan.dcm",
    #     output_path="output/scan.jpg",
    #     quality=95
    # )
    
    # Batch conversion
    # results = converter.batch_convert(
    #     input_dir="output",
    #     output_dir="output/png",
    #     output_format="png"
    # )
    
    print("✓ Example code ready for format conversion")


def example_4_validation():
    """Example 4: Validate de-identified files"""
    print("\n" + "=" * 60)
    print("Example 4: Validation")
    print("=" * 60)
    
    # Initialize validator
    validator = DeidentificationValidator(
        strict_mode=True,
        check_private_tags=True
    )
    
    # Validate single file
    # validation = validator.validate_dicom("output/anonymized_scan.dcm")
    # if validation['passed']:
    #     print("✓ Validation PASSED")
    # else:
    #     print("✗ Validation FAILED")
    #     for failure in validation['failures']:
    #         print(f"  - {failure}")
    
    # Batch validation
    # results = validator.validate_batch(
    #     input_dir="output",
    #     sample_rate=0.2  # Validate 20% of files
    # )
    
    # Generate report
    # report = validator.generate_report(
    #     results,
    #     output_path="output/validation_report.txt"
    # )
    
    print("✓ Example code ready for validation")


def example_5_complete_workflow():
    """Example 5: Complete workflow using BatchProcessor"""
    print("\n" + "=" * 60)
    print("Example 5: Complete Workflow")
    print("=" * 60)
    
    # Initialize batch processor
    processor = BatchProcessor(
        log_dir="./logs",
        enable_logging=True,
        enable_validation=True
    )
    
    # Process entire directory with all steps
    # results = processor.process_directory(
    #     input_dir="sample_data",
    #     output_dir="output/complete",
    #     remove_metadata=True,
    #     remove_burned_text=True,
    #     convert_format="png",  # Optional: convert to PNG
    #     text_removal_method="ocr",
    #     validate_output=True,
    #     recursive=True
    # )
    
    # Generate comprehensive report
    # report = processor.generate_complete_report(
    #     results,
    #     output_path="output/workflow_report.txt"
    # )
    
    # print("\nWorkflow Summary:")
    # print(f"  Total Files: {results['total_files']}")
    # print(f"  Successful: {results['successful']}")
    # print(f"  Failed: {results['failed']}")
    
    print("✓ Example code ready for complete workflow")


def example_6_audit_logging():
    """Example 6: Audit logging and compliance"""
    print("\n" + "=" * 60)
    print("Example 6: Audit Logging")
    print("=" * 60)
    
    # Initialize logger
    logger = AuditLogger(
        log_dir="./audit_logs",
        create_hash_mapping=True
    )
    
    # Logging is usually automatic with BatchProcessor,
    # but you can log manually:
    # logger.log_deidentification(
    #     file_path="scan.dcm",
    #     original_patient_id="12345",
    #     anonymized_patient_id="abc123def",
    #     tags_modified=["PatientName", "PatientID"],
    #     method="metadata"
    # )
    
    # Export ID mapping for secure storage
    # logger.export_mapping(
    #     output_path="./secure/id_mapping.json"
    # )
    
    # Create session report
    # report = logger.create_session_report(
    #     output_path="./audit_logs/session_report.txt"
    # )
    
    print("✓ Example code ready for audit logging")


def example_7_custom_workflow():
    """Example 7: Custom multi-step workflow"""
    print("\n" + "=" * 60)
    print("Example 7: Custom Workflow")
    print("=" * 60)
    
    # Step 1: De-identify metadata
    deidentifier = DicomDeidentifier(
        date_offset_days=365,  # Offset dates by 1 year
        hash_patient_id=True
    )
    
    # result1 = deidentifier.deidentify(
    #     "sample.dcm",
    #     "step1_metadata_removed.dcm"
    # )
    
    # Step 2: Remove burned-in text
    text_remover = TextRemover(ocr_enabled=True)
    # result2 = text_remover.process_dicom(
    #     "step1_metadata_removed.dcm",
    #     "step2_text_removed.dcm",
    #     method="ocr"
    # )
    
    # Step 3: Validate
    validator = DeidentificationValidator(strict_mode=True)
    # validation = validator.validate_dicom("step2_text_removed.dcm")
    
    # Step 4: Convert to PNG if validation passed
    # if validation['passed']:
    #     converter = FormatConverter()
    #     converter.dicom_to_png(
    #         "step2_text_removed.dcm",
    #         "final_output.png"
    #     )
    #     print("✓ Workflow complete!")
    
    print("✓ Example code ready for custom workflow")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("MEDIMAGECLEANER - Complete Examples")
    print("=" * 60)
    print("\nThese examples demonstrate all features of medimagecleaner.")
    print("Uncomment the actual processing code and add your DICOM files to test.\n")
    
    # Run all examples
    example_1_basic_metadata_removal()
    example_2_burned_text_removal()
    example_3_format_conversion()
    example_4_validation()
    example_5_complete_workflow()
    example_6_audit_logging()
    example_7_custom_workflow()
    
    print("\n" + "=" * 60)
    print("All examples loaded successfully!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Add DICOM files to sample_data/")
    print("2. Uncomment the processing code in each example")
    print("3. Run this script to test the workflows")
    print("\nFor production use, always:")
    print("  ✓ Keep original data separately")
    print("  ✓ Enable validation")
    print("  ✓ Enable audit logging")
    print("  ✓ Review validation reports")
    print("  ✓ Manually spot-check sample files")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
