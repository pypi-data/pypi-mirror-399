"""
Advanced Features Example

Demonstrates new features including face removal, risk assessment,
and progress tracking.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from medimagecleaner import (
    FaceRemover,
    RiskAssessment,
    ProgressTracker,
    StatusLogger,
    Timer,
    with_progress,
)


def example_1_face_removal():
    """Example 1: Face Detection and Removal"""
    print("\n" + "=" * 60)
    print("Example 1: Face Detection and Removal")
    print("=" * 60)
    
    # Initialize face remover with different methods
    
    # Method 1: Blur faces
    blur_remover = FaceRemover(
        method="blur",
        blur_strength=25
    )
    
    # Method 2: Pixelate faces
    pixelate_remover = FaceRemover(
        method="pixelate",
        pixelate_size=10
    )
    
    # Method 3: Black box over faces
    box_remover = FaceRemover(
        method="black_box"
    )
    
    # Method 4: Inpainting (smart removal)
    inpaint_remover = FaceRemover(
        method="remove"
    )
    
    # Process a single image
    # result = blur_remover.process_image(
    #     "patient_photo.jpg",
    #     "patient_photo_deidentified.jpg"
    # )
    # print(f"✓ Detected {result['faces_detected']} face(s)")
    
    # Process DICOM with embedded photo
    # result = blur_remover.process_dicom(
    #     "whole_body_scan.dcm",
    #     "deidentified_scan.dcm"
    # )
    
    # Batch process directory
    # results = blur_remover.batch_process(
    #     input_dir="./clinical_photos",
    #     output_dir="./deidentified_photos",
    #     file_pattern="*.jpg"
    # )
    # print(f"Processed {results['successful']}/{results['total_files']} files")
    # print(f"Total faces detected: {results['total_faces_detected']}")
    
    print("✓ Face removal examples ready")


def example_2_risk_assessment():
    """Example 2: Re-identification Risk Assessment"""
    print("\n" + "=" * 60)
    print("Example 2: Re-identification Risk Assessment")
    print("=" * 60)
    
    # Initialize risk assessment
    risk_assessor = RiskAssessment(strict_mode=True)
    
    # Assess a single DICOM file
    # file_risk = risk_assessor.assess_dicom_file("deidentified.dcm")
    # print(f"Risk Level: {file_risk['risk_level']}")
    # print(f"Risk Score: {file_risk['risk_score']}/100")
    # if file_risk['remaining_phi']:
    #     print(f"⚠️ Remaining PHI: {file_risk['remaining_phi']}")
    
    # Assess entire dataset
    # dataset_risk = risk_assessor.assess_dataset(
    #     input_dir="./deidentified_dataset",
    #     recursive=True,
    #     sample_size=1000  # Analyze 1000 random files
    # )
    
    # print(f"\nDataset Risk Assessment:")
    # print(f"  Overall Risk: {dataset_risk['overall_risk_level']}")
    # print(f"  Files Analyzed: {dataset_risk['files_analyzed']}")
    # print(f"  K-anonymity: {dataset_risk['k_anonymity']['k_value']}")
    # print(f"  Uniqueness: {dataset_risk['uniqueness']['uniqueness_percentage']:.1f}%")
    
    # Print recommendations
    # print("\nRecommendations:")
    # for rec in dataset_risk['recommendations']:
    #     print(f"  • {rec}")
    
    # Generate detailed report
    # report = risk_assessor.generate_report(
    #     dataset_risk,
    #     "risk_assessment_report.txt"
    # )
    # print(f"\n✓ Report saved to risk_assessment_report.txt")
    
    print("✓ Risk assessment examples ready")


def example_3_progress_tracking():
    """Example 3: Progress Tracking"""
    print("\n" + "=" * 60)
    print("Example 3: Progress Tracking")
    print("=" * 60)
    
    import time
    
    # Basic progress bar
    print("\n1. Basic Progress Bar:")
    tracker = ProgressTracker(
        total=50,
        description="Processing files",
        show_eta=True
    )
    
    for i in range(50):
        time.sleep(0.02)  # Simulate work
        tracker.update()
    
    tracker.finish()
    
    # Using context manager
    print("\n2. Progress with Context Manager:")
    with ProgressTracker(30, "Converting formats") as tracker:
        for i in range(30):
            time.sleep(0.02)
            tracker.update()
    
    # Using with_progress wrapper
    print("\n3. Progress Wrapper:")
    files = range(25)
    for file in with_progress(files, "Validating"):
        time.sleep(0.02)  # Simulate work
    
    print("\n✓ Progress tracking demonstrated")


def example_4_status_logging():
    """Example 4: Status Logging"""
    print("\n" + "=" * 60)
    print("Example 4: Status Logging")
    print("=" * 60)
    
    logger = StatusLogger(
        show_timestamp=True,
        show_level=True
    )
    
    logger.info("Starting de-identification process")
    logger.info("Loading DICOM files from directory")
    logger.success("Successfully loaded 150 files")
    logger.warning("3 files have validation warnings")
    logger.success("Metadata de-identification complete")
    logger.info("Starting text removal")
    logger.error("Failed to process 2 files - corrupt DICOM")
    logger.success("Process completed")
    
    print("\n✓ Status logging demonstrated")


def example_5_timer():
    """Example 5: Operation Timing"""
    print("\n" + "=" * 60)
    print("Example 5: Operation Timing")
    print("=" * 60)
    
    import time
    
    # Using context manager
    with Timer("Batch de-identification"):
        time.sleep(1.5)  # Simulate work
    
    # Manual start/stop
    timer = Timer("Risk assessment")
    timer.start()
    time.sleep(0.8)  # Simulate work
    elapsed = timer.stop()
    
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print("\n✓ Timing demonstrated")


def example_6_complete_workflow_with_tracking():
    """Example 6: Complete Workflow with Progress and Risk Assessment"""
    print("\n" + "=" * 60)
    print("Example 6: Complete Workflow with Advanced Features")
    print("=" * 60)
    
    from medimagecleaner import BatchProcessor
    
    logger = StatusLogger()
    
    # Step 1: Initialize
    logger.info("Initializing batch processor")
    processor = BatchProcessor(
        log_dir="./logs",
        enable_logging=True,
        enable_validation=True
    )
    
    # Step 2: Process with progress tracking
    # logger.info("Starting de-identification")
    # with Timer("De-identification"):
    #     results = processor.process_directory(
    #         input_dir="./raw_data",
    #         output_dir="./deidentified",
    #         remove_metadata=True,
    #         remove_burned_text=True,
    #         validate_output=True
    #     )
    
    # logger.success(f"Processed {results['successful']}/{results['total_files']} files")
    
    # Step 3: Remove faces
    # logger.info("Removing faces from images")
    # face_remover = FaceRemover(method="blur")
    # with Timer("Face removal"):
    #     face_results = face_remover.batch_process(
    #         input_dir="./deidentified",
    #         output_dir="./deidentified",  # Overwrite
    #         file_pattern="*.dcm"
    #     )
    # logger.success(f"Removed {face_results['total_faces_detected']} faces")
    
    # Step 4: Risk assessment
    # logger.info("Performing risk assessment")
    # risk_assessor = RiskAssessment(strict_mode=True)
    # with Timer("Risk assessment"):
    #     risk = risk_assessor.assess_dataset("./deidentified")
    
    # logger.info(f"Risk Level: {risk['overall_risk_level']}")
    
    # if risk['overall_risk_level'] == 'HIGH':
    #     logger.error("⚠️ HIGH RISK detected - do not share dataset")
    # elif risk['overall_risk_level'] == 'MEDIUM':
    #     logger.warning("MEDIUM RISK - review recommendations")
    # else:
    #     logger.success("✓ LOW RISK - dataset appears safe")
    
    # # Generate report
    # logger.info("Generating comprehensive report")
    # risk_assessor.generate_report(risk, "./risk_report.txt")
    # processor.generate_complete_report(results, "./workflow_report.txt")
    
    # logger.success("✓ Complete workflow finished")
    
    print("✓ Complete workflow example ready")


def example_7_k_anonymity_calculation():
    """Example 7: Understanding K-Anonymity"""
    print("\n" + "=" * 60)
    print("Example 7: K-Anonymity Analysis")
    print("=" * 60)
    
    # Sample dataset (in real use, this comes from DICOM files)
    sample_records = [
        {"PatientAge": "45", "PatientSex": "M", "Modality": "CT"},
        {"PatientAge": "45", "PatientSex": "M", "Modality": "CT"},
        {"PatientAge": "45", "PatientSex": "M", "Modality": "CT"},
        {"PatientAge": "52", "PatientSex": "F", "Modality": "MR"},
        {"PatientAge": "52", "PatientSex": "F", "Modality": "MR"},
        {"PatientAge": "38", "PatientSex": "M", "Modality": "CT"},  # Unique!
    ]
    
    risk_assessor = RiskAssessment()
    
    # Calculate k-anonymity
    k_result = risk_assessor.calculate_k_anonymity(sample_records)
    
    print(f"K-value: {k_result['k_value']}")
    print(f"This means: Each record is indistinguishable from at least")
    print(f"            {k_result['k_value']-1} other record(s)")
    print(f"Threshold: {k_result['k_threshold']} (recommended minimum)")
    print(f"Meets threshold: {'✓ YES' if k_result['meets_threshold'] else '✗ NO'}")
    print(f"\nEquivalence classes: {k_result['num_equivalence_classes']}")
    print(f"Risky records: {k_result['risky_records']} ({k_result['risk_percentage']:.1f}%)")
    
    print("\n✓ K-anonymity analysis demonstrated")


def main():
    """Run all advanced feature examples"""
    print("\n" + "=" * 60)
    print("MEDIMAGECLEANER - Advanced Features Examples")
    print("=" * 60)
    print("\nVersion 0.2.0 - New Features:")
    print("• Face Detection and Removal")
    print("• Re-identification Risk Assessment")
    print("• Progress Tracking")
    print("• Status Logging")
    print("• Operation Timing\n")
    
    # Run all examples
    example_1_face_removal()
    example_2_risk_assessment()
    example_3_progress_tracking()
    example_4_status_logging()
    example_5_timer()
    example_6_complete_workflow_with_tracking()
    example_7_k_anonymity_calculation()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Review the FEATURE_ROADMAP.md for upcoming features")
    print("2. Try face removal on clinical photos")
    print("3. Run risk assessment on your de-identified dataset")
    print("4. Use progress tracking for large batch operations")
    print("\nFor questions or feedback:")
    print("  • GitHub Issues")
    print("  • Email: contact@example.com")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
