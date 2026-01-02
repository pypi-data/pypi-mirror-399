#!/usr/bin/env python3
"""
Simple DICOM Tag Reader

Extract and display DICOM tags from medical images.
Can export to JSON, CSV, or display in terminal.

Usage:
    python dicom_tags.py <dicom_file> [--format json|csv|txt]
    python dicom_tags.py <dicom_file> --phi-only
    python dicom_tags.py <dicom_file> --standard
"""

import argparse
import json
import csv
import sys
from pathlib import Path

try:
    import pydicom
except ImportError:
    print("Error: pydicom not installed")
    print("Install with: pip install pydicom")
    sys.exit(1)


def get_all_tags(dicom_file):
    """Extract all DICOM tags."""
    ds = pydicom.dcmread(dicom_file)
    
    tags = []
    for elem in ds:
        tags.append({
            "tag": str(elem.tag),
            "name": elem.name,
            "vr": elem.VR,
            "value": str(elem.value)[:100],  # Truncate long values
            "keyword": elem.keyword,
        })
    
    return {
        "file": str(dicom_file),
        "total_tags": len(tags),
        "tags": tags
    }


def get_phi_tags(dicom_file):
    """Extract only PHI-related tags."""
    ds = pydicom.dcmread(dicom_file)
    
    # Common PHI tag names
    phi_tags = [
        "PatientName", "PatientID", "PatientBirthDate", "PatientSex",
        "PatientAge", "PatientAddress", "PatientTelephoneNumbers",
        "InstitutionName", "InstitutionAddress",
        "ReferringPhysicianName", "PerformingPhysicianName",
        "StudyDate", "SeriesDate", "AccessionNumber",
        "DeviceSerialNumber", "StationName"
    ]
    
    found_tags = []
    for tag_name in phi_tags:
        if tag_name in ds:
            elem = ds.data_element(tag_name)
            value = str(elem.value)
            
            if value and value.upper() not in ["", "ANONYMIZED", "REMOVED"]:
                found_tags.append({
                    "tag": str(elem.tag),
                    "name": tag_name,
                    "vr": elem.VR,
                    "value": value,
                    "keyword": elem.keyword,
                })
    
    return {
        "file": str(dicom_file),
        "phi_count": len(found_tags),
        "tags": found_tags
    }


def get_standard_tags(dicom_file):
    """Extract commonly used DICOM tags."""
    ds = pydicom.dcmread(dicom_file)
    
    def safe_get(tag_name):
        try:
            return str(ds.data_element(tag_name).value) if tag_name in ds else "N/A"
        except:
            return "N/A"
    
    return {
        "file": str(dicom_file),
        "patient": {
            "name": safe_get("PatientName"),
            "id": safe_get("PatientID"),
            "birth_date": safe_get("PatientBirthDate"),
            "sex": safe_get("PatientSex"),
            "age": safe_get("PatientAge"),
        },
        "study": {
            "date": safe_get("StudyDate"),
            "time": safe_get("StudyTime"),
            "description": safe_get("StudyDescription"),
            "modality": safe_get("Modality"),
            "accession": safe_get("AccessionNumber"),
        },
        "image": {
            "rows": safe_get("Rows"),
            "columns": safe_get("Columns"),
            "bits_allocated": safe_get("BitsAllocated"),
        },
        "institution": {
            "name": safe_get("InstitutionName"),
        },
    }


def print_tags_table(data):
    """Print tags in a formatted table."""
    print("\n" + "=" * 80)
    print(f"DICOM File: {data['file']}")
    print("=" * 80)
    
    if "total_tags" in data:
        print(f"Total Tags: {data['total_tags']}")
    if "phi_count" in data:
        print(f"PHI Tags: {data['phi_count']}")
    
    print("\n" + "-" * 80)
    print(f"{'Tag':<15} {'Name':<30} {'VR':<5} {'Value':<28}")
    print("-" * 80)
    
    for tag in data.get("tags", [])[:50]:  # Show first 50
        print(f"{tag['tag']:<15} {tag['name']:<30} {tag['vr']:<5} {tag['value']:<28}")
    
    if len(data.get("tags", [])) > 50:
        print(f"\n... and {len(data['tags']) - 50} more tags")
    
    print("=" * 80 + "\n")


def print_standard_tags(data):
    """Print standard tags in organized format."""
    print("\n" + "=" * 80)
    print(f"DICOM File: {data['file']}")
    print("=" * 80)
    
    print("\nPATIENT INFORMATION:")
    print("-" * 40)
    for key, value in data["patient"].items():
        print(f"  {key.replace('_', ' ').title():<20}: {value}")
    
    print("\nSTUDY INFORMATION:")
    print("-" * 40)
    for key, value in data["study"].items():
        print(f"  {key.replace('_', ' ').title():<20}: {value}")
    
    print("\nIMAGE INFORMATION:")
    print("-" * 40)
    for key, value in data["image"].items():
        print(f"  {key.replace('_', ' ').title():<20}: {value}")
    
    print("\nINSTITUTION:")
    print("-" * 40)
    for key, value in data["institution"].items():
        print(f"  {key.replace('_', ' ').title():<20}: {value}")
    
    print("=" * 80 + "\n")


def export_json(data, output_file):
    """Export tags to JSON."""
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Exported to JSON: {output_file}")


def export_csv(data, output_file):
    """Export tags to CSV."""
    with open(output_file, 'w', newline='') as f:
        if not data.get("tags"):
            print("No tags to export to CSV")
            return
        
        fieldnames = ["tag", "name", "vr", "value", "keyword"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for tag in data["tags"]:
            writer.writerow(tag)
    
    print(f"✓ Exported to CSV: {output_file}")


def export_txt(data, output_file):
    """Export tags to text file."""
    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("DICOM TAGS REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"File: {data['file']}\n")
        
        if "total_tags" in data:
            f.write(f"Total Tags: {data['total_tags']}\n")
        if "phi_count" in data:
            f.write(f"PHI Tags: {data['phi_count']}\n")
        
        f.write("\n" + "-" * 80 + "\n")
        f.write("TAGS\n")
        f.write("-" * 80 + "\n\n")
        
        for tag in data.get("tags", []):
            f.write(f"Tag: {tag['tag']}\n")
            f.write(f"  Name: {tag['name']}\n")
            f.write(f"  VR: {tag['vr']}\n")
            f.write(f"  Value: {tag['value']}\n")
            f.write(f"  Keyword: {tag['keyword']}\n\n")
        
        f.write("=" * 80 + "\n")
    
    print(f"✓ Exported to TXT: {output_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Extract and display DICOM tags",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Display all tags
  python dicom_tags.py scan.dcm
  
  # Show only PHI tags
  python dicom_tags.py scan.dcm --phi-only
  
  # Show standard tags (organized)
  python dicom_tags.py scan.dcm --standard
  
  # Export to JSON
  python dicom_tags.py scan.dcm --format json --output tags.json
  
  # Export PHI tags to CSV
  python dicom_tags.py scan.dcm --phi-only --format csv --output phi.csv
        """
    )
    
    parser.add_argument("dicom_file", help="Path to DICOM file")
    parser.add_argument("--phi-only", action="store_true",
                       help="Show only PHI tags")
    parser.add_argument("--standard", action="store_true",
                       help="Show standard organized tags")
    parser.add_argument("--format", choices=["json", "csv", "txt"],
                       help="Export format")
    parser.add_argument("--output", "-o",
                       help="Output file path")
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.dicom_file).exists():
        print(f"Error: File not found: {args.dicom_file}")
        sys.exit(1)
    
    # Extract tags based on mode
    try:
        if args.phi_only:
            data = get_phi_tags(args.dicom_file)
            if not args.format:
                print_tags_table(data)
        elif args.standard:
            data = get_standard_tags(args.dicom_file)
            if not args.format:
                print_standard_tags(data)
        else:
            data = get_all_tags(args.dicom_file)
            if not args.format:
                print_tags_table(data)
        
        # Export if format specified
        if args.format:
            output_file = args.output or f"dicom_tags.{args.format}"
            
            if args.format == "json":
                export_json(data, output_file)
            elif args.format == "csv":
                export_csv(data, output_file)
            elif args.format == "txt":
                export_txt(data, output_file)
    
    except Exception as e:
        print(f"Error processing DICOM file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
