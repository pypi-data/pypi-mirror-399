"""
DICOM De-identification Module

Handles removal and anonymization of PHI from DICOM metadata.
"""

import pydicom
from typing import List, Dict, Optional, Union
from pathlib import Path
import hashlib
from datetime import datetime, timedelta


class DicomDeidentifier:
    """De-identifies DICOM files by removing or anonymizing PHI tags."""
    
    # Comprehensive list of PHI tags based on DICOM PS3.15 and HIPAA
    DEFAULT_PHI_TAGS = [
        # Patient Information
        "PatientName",
        "PatientID",
        "PatientBirthDate",
        "PatientSex",
        "PatientAge",
        "PatientWeight",
        "PatientSize",
        "PatientAddress",
        "PatientTelephoneNumbers",
        "PatientMotherBirthName",
        "MilitaryRank",
        "EthnicGroup",
        "Occupation",
        "AdditionalPatientHistory",
        "PatientComments",
        "PatientBirthTime",
        "PatientBirthName",
        "PatientInsurancePlanCodeSequence",
        "PatientPrimaryLanguageCodeSequence",
        "PatientReligiousPreference",
        
        # Institution Information
        "InstitutionName",
        "InstitutionAddress",
        "InstitutionalDepartmentName",
        "StationName",
        
        # Physician Information
        "ReferringPhysicianName",
        "ReferringPhysicianAddress",
        "ReferringPhysicianTelephoneNumbers",
        "ReferringPhysicianIdentificationSequence",
        "PerformingPhysicianName",
        "PerformingPhysicianIdentificationSequence",
        "NameOfPhysiciansReadingStudy",
        "PhysiciansOfRecord",
        "PhysiciansOfRecordIdentificationSequence",
        "OperatorsName",
        "OperatorIdentificationSequence",
        
        # Study/Series Information with Dates
        "StudyDate",
        "SeriesDate",
        "AcquisitionDate",
        "ContentDate",
        "OverlayDate",
        "CurveDate",
        "StudyTime",
        "SeriesTime",
        "AcquisitionTime",
        "ContentTime",
        
        # Identifiers
        "AccessionNumber",
        "StudyID",
        "FrameOfReferenceUID",
        "SynchronizationFrameOfReferenceUID",
        "DeviceSerialNumber",
        "PlateID",
        "CassetteID",
        "GantryID",
        
        # Other potentially identifying information
        "RequestingPhysician",
        "RequestingService",
        "RequestedProcedureDescription",
        "PerformedProcedureStepDescription",
        "ScheduledProcedureStepDescription",
        "ImageComments",
        "StudyComments",
        "AdmissionID",
        "IssuerOfAdmissionID",
        "ServiceEpisodeID",
        "IssuerOfServiceEpisodeID",
    ]
    
    def __init__(
        self,
        custom_phi_tags: Optional[List[str]] = None,
        replacement_value: str = "ANONYMIZED",
        date_offset_days: Optional[int] = None,
        preserve_age: bool = False,
        preserve_sex: bool = False,
        hash_patient_id: bool = True,
    ):
        """
        Initialize the DICOM de-identifier.
        
        Args:
            custom_phi_tags: Additional PHI tags to remove (supplements defaults)
            replacement_value: Value to use for anonymized fields
            date_offset_days: If set, offset dates by this many days instead of removing
            preserve_age: Keep patient age information
            preserve_sex: Keep patient sex information
            hash_patient_id: Replace patient ID with hash instead of generic value
        """
        self.phi_tags = set(self.DEFAULT_PHI_TAGS)
        if custom_phi_tags:
            self.phi_tags.update(custom_phi_tags)
        
        self.replacement_value = replacement_value
        self.date_offset_days = date_offset_days
        self.preserve_age = preserve_age
        self.preserve_sex = preserve_sex
        self.hash_patient_id = hash_patient_id
        
        # Remove preserved tags from phi_tags
        if self.preserve_age:
            self.phi_tags.discard("PatientAge")
        if self.preserve_sex:
            self.phi_tags.discard("PatientSex")
    
    def _hash_identifier(self, identifier: str, salt: str = "medimagecleaner") -> str:
        """Create a consistent hash of an identifier."""
        return hashlib.sha256(f"{salt}{identifier}".encode()).hexdigest()[:16]
    
    def _offset_date(self, date_str: str, offset_days: int) -> str:
        """Offset a DICOM date by specified number of days."""
        try:
            # DICOM dates are typically YYYYMMDD
            if len(date_str) == 8:
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                new_date = date_obj + timedelta(days=offset_days)
                return new_date.strftime("%Y%m%d")
        except ValueError:
            pass
        return self.replacement_value
    
    def deidentify(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        remove_private_tags: bool = True,
        remove_curves: bool = True,
        remove_overlays: bool = True,
    ) -> Dict[str, any]:
        """
        De-identify a DICOM file.
        
        Args:
            input_path: Path to input DICOM file
            output_path: Path to save de-identified file (optional)
            remove_private_tags: Remove all private tags
            remove_curves: Remove curve data
            remove_overlays: Remove overlay data
        
        Returns:
            Dictionary with de-identification results and statistics
        """
        input_path = Path(input_path)
        
        # Load DICOM
        ds = pydicom.dcmread(str(input_path))
        
        # Track changes
        changes = {
            "tags_modified": [],
            "tags_removed": [],
            "private_tags_removed": 0,
            "original_patient_id": None,
        }
        
        # Store original patient ID for tracking
        if "PatientID" in ds:
            changes["original_patient_id"] = str(ds.PatientID)
        
        # Process PHI tags
        for tag in self.phi_tags:
            if tag in ds:
                # Special handling for PatientID with hashing
                if tag == "PatientID" and self.hash_patient_id:
                    original_id = str(ds.data_element(tag).value)
                    ds.data_element(tag).value = self._hash_identifier(original_id)
                    changes["tags_modified"].append(tag)
                
                # Special handling for dates with offset
                elif self.date_offset_days and "Date" in tag:
                    original_date = str(ds.data_element(tag).value)
                    ds.data_element(tag).value = self._offset_date(
                        original_date, self.date_offset_days
                    )
                    changes["tags_modified"].append(tag)
                
                # Default: replace with anonymized value
                else:
                    ds.data_element(tag).value = self.replacement_value
                    changes["tags_modified"].append(tag)
        
        # Remove private tags
        if remove_private_tags:
            for elem in list(ds):
                if elem.tag.is_private:
                    del ds[elem.tag]
                    changes["private_tags_removed"] += 1
        
        # Remove curves (often contain PHI)
        if remove_curves:
            ds.remove_private_tags()
            for elem in list(ds):
                if elem.tag.group == 0x5000:  # Curve data group
                    del ds[elem.tag]
        
        # Remove overlays (may contain burned-in annotations)
        if remove_overlays:
            for elem in list(ds):
                if elem.tag.group == 0x6000:  # Overlay data group
                    del ds[elem.tag]
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            ds.save_as(str(output_path))
            changes["output_path"] = str(output_path)
        
        changes["success"] = True
        return {"dataset": ds, "changes": changes}
    
    def batch_deidentify(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        recursive: bool = True,
        **kwargs
    ) -> Dict[str, any]:
        """
        De-identify all DICOM files in a directory.
        
        Args:
            input_dir: Directory containing DICOM files
            output_dir: Directory to save de-identified files
            recursive: Process subdirectories recursively
            **kwargs: Additional arguments passed to deidentify()
        
        Returns:
            Dictionary with batch processing results
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all DICOM files
        if recursive:
            dicom_files = list(input_dir.rglob("*.dcm"))
        else:
            dicom_files = list(input_dir.glob("*.dcm"))
        
        results = {
            "total_files": len(dicom_files),
            "successful": 0,
            "failed": 0,
            "errors": [],
        }
        
        for dcm_file in dicom_files:
            try:
                # Preserve directory structure
                rel_path = dcm_file.relative_to(input_dir)
                output_path = output_dir / rel_path
                
                result = self.deidentify(dcm_file, output_path, **kwargs)
                if result["changes"]["success"]:
                    results["successful"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "file": str(dcm_file),
                    "error": str(e)
                })
        
        return results
