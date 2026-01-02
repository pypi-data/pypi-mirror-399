"""
PHI Detection Example

Demonstrates how to check for patient information in DICOM files
WITHOUT modifying them.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from medimagecleaner import PHIDetector


def example_1_check_single_file():
    """Example 1: Check a single DICOM file for PHI"""
    print("\n" + "=" * 60)
    print("Example 1: Check Single File for PHI")
    print("=" * 60)
    
    # Initialize PHI detector
    detector = PHIDetector(
        enable_ocr=True,              # Check for burned-in text
        enable_face_detection=True,   # Check for faces
        enable_risk_assessment=True   # Calculate risk score
    )
    
    # Check a file (uncomment to use with real DICOM)
    # report = detector.check_file("patient_scan.dcm")
    
    # print(f"\nFile: {report['file']}")
    # print(f"PHI Detected: {'YES ✗' if report['phi_detected'] else 'NO ✓'}")
    # print(f"\nSummary:")
    # print(f"  • Metadata PHI: {'Found ✗' if report['summary']['has_metadata_phi'] else 'Clean ✓'}")
    # print(f"  • Burned-in Text: {'Found ✗' if report['summary']['has_burned_text'] else 'Clean ✓'}")
    # print(f"  • Faces: {'Found ✗' if report['summary']['has_faces'] else 'Clean ✓'}")
    # print(f"  • Risk Level: {report['summary']['overall_risk']}")
    
    # # Detailed metadata PHI
    # if report['metadata_phi']['phi_tags_found']:
    #     print(f"\nMetadata PHI Details:")
    #     for tag in report['metadata_phi']['phi_tags_found']:
    #         print(f"  • {tag['tag']}: {tag['value']}")
    
    # # Detected text
    # if report['burned_in_text'].get('text_found'):
    #     print(f"\nBurned-in Text Found:")
    #     for text in report['burned_in_text']['text_found']:
    #         print(f"  • '{text['text']}' (confidence: {text['confidence']:.1f}%)")
    
    # # Detected faces
    # if report['faces'].get('faces_found'):
    #     print(f"\nFaces Detected: {report['faces']['total_faces']}")
    #     for i, face in enumerate(report['faces']['faces_found'], 1):
    #         print(f"  • Face {i}: Location {face['location']}, Size {face['size']}")
    
    # # Generate detailed report
    # detailed_report = detector.generate_report(report, "phi_check_report.txt")
    # print(f"\n✓ Detailed report saved to phi_check_report.txt")
    
    print("✓ Example code ready (add your DICOM files to test)")


def example_2_batch_check():
    """Example 2: Check entire directory for PHI"""
    print("\n" + "=" * 60)
    print("Example 2: Batch Check Directory")
    print("=" * 60)
    
    detector = PHIDetector()
    
    # Check entire directory
    # results = detector.check_directory(
    #     input_dir="./dicom_files",
    #     recursive=True,
    #     sample_rate=1.0  # Check all files (use 0.1 for 10% sample)
    # )
    
    # print(f"\nBatch Check Results:")
    # print(f"  Total Files: {results['total_files']}")
    # print(f"  Files Checked: {results['files_checked']}")
    # print(f"  Files with PHI: {results['files_with_phi']}")
    # print(f"  Clean Files: {results['files_clean']}")
    
    # print(f"\nPHI Type Breakdown:")
    # print(f"  • Files with Metadata PHI: {results['summary']['metadata_phi_count']}")
    # print(f"  • Files with Burned-in Text: {results['summary']['burned_text_count']}")
    # print(f"  • Files with Faces: {results['summary']['faces_count']}")
    # print(f"  • High Risk Files: {results['summary']['high_risk_count']}")
    
    # # Generate batch report
    # report = detector.generate_report(results, "batch_phi_report.txt")
    # print(f"\n✓ Batch report saved to batch_phi_report.txt")
    
    print("✓ Example code ready for batch checking")


def example_3_metadata_only_check():
    """Example 3: Quick metadata-only check (no OCR/face detection)"""
    print("\n" + "=" * 60)
    print("Example 3: Quick Metadata Check")
    print("=" * 60)
    
    # Faster check - metadata only
    detector = PHIDetector(
        enable_ocr=False,              # Skip OCR
        enable_face_detection=False,   # Skip face detection
        enable_risk_assessment=True
    )
    
    # report = detector.check_file("scan.dcm")
    
    # print(f"Quick Check Results:")
    # print(f"  Metadata PHI: {'Found ✗' if report['summary']['has_metadata_phi'] else 'Clean ✓'}")
    # print(f"  Risk Level: {report['summary']['overall_risk']}")
    
    # if report['metadata_phi']['phi_tags_found']:
    #     print(f"\nPHI Tags Found:")
    #     for tag in report['metadata_phi']['phi_tags_found']:
    #         print(f"  • {tag['tag']}: {tag['value'][:30]}...")  # Truncated
    
    print("✓ Quick check example ready")


def example_4_pre_deidentification_check():
    """Example 4: Check files before de-identification"""
    print("\n" + "=" * 60)
    print("Example 4: Pre-Deidentification Workflow")
    print("=" * 60)
    
    from medimagecleaner import PHIDetector, BatchProcessor
    
    detector = PHIDetector()
    
    # Step 1: Check what PHI exists
    # print("Step 1: Checking for PHI...")
    # check_results = detector.check_directory("./raw_data")
    
    # if check_results['files_with_phi'] > 0:
    #     print(f"⚠️  Found PHI in {check_results['files_with_phi']} files")
    #     print(f"   • Metadata PHI: {check_results['summary']['metadata_phi_count']} files")
    #     print(f"   • Burned-in Text: {check_results['summary']['burned_text_count']} files")
    #     print(f"   • Faces: {check_results['summary']['faces_count']} files")
    #     
    #     # Step 2: De-identify based on findings
    #     print("\nStep 2: De-identifying...")
    #     processor = BatchProcessor()
    #     
    #     deidentify_results = processor.process_directory(
    #         input_dir="./raw_data",
    #         output_dir="./deidentified",
    #         remove_metadata=True,
    #         remove_burned_text=(check_results['summary']['burned_text_count'] > 0),
    #         validate_output=True
    #     )
    #     
    #     # Step 3: Verify PHI removed
    #     print("\nStep 3: Verifying PHI removal...")
    #     verify_results = detector.check_directory("./deidentified")
    #     
    #     if verify_results['files_with_phi'] == 0:
    #         print("✓ All PHI successfully removed!")
    #     else:
    #         print(f"⚠️  PHI still found in {verify_results['files_with_phi']} files")
    #         print("   Manual review required.")
    
    print("✓ Pre-deidentification workflow example ready")


def example_5_individual_checks():
    """Example 5: Use individual detection methods"""
    print("\n" + "=" * 60)
    print("Example 5: Individual Detection Methods")
    print("=" * 60)
    
    # You can also use the individual components directly
    from medimagecleaner import (
        DeidentificationValidator,
        TextRemover,
        FaceRemover,
        RiskAssessment
    )
    
    # import pydicom
    # ds = pydicom.dcmread("scan.dcm")
    
    # # Check 1: Metadata validation
    # validator = DeidentificationValidator()
    # validation = validator.validate_dicom(ds)
    # print(f"Metadata Check: {'✗ PHI Found' if not validation['passed'] else '✓ Clean'}")
    
    # # Check 2: Text detection
    # text_remover = TextRemover(ocr_enabled=True)
    # pixel_array = ds.pixel_array
    # text_regions = text_remover.detect_text_ocr(pixel_array)
    # print(f"Text Check: Found {len(text_regions)} text region(s)")
    
    # # Check 3: Face detection
    # face_remover = FaceRemover()
    # faces = face_remover.detect_faces_haar(pixel_array)
    # print(f"Face Check: Found {len(faces)} face(s)")
    
    # # Check 4: Risk assessment
    # risk = RiskAssessment()
    # assessment = risk.assess_dicom_file(ds)
    # print(f"Risk Assessment: {assessment['risk_level']} ({assessment['risk_score']}/100)")
    
    print("✓ Individual check methods demonstrated")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("PHI DETECTION EXAMPLES")
    print("=" * 60)
    print("\nThese examples show how to CHECK for patient information")
    print("in medical images WITHOUT modifying the files.\n")
    
    # Run all examples
    example_1_check_single_file()
    example_2_batch_check()
    example_3_metadata_only_check()
    example_4_pre_deidentification_check()
    example_5_individual_checks()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nKey Features:")
    print("  ✓ Detect metadata PHI (50+ DICOM tags)")
    print("  ✓ Detect burned-in text using OCR")
    print("  ✓ Detect faces in images")
    print("  ✓ Calculate re-identification risk")
    print("  ✓ Generate detailed reports")
    print("  ✓ Batch checking support")
    print("\nNext Steps:")
    print("  1. Add your DICOM files")
    print("  2. Run PHI detection")
    print("  3. Review reports")
    print("  4. De-identify as needed")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
