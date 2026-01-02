"""
DICOM Tag Extractor and Processor

This script demonstrates how to use the medimagecleaner package to:
1. Read and display DICOM tags
2. Detect PHI in tags
3. De-identify DICOM files
4. Compare tags before and after de-identification
5. Export tags to various formats (JSON, CSV, TXT)
"""

import sys
from pathlib import Path
import json
import csv
from typing import Dict, List, Optional, Union

# Add parent directory for imports if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pydicom
    from pydicom.tag import Tag
    from medimagecleaner import (
        DicomDeidentifier,
        PHIDetector,
        DeidentificationValidator,
        RiskAssessment
    )
except ImportError as e:
    print(f"Error: {e}")
    print("Please install required packages: pip install pydicom medimagecleaner")
    sys.exit(1)


class DicomTagProcessor:
    """Process and manage DICOM tags with PHI detection and de-identification."""
    
    def __init__(self):
        """Initialize the tag processor."""
        self.phi_detector = PHIDetector(
            enable_ocr=False,  # Focus on metadata
            enable_face_detection=False,
            enable_risk_assessment=True
        )
        self.validator = DeidentificationValidator()
        self.deidentifier = DicomDeidentifier()
    
    def read_all_tags(
        self,
        dicom_path: Union[str, Path]
    ) -> Dict[str, any]:
        """
        Read all DICOM tags from a file.
        
        Args:
            dicom_path: Path to DICOM file
        
        Returns:
            Dictionary of all tags with metadata
        """
        ds = pydicom.dcmread(str(dicom_path))
        
        tags_info = {
            "file_path": str(dicom_path),
            "total_tags": len(ds),
            "tags": []
        }
        
        for elem in ds:
            tag_info = {
                "tag": str(elem.tag),
                "tag_name": elem.name if hasattr(elem, 'name') else "Unknown",
                "vr": elem.VR if hasattr(elem, 'VR') else "Unknown",
                "value": str(elem.value),
                "keyword": elem.keyword if hasattr(elem, 'keyword') else "",
                "is_private": elem.tag.is_private,
            }
            tags_info["tags"].append(tag_info)
        
        return tags_info
    
    def get_phi_tags(
        self,
        dicom_path: Union[str, Path]
    ) -> Dict[str, any]:
        """
        Get only tags containing PHI.
        
        Args:
            dicom_path: Path to DICOM file
        
        Returns:
            Dictionary of PHI tags
        """
        ds = pydicom.dcmread(str(dicom_path))
        
        # List of common PHI tag names
        phi_tag_names = [
            "PatientName",
            "PatientID",
            "PatientBirthDate",
            "PatientBirthTime",
            "PatientSex",
            "PatientAge",
            "PatientSize",
            "PatientWeight",
            "PatientAddress",
            "PatientTelephoneNumbers",
            "PatientMotherBirthName",
            "MedicalRecordLocator",
            "EthnicGroup",
            "Occupation",
            "AdditionalPatientHistory",
            "PatientComments",
            "InstitutionName",
            "InstitutionAddress",
            "InstitutionCodeSequence",
            "ReferringPhysicianName",
            "ReferringPhysicianAddress",
            "ReferringPhysicianTelephoneNumbers",
            "PerformingPhysicianName",
            "NameOfPhysiciansReadingStudy",
            "OperatorsName",
            "StudyDate",
            "SeriesDate",
            "AcquisitionDate",
            "ContentDate",
            "StudyTime",
            "SeriesTime",
            "AcquisitionTime",
            "ContentTime",
            "AccessionNumber",
            "StudyID",
            "StudyDescription",
            "SeriesDescription",
            "RequestingPhysician",
            "RequestedProcedureDescription",
            "ScheduledProcedureStepDescription",
            "DeviceSerialNumber",
            "StationName",
        ]
        
        phi_tags = {
            "file_path": str(dicom_path),
            "phi_tags_found": [],
            "phi_count": 0,
        }
        
        for tag_name in phi_tag_names:
            if tag_name in ds:
                elem = ds.data_element(tag_name)
                value = str(elem.value)
                
                # Skip if value is empty or anonymized
                if value and value.upper() not in ["", "ANONYMIZED", "REMOVED", "UNKNOWN"]:
                    phi_tags["phi_tags_found"].append({
                        "tag": str(elem.tag),
                        "tag_name": tag_name,
                        "vr": elem.VR,
                        "value": value,
                        "keyword": elem.keyword,
                    })
        
        phi_tags["phi_count"] = len(phi_tags["phi_tags_found"])
        
        return phi_tags
    
    def get_standard_tags(
        self,
        dicom_path: Union[str, Path]
    ) -> Dict[str, any]:
        """
        Get commonly used DICOM tags organized by category.
        
        Args:
            dicom_path: Path to DICOM file
        
        Returns:
            Dictionary of categorized tags
        """
        ds = pydicom.dcmread(str(dicom_path))
        
        def get_tag_value(tag_name):
            """Safely get tag value."""
            try:
                if tag_name in ds:
                    return str(ds.data_element(tag_name).value)
                return None
            except:
                return None
        
        tags = {
            "file_path": str(dicom_path),
            "patient": {
                "name": get_tag_value("PatientName"),
                "id": get_tag_value("PatientID"),
                "birth_date": get_tag_value("PatientBirthDate"),
                "sex": get_tag_value("PatientSex"),
                "age": get_tag_value("PatientAge"),
            },
            "study": {
                "instance_uid": get_tag_value("StudyInstanceUID"),
                "date": get_tag_value("StudyDate"),
                "time": get_tag_value("StudyTime"),
                "description": get_tag_value("StudyDescription"),
                "accession_number": get_tag_value("AccessionNumber"),
                "study_id": get_tag_value("StudyID"),
            },
            "series": {
                "instance_uid": get_tag_value("SeriesInstanceUID"),
                "number": get_tag_value("SeriesNumber"),
                "description": get_tag_value("SeriesDescription"),
                "modality": get_tag_value("Modality"),
                "date": get_tag_value("SeriesDate"),
                "time": get_tag_value("SeriesTime"),
            },
            "image": {
                "sop_instance_uid": get_tag_value("SOPInstanceUID"),
                "sop_class_uid": get_tag_value("SOPClassUID"),
                "rows": get_tag_value("Rows"),
                "columns": get_tag_value("Columns"),
                "bits_allocated": get_tag_value("BitsAllocated"),
                "bits_stored": get_tag_value("BitsStored"),
                "photometric_interpretation": get_tag_value("PhotometricInterpretation"),
            },
            "equipment": {
                "manufacturer": get_tag_value("Manufacturer"),
                "model_name": get_tag_value("ManufacturerModelName"),
                "device_serial_number": get_tag_value("DeviceSerialNumber"),
                "software_versions": get_tag_value("SoftwareVersions"),
                "station_name": get_tag_value("StationName"),
            },
            "institution": {
                "name": get_tag_value("InstitutionName"),
                "address": get_tag_value("InstitutionAddress"),
            },
            "physicians": {
                "referring": get_tag_value("ReferringPhysicianName"),
                "performing": get_tag_value("PerformingPhysicianName"),
            },
        }
        
        return tags
    
    def compare_tags_before_after(
        self,
        original_path: Union[str, Path],
        deidentified_path: Union[str, Path]
    ) -> Dict[str, any]:
        """
        Compare tags before and after de-identification.
        
        Args:
            original_path: Path to original DICOM
            deidentified_path: Path to de-identified DICOM
        
        Returns:
            Comparison results
        """
        original_tags = self.get_phi_tags(original_path)
        deidentified_tags = self.get_phi_tags(deidentified_path)
        
        comparison = {
            "original_file": str(original_path),
            "deidentified_file": str(deidentified_path),
            "original_phi_count": original_tags["phi_count"],
            "deidentified_phi_count": deidentified_tags["phi_count"],
            "phi_removed": original_tags["phi_count"] - deidentified_tags["phi_count"],
            "removed_tags": [],
            "remaining_tags": deidentified_tags["phi_tags_found"],
        }
        
        # Find which tags were removed
        original_tag_names = {tag["tag_name"] for tag in original_tags["phi_tags_found"]}
        deidentified_tag_names = {tag["tag_name"] for tag in deidentified_tags["phi_tags_found"]}
        
        removed_tag_names = original_tag_names - deidentified_tag_names
        
        for tag in original_tags["phi_tags_found"]:
            if tag["tag_name"] in removed_tag_names:
                comparison["removed_tags"].append(tag)
        
        return comparison
    
    def export_tags_json(
        self,
        tags_data: Dict,
        output_path: Union[str, Path]
    ) -> None:
        """
        Export tags to JSON file.
        
        Args:
            tags_data: Tags dictionary
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tags_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Tags exported to JSON: {output_path}")
    
    def export_tags_csv(
        self,
        tags_data: Dict,
        output_path: Union[str, Path]
    ) -> None:
        """
        Export tags to CSV file.
        
        Args:
            tags_data: Tags dictionary (must have 'tags' key)
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if "tags" not in tags_data:
            print("Error: tags_data must have 'tags' key for CSV export")
            return
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["tag", "tag_name", "vr", "value", "keyword", "is_private"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for tag in tags_data["tags"]:
                writer.writerow(tag)
        
        print(f"✓ Tags exported to CSV: {output_path}")
    
    def export_tags_txt(
        self,
        tags_data: Dict,
        output_path: Union[str, Path]
    ) -> None:
        """
        Export tags to formatted text file.
        
        Args:
            tags_data: Tags dictionary
            output_path: Output file path
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("DICOM TAGS REPORT\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"File: {tags_data.get('file_path', 'Unknown')}\n")
            
            if "total_tags" in tags_data:
                f.write(f"Total Tags: {tags_data['total_tags']}\n\n")
            
            if "phi_count" in tags_data:
                f.write(f"PHI Tags Found: {tags_data['phi_count']}\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("TAGS\n")
            f.write("-" * 70 + "\n\n")
            
            # Handle different tag formats
            tags_list = tags_data.get("tags", tags_data.get("phi_tags_found", []))
            
            for tag in tags_list:
                f.write(f"Tag: {tag.get('tag', 'N/A')}\n")
                f.write(f"  Name: {tag.get('tag_name', 'N/A')}\n")
                f.write(f"  VR: {tag.get('vr', 'N/A')}\n")
                f.write(f"  Value: {tag.get('value', 'N/A')}\n")
                f.write(f"  Keyword: {tag.get('keyword', 'N/A')}\n")
                if "is_private" in tag:
                    f.write(f"  Private: {tag['is_private']}\n")
                f.write("\n")
            
            f.write("=" * 70 + "\n")
        
        print(f"✓ Tags exported to TXT: {output_path}")
    
    def print_tags_summary(
        self,
        tags_data: Dict
    ) -> None:
        """
        Print a formatted summary of tags to console.
        
        Args:
            tags_data: Tags dictionary
        """
        print("\n" + "=" * 70)
        print("DICOM TAGS SUMMARY")
        print("=" * 70)
        
        print(f"\nFile: {tags_data.get('file_path', 'Unknown')}")
        
        if "total_tags" in tags_data:
            print(f"Total Tags: {tags_data['total_tags']}")
        
        if "phi_count" in tags_data:
            print(f"PHI Tags: {tags_data['phi_count']}")
        
        # Handle different tag formats
        if "patient" in tags_data:
            # Standard tags format
            print("\nPATIENT INFORMATION:")
            for key, value in tags_data["patient"].items():
                if value:
                    print(f"  {key}: {value}")
            
            print("\nSTUDY INFORMATION:")
            for key, value in tags_data["study"].items():
                if value:
                    print(f"  {key}: {value}")
            
            print("\nSERIES INFORMATION:")
            for key, value in tags_data["series"].items():
                if value:
                    print(f"  {key}: {value}")
        
        elif "phi_tags_found" in tags_data:
            # PHI tags format
            print("\nPHI TAGS FOUND:")
            for tag in tags_data["phi_tags_found"][:10]:  # Show first 10
                print(f"  • {tag['tag_name']}: {tag['value'][:50]}")
            
            if len(tags_data["phi_tags_found"]) > 10:
                print(f"  ... and {len(tags_data['phi_tags_found']) - 10} more")
        
        elif "tags" in tags_data:
            # All tags format
            print(f"\nShowing first 20 tags (of {len(tags_data['tags'])}):")
            for tag in tags_data["tags"][:20]:
                print(f"  • {tag['tag_name']}: {tag['value'][:50]}")
        
        print("=" * 70 + "\n")


def example_1_read_all_tags():
    """Example 1: Read and display all DICOM tags."""
    print("\n" + "=" * 70)
    print("Example 1: Read All DICOM Tags")
    print("=" * 70)
    
    processor = DicomTagProcessor()
    
    # Read all tags (uncomment to use with real DICOM)
    # tags = processor.read_all_tags("sample.dcm")
    # processor.print_tags_summary(tags)
    # processor.export_tags_json(tags, "all_tags.json")
    # processor.export_tags_csv(tags, "all_tags.csv")
    # processor.export_tags_txt(tags, "all_tags.txt")
    
    print("✓ Example code ready (add your DICOM file)")


def example_2_get_phi_tags():
    """Example 2: Get only PHI tags."""
    print("\n" + "=" * 70)
    print("Example 2: Extract PHI Tags Only")
    print("=" * 70)
    
    processor = DicomTagProcessor()
    
    # Get PHI tags
    # phi_tags = processor.get_phi_tags("sample.dcm")
    # 
    # print(f"PHI Tags Found: {phi_tags['phi_count']}")
    # 
    # for tag in phi_tags['phi_tags_found']:
    #     print(f"  • {tag['tag_name']}: {tag['value']}")
    # 
    # # Export
    # processor.export_tags_json(phi_tags, "phi_tags.json")
    # processor.export_tags_txt(phi_tags, "phi_tags.txt")
    
    print("✓ Example code ready")


def example_3_get_standard_tags():
    """Example 3: Get organized standard tags."""
    print("\n" + "=" * 70)
    print("Example 3: Get Organized Standard Tags")
    print("=" * 70)
    
    processor = DicomTagProcessor()
    
    # Get organized tags
    # standard_tags = processor.get_standard_tags("sample.dcm")
    # processor.print_tags_summary(standard_tags)
    # processor.export_tags_json(standard_tags, "standard_tags.json")
    
    print("✓ Example code ready")


def example_4_compare_before_after():
    """Example 4: Compare tags before and after de-identification."""
    print("\n" + "=" * 70)
    print("Example 4: Compare Before/After De-identification")
    print("=" * 70)
    
    processor = DicomTagProcessor()
    
    # Compare
    # comparison = processor.compare_tags_before_after(
    #     "original.dcm",
    #     "deidentified.dcm"
    # )
    # 
    # print(f"Original PHI Tags: {comparison['original_phi_count']}")
    # print(f"Remaining PHI Tags: {comparison['deidentified_phi_count']}")
    # print(f"PHI Removed: {comparison['phi_removed']}")
    # 
    # print("\nRemoved Tags:")
    # for tag in comparison['removed_tags']:
    #     print(f"  ✓ {tag['tag_name']}")
    # 
    # if comparison['remaining_tags']:
    #     print("\n⚠ Remaining PHI Tags:")
    #     for tag in comparison['remaining_tags']:
    #         print(f"  • {tag['tag_name']}: {tag['value']}")
    # 
    # processor.export_tags_json(comparison, "comparison.json")
    
    print("✓ Example code ready")


def example_5_complete_workflow():
    """Example 5: Complete workflow with de-identification."""
    print("\n" + "=" * 70)
    print("Example 5: Complete Workflow")
    print("=" * 70)
    
    processor = DicomTagProcessor()
    
    # Step 1: Read original tags
    # print("Step 1: Reading original DICOM tags...")
    # original_tags = processor.get_phi_tags("original.dcm")
    # print(f"  PHI Tags Found: {original_tags['phi_count']}")
    # 
    # # Step 2: De-identify
    # print("\nStep 2: De-identifying...")
    # deidentifier = DicomDeidentifier(
    #     hash_patient_id=True,
    #     date_offset_days=365,
    #     preserve_age=True,
    #     preserve_sex=True
    # )
    # 
    # result = deidentifier.deidentify(
    #     input_path="original.dcm",
    #     output_path="deidentified.dcm",
    #     remove_private_tags=True
    # )
    # 
    # if result['success']:
    #     print("  ✓ De-identification complete")
    # 
    # # Step 3: Verify
    # print("\nStep 3: Verifying de-identification...")
    # deidentified_tags = processor.get_phi_tags("deidentified.dcm")
    # print(f"  Remaining PHI Tags: {deidentified_tags['phi_count']}")
    # 
    # # Step 4: Compare
    # print("\nStep 4: Generating comparison...")
    # comparison = processor.compare_tags_before_after(
    #     "original.dcm",
    #     "deidentified.dcm"
    # )
    # 
    # print(f"  Tags Removed: {comparison['phi_removed']}")
    # 
    # # Step 5: Export results
    # print("\nStep 5: Exporting results...")
    # processor.export_tags_json(original_tags, "reports/original_phi_tags.json")
    # processor.export_tags_json(deidentified_tags, "reports/deidentified_phi_tags.json")
    # processor.export_tags_json(comparison, "reports/comparison.json")
    # processor.export_tags_txt(comparison, "reports/comparison_report.txt")
    # 
    # print("\n✓ Complete workflow finished!")
    
    print("✓ Example code ready")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("DICOM TAG PROCESSOR - medimagecleaner")
    print("=" * 70)
    print("\nThis script demonstrates how to:")
    print("  1. Read and extract DICOM tags")
    print("  2. Identify PHI tags")
    print("  3. De-identify DICOM files")
    print("  4. Compare tags before/after")
    print("  5. Export tags to JSON/CSV/TXT")
    
    # Run examples
    example_1_read_all_tags()
    example_2_get_phi_tags()
    example_3_get_standard_tags()
    example_4_compare_before_after()
    example_5_complete_workflow()
    
    print("\n" + "=" * 70)
    print("All examples ready!")
    print("=" * 70)
    print("\nQuick Start:")
    print("  1. Generate test DICOMs: python generate_test_dicoms.py")
    print("  2. Use this script with test files")
    print("  3. View exported tags in JSON/CSV/TXT formats")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
