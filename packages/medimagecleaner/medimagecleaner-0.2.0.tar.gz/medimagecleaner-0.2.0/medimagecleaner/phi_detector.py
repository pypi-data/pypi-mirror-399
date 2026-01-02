"""
PHI Detection Module

Comprehensive patient information detection without modifying files.
Provides detailed reports on what PHI is present in medical images.
"""

import pydicom
from typing import Dict, List, Union, Optional
from pathlib import Path
import numpy as np
from .validator import DeidentificationValidator
from .text_remover import TextRemover
from .face_remover import FaceRemover
from .risk_assessment import RiskAssessment


class PHIDetector:
    """
    Detect patient information in medical images without modifying them.
    
    Provides comprehensive reports on PHI presence including:
    - DICOM metadata PHI
    - Burned-in text
    - Faces in images
    - Risk assessment
    """
    
    def __init__(
        self,
        enable_ocr: bool = True,
        enable_face_detection: bool = True,
        enable_risk_assessment: bool = True,
    ):
        """
        Initialize the PHI detector.
        
        Args:
            enable_ocr: Enable OCR for burned-in text detection
            enable_face_detection: Enable face detection
            enable_risk_assessment: Enable risk scoring
        """
        self.enable_ocr = enable_ocr
        self.enable_face_detection = enable_face_detection
        self.enable_risk_assessment = enable_risk_assessment
        
        # Initialize components
        self.validator = DeidentificationValidator(strict_mode=True)
        
        if enable_ocr:
            self.text_remover = TextRemover(ocr_enabled=True)
        
        if enable_face_detection:
            self.face_remover = FaceRemover()
        
        if enable_risk_assessment:
            self.risk_assessor = RiskAssessment(strict_mode=True)
    
    def detect_metadata_phi(
        self,
        ds: pydicom.Dataset
    ) -> Dict[str, any]:
        """
        Detect PHI in DICOM metadata.
        
        Args:
            ds: DICOM dataset
        
        Returns:
            Dictionary with metadata PHI findings
        """
        findings = {
            "phi_tags_found": [],
            "suspicious_values": [],
            "private_tags": 0,
            "has_phi": False,
        }
        
        # Check for standard PHI tags
        phi_tag_names = [
            "PatientName",
            "PatientID",
            "PatientBirthDate",
            "PatientAddress",
            "PatientTelephoneNumbers",
            "InstitutionName",
            "ReferringPhysicianName",
            "StudyDate",
            "AccessionNumber",
        ]
        
        for tag_name in phi_tag_names:
            if tag_name in ds:
                value = str(ds.data_element(tag_name).value)
                if value and value.upper() not in ["ANONYMIZED", "REMOVED", ""]:
                    findings["phi_tags_found"].append({
                        "tag": tag_name,
                        "value": value[:50],  # Truncate for safety
                        "vr": ds.data_element(tag_name).VR,
                    })
                    findings["has_phi"] = True
        
        # Count private tags
        for elem in ds:
            if elem.tag.is_private:
                findings["private_tags"] += 1
        
        # Run validator for additional checks
        validation = self.validator.validate_dicom(ds)
        findings["suspicious_values"] = validation.get("suspicious_tags", [])
        
        return findings
    
    def detect_burned_in_text(
        self,
        ds: pydicom.Dataset
    ) -> Dict[str, any]:
        """
        Detect burned-in text in DICOM pixel data.
        
        Args:
            ds: DICOM dataset
        
        Returns:
            Dictionary with text detection findings
        """
        if not self.enable_ocr:
            return {"enabled": False, "text_found": []}
        
        findings = {
            "enabled": True,
            "text_found": [],
            "total_regions": 0,
            "has_text": False,
        }
        
        try:
            # Get pixel array
            pixel_array = ds.pixel_array
            
            # Convert to appropriate format
            if pixel_array.dtype != np.uint8:
                pixel_array = (
                    (pixel_array - pixel_array.min()) * 
                    (255.0 / (pixel_array.max() - pixel_array.min()))
                ).astype(np.uint8)
            
            # Detect text
            text_regions = self.text_remover.detect_text_ocr(pixel_array)
            
            findings["total_regions"] = len(text_regions)
            findings["has_text"] = len(text_regions) > 0
            
            # Categorize detected text
            for region in text_regions:
                findings["text_found"].append({
                    "text": region["text"],
                    "confidence": region["confidence"],
                    "location": region["bbox"],
                })
        
        except Exception as e:
            findings["error"] = str(e)
        
        return findings
    
    def detect_faces(
        self,
        ds: pydicom.Dataset
    ) -> Dict[str, any]:
        """
        Detect faces in DICOM pixel data.
        
        Args:
            ds: DICOM dataset
        
        Returns:
            Dictionary with face detection findings
        """
        if not self.enable_face_detection:
            return {"enabled": False, "faces_found": []}
        
        findings = {
            "enabled": True,
            "faces_found": [],
            "total_faces": 0,
            "has_faces": False,
        }
        
        try:
            # Get pixel array
            pixel_array = ds.pixel_array
            
            # Convert to appropriate format
            if pixel_array.dtype != np.uint8:
                pixel_array = (
                    (pixel_array - pixel_array.min()) * 
                    (255.0 / (pixel_array.max() - pixel_array.min()))
                ).astype(np.uint8)
            
            # Detect faces
            faces = self.face_remover.detect_faces_haar(pixel_array)
            
            findings["total_faces"] = len(faces)
            findings["has_faces"] = len(faces) > 0
            
            for x, y, w, h in faces:
                findings["faces_found"].append({
                    "location": (x, y),
                    "size": (w, h),
                    "bbox": (x, y, w, h),
                })
        
        except Exception as e:
            findings["error"] = str(e)
        
        return findings
    
    def check_file(
        self,
        dicom_path: Union[str, Path]
    ) -> Dict[str, any]:
        """
        Comprehensive PHI check for a single DICOM file.
        
        Args:
            dicom_path: Path to DICOM file
        
        Returns:
            Comprehensive PHI detection report
        """
        # Load DICOM
        ds = pydicom.dcmread(str(dicom_path))
        
        report = {
            "file": str(dicom_path),
            "phi_detected": False,
            "metadata_phi": {},
            "burned_in_text": {},
            "faces": {},
            "risk_assessment": {},
            "summary": {
                "has_metadata_phi": False,
                "has_burned_text": False,
                "has_faces": False,
                "overall_risk": "UNKNOWN",
            },
        }
        
        # 1. Check metadata
        report["metadata_phi"] = self.detect_metadata_phi(ds)
        report["summary"]["has_metadata_phi"] = report["metadata_phi"]["has_phi"]
        
        # 2. Check burned-in text
        report["burned_in_text"] = self.detect_burned_in_text(ds)
        if report["burned_in_text"].get("enabled"):
            report["summary"]["has_burned_text"] = report["burned_in_text"]["has_text"]
        
        # 3. Check for faces
        report["faces"] = self.detect_faces(ds)
        if report["faces"].get("enabled"):
            report["summary"]["has_faces"] = report["faces"]["has_faces"]
        
        # 4. Risk assessment
        if self.enable_risk_assessment:
            assessment = self.risk_assessor.assess_dicom_file(ds)
            report["risk_assessment"] = assessment
            report["summary"]["overall_risk"] = assessment["risk_level"]
        
        # Determine if PHI detected
        report["phi_detected"] = (
            report["summary"]["has_metadata_phi"] or
            report["summary"]["has_burned_text"] or
            report["summary"]["has_faces"]
        )
        
        return report
    
    def check_directory(
        self,
        input_dir: Union[str, Path],
        recursive: bool = True,
        sample_rate: float = 1.0,
    ) -> Dict[str, any]:
        """
        Check entire directory for PHI.
        
        Args:
            input_dir: Directory containing DICOM files
            recursive: Process subdirectories
            sample_rate: Fraction of files to check (0.0-1.0)
        
        Returns:
            Batch PHI detection results
        """
        import random
        
        input_dir = Path(input_dir)
        
        # Find DICOM files
        if recursive:
            dicom_files = list(input_dir.rglob("*.dcm"))
        else:
            dicom_files = list(input_dir.glob("*.dcm"))
        
        # Sample if requested
        if sample_rate < 1.0:
            k = int(len(dicom_files) * sample_rate)
            dicom_files = random.sample(dicom_files, k)
        
        results = {
            "total_files": len(dicom_files),
            "files_checked": 0,
            "files_with_phi": 0,
            "files_clean": 0,
            "summary": {
                "metadata_phi_count": 0,
                "burned_text_count": 0,
                "faces_count": 0,
                "high_risk_count": 0,
            },
            "details": [],
        }
        
        for dcm_file in dicom_files:
            try:
                report = self.check_file(dcm_file)
                results["files_checked"] += 1
                
                if report["phi_detected"]:
                    results["files_with_phi"] += 1
                else:
                    results["files_clean"] += 1
                
                # Update summary
                if report["summary"]["has_metadata_phi"]:
                    results["summary"]["metadata_phi_count"] += 1
                if report["summary"]["has_burned_text"]:
                    results["summary"]["burned_text_count"] += 1
                if report["summary"]["has_faces"]:
                    results["summary"]["faces_count"] += 1
                if report["summary"]["overall_risk"] == "HIGH":
                    results["summary"]["high_risk_count"] += 1
                
                # Store details
                results["details"].append(report)
            
            except Exception as e:
                pass
        
        return results
    
    def generate_report(
        self,
        check_results: Dict[str, any],
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """
        Generate human-readable PHI detection report.
        
        Args:
            check_results: Results from check_file() or check_directory()
            output_path: Optional path to save report
        
        Returns:
            Report as string
        """
        # Check if single file or batch
        if "file" in check_results:
            # Single file report
            report = self._generate_single_file_report(check_results)
        else:
            # Batch report
            report = self._generate_batch_report(check_results)
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)
        
        return report
    
    def _generate_single_file_report(self, results: Dict) -> str:
        """Generate report for single file."""
        lines = [
            "=" * 70,
            "PHI DETECTION REPORT - SINGLE FILE",
            "=" * 70,
            "",
            f"File: {results['file']}",
            f"PHI Detected: {'✗ YES' if results['phi_detected'] else '✓ NO'}",
            "",
            "SUMMARY",
            "-" * 70,
            f"Metadata PHI: {'✗ Found' if results['summary']['has_metadata_phi'] else '✓ Clean'}",
            f"Burned-in Text: {'✗ Found' if results['summary']['has_burned_text'] else '✓ Clean'}",
            f"Faces: {'✗ Found' if results['summary']['has_faces'] else '✓ Clean'}",
            f"Risk Level: {results['summary']['overall_risk']}",
            "",
        ]
        
        # Metadata details
        if results["metadata_phi"]["phi_tags_found"]:
            lines.extend([
                "METADATA PHI DETAILS",
                "-" * 70,
            ])
            for tag in results["metadata_phi"]["phi_tags_found"]:
                lines.append(f"  • {tag['tag']}: {tag['value']}")
            lines.append("")
        
        # Text details
        if results["burned_in_text"].get("text_found"):
            lines.extend([
                "BURNED-IN TEXT DETAILS",
                "-" * 70,
            ])
            for text in results["burned_in_text"]["text_found"]:
                lines.append(
                    f"  • '{text['text']}' (confidence: {text['confidence']:.1f}%)"
                )
            lines.append("")
        
        # Face details
        if results["faces"].get("faces_found"):
            lines.extend([
                "FACE DETECTION DETAILS",
                "-" * 70,
                f"  Faces detected: {len(results['faces']['faces_found'])}",
            ])
            for i, face in enumerate(results["faces"]["faces_found"], 1):
                lines.append(
                    f"  • Face {i}: Location {face['location']}, Size {face['size']}"
                )
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _generate_batch_report(self, results: Dict) -> str:
        """Generate report for batch check."""
        lines = [
            "=" * 70,
            "PHI DETECTION REPORT - BATCH CHECK",
            "=" * 70,
            "",
            f"Total Files: {results['total_files']}",
            f"Files Checked: {results['files_checked']}",
            f"Files with PHI: {results['files_with_phi']}",
            f"Clean Files: {results['files_clean']}",
            "",
            "SUMMARY",
            "-" * 70,
            f"Files with Metadata PHI: {results['summary']['metadata_phi_count']}",
            f"Files with Burned-in Text: {results['summary']['burned_text_count']}",
            f"Files with Faces: {results['summary']['faces_count']}",
            f"High Risk Files: {results['summary']['high_risk_count']}",
            "",
        ]
        
        if results['files_with_phi'] > 0:
            lines.extend([
                "FILES WITH PHI (First 10)",
                "-" * 70,
            ])
            for detail in results['details'][:10]:
                if detail['phi_detected']:
                    phi_types = []
                    if detail['summary']['has_metadata_phi']:
                        phi_types.append("Metadata")
                    if detail['summary']['has_burned_text']:
                        phi_types.append("Text")
                    if detail['summary']['has_faces']:
                        phi_types.append("Faces")
                    
                    lines.append(
                        f"  • {detail['file']}: {', '.join(phi_types)}"
                    )
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)
