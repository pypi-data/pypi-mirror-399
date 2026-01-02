"""
Validation Module

Validates that de-identification was successful and comprehensive.
"""

import pydicom
from typing import List, Dict, Set, Union, Optional
from pathlib import Path
import re


class DeidentificationValidator:
    """Validates de-identification of DICOM files."""
    
    # Patterns that might indicate PHI
    PHI_PATTERNS = {
        "name": r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b",  # Name pattern
        "date": r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",  # Date pattern
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone pattern
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        "mrn": r"\b(MRN|ID|Patient)\s*[:#]?\s*\d+\b",  # Medical record number
    }
    
    def __init__(
        self,
        strict_mode: bool = True,
        check_private_tags: bool = True,
        check_pixel_data: bool = False,
    ):
        """
        Initialize the validator.
        
        Args:
            strict_mode: Fail validation on any potential PHI
            check_private_tags: Check for remaining private tags
            check_pixel_data: Check pixel data for text (requires OCR)
        """
        self.strict_mode = strict_mode
        self.check_private_tags = check_private_tags
        self.check_pixel_data = check_pixel_data
    
    def _check_tag_value(self, value: str) -> List[str]:
        """Check if a tag value contains potential PHI."""
        if not isinstance(value, str):
            value = str(value)
        
        findings = []
        
        for phi_type, pattern in self.PHI_PATTERNS.items():
            if re.search(pattern, value):
                findings.append(phi_type)
        
        return findings
    
    def validate_dicom(
        self,
        dicom_path: Union[str, Path, pydicom.Dataset],
        expected_phi_tags: Optional[Set[str]] = None,
    ) -> Dict[str, any]:
        """
        Validate a DICOM file for remaining PHI.
        
        Args:
            dicom_path: Path to DICOM file or DICOM dataset
            expected_phi_tags: Tags that should have been removed/anonymized
        
        Returns:
            Dictionary with validation results
        """
        # Load DICOM if path provided
        if isinstance(dicom_path, (str, Path)):
            ds = pydicom.dcmread(str(dicom_path))
            file_path = str(dicom_path)
        else:
            ds = dicom_path
            file_path = "Dataset"
        
        validation = {
            "file": file_path,
            "passed": True,
            "warnings": [],
            "failures": [],
            "suspicious_tags": [],
            "private_tags_found": 0,
        }
        
        # Check for private tags
        if self.check_private_tags:
            for elem in ds:
                if elem.tag.is_private:
                    validation["private_tags_found"] += 1
                    validation["warnings"].append(
                        f"Private tag found: {elem.tag}"
                    )
        
        # Check all tags for potential PHI
        for elem in ds:
            if elem.VR in ["PN", "LO", "SH", "LT", "ST", "UT"]:  # Text VRs
                value = str(elem.value)
                
                # Skip empty or placeholder values
                if not value or value.upper() in ["ANONYMIZED", "REMOVED", ""]:
                    continue
                
                # Check for PHI patterns
                phi_findings = self._check_tag_value(value)
                if phi_findings:
                    validation["suspicious_tags"].append({
                        "tag": str(elem.tag),
                        "name": elem.keyword if hasattr(elem, "keyword") else "Unknown",
                        "value": value[:50],  # Truncate for safety
                        "potential_phi": phi_findings,
                    })
                    
                    if self.strict_mode:
                        validation["failures"].append(
                            f"Potential PHI in {elem.keyword}: {phi_findings}"
                        )
                        validation["passed"] = False
        
        # Check for standard PHI tags that should be anonymized
        if expected_phi_tags:
            for tag_name in expected_phi_tags:
                if tag_name in ds:
                    value = str(ds.data_element(tag_name).value)
                    if value.upper() not in ["ANONYMIZED", "REMOVED", ""]:
                        validation["failures"].append(
                            f"PHI tag not anonymized: {tag_name} = {value[:50]}"
                        )
                        validation["passed"] = False
        
        # Overall pass/fail
        if validation["failures"]:
            validation["passed"] = False
        
        return validation
    
    def validate_batch(
        self,
        input_dir: Union[str, Path],
        recursive: bool = True,
        sample_rate: float = 1.0,
    ) -> Dict[str, any]:
        """
        Validate a batch of DICOM files.
        
        Args:
            input_dir: Directory containing DICOM files
            recursive: Process subdirectories recursively
            sample_rate: Fraction of files to validate (0.0-1.0)
        
        Returns:
            Dictionary with batch validation results
        """
        import random
        
        input_dir = Path(input_dir)
        
        # Find all DICOM files
        if recursive:
            dicom_files = list(input_dir.rglob("*.dcm"))
        else:
            dicom_files = list(input_dir.glob("*.dcm"))
        
        # Sample files if requested
        if sample_rate < 1.0:
            k = int(len(dicom_files) * sample_rate)
            dicom_files = random.sample(dicom_files, k)
        
        results = {
            "total_files": len(dicom_files),
            "files_checked": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "failures_by_file": [],
            "summary": {},
        }
        
        for dcm_file in dicom_files:
            try:
                validation = self.validate_dicom(dcm_file)
                results["files_checked"] += 1
                
                if validation["passed"]:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["failures_by_file"].append({
                        "file": str(dcm_file),
                        "failures": validation["failures"],
                    })
                
                if validation["warnings"]:
                    results["warnings"] += len(validation["warnings"])
                
            except Exception as e:
                results["failures_by_file"].append({
                    "file": str(dcm_file),
                    "error": str(e)
                })
        
        # Calculate summary statistics
        if results["files_checked"] > 0:
            results["summary"] = {
                "pass_rate": results["passed"] / results["files_checked"],
                "fail_rate": results["failed"] / results["files_checked"],
                "avg_warnings": results["warnings"] / results["files_checked"],
            }
        
        return results
    
    def generate_report(
        self,
        validation_results: Dict[str, any],
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """
        Generate a human-readable validation report.
        
        Args:
            validation_results: Results from validate_batch()
            output_path: Optional path to save report
        
        Returns:
            Report as string
        """
        report_lines = [
            "=" * 60,
            "DE-IDENTIFICATION VALIDATION REPORT",
            "=" * 60,
            "",
            f"Total Files: {validation_results['total_files']}",
            f"Files Checked: {validation_results['files_checked']}",
            f"Passed: {validation_results['passed']}",
            f"Failed: {validation_results['failed']}",
            f"Warnings: {validation_results['warnings']}",
            "",
        ]
        
        if validation_results.get("summary"):
            summary = validation_results["summary"]
            report_lines.extend([
                "Summary Statistics:",
                f"  Pass Rate: {summary['pass_rate']:.1%}",
                f"  Fail Rate: {summary['fail_rate']:.1%}",
                f"  Avg Warnings per File: {summary['avg_warnings']:.2f}",
                "",
            ])
        
        if validation_results["failures_by_file"]:
            report_lines.extend([
                "Failed Files:",
                "-" * 60,
            ])
            for failure in validation_results["failures_by_file"][:10]:  # Limit to 10
                report_lines.append(f"\nFile: {failure['file']}")
                if "failures" in failure:
                    for fail in failure["failures"]:
                        report_lines.append(f"  - {fail}")
                if "error" in failure:
                    report_lines.append(f"  ERROR: {failure['error']}")
            
            if len(validation_results["failures_by_file"]) > 10:
                report_lines.append(
                    f"\n... and {len(validation_results['failures_by_file']) - 10} more"
                )
        
        report_lines.append("\n" + "=" * 60)
        
        report = "\n".join(report_lines)
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)
        
        return report
