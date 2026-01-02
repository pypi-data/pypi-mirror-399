"""
Audit Logger Module

Maintains detailed logs of de-identification operations for compliance.
"""

import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
import hashlib


class AuditLogger:
    """Logs all de-identification operations for audit trails."""
    
    def __init__(
        self,
        log_dir: Union[str, Path],
        log_level: int = logging.INFO,
        create_hash_mapping: bool = True,
    ):
        """
        Initialize the audit logger.
        
        Args:
            log_dir: Directory to store log files
            log_level: Logging level (e.g., logging.INFO)
            create_hash_mapping: Create mapping between original and hashed IDs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.create_hash_mapping = create_hash_mapping
        
        # Set up main logger
        self.logger = logging.getLogger("medimagecleaner")
        self.logger.setLevel(log_level)
        
        # File handler for audit log
        audit_file = self.log_dir / f"audit_{datetime.now():%Y%m%d_%H%M%S}.log"
        file_handler = logging.FileHandler(audit_file)
        file_handler.setLevel(log_level)
        
        # Format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Hash mapping file
        if self.create_hash_mapping:
            self.mapping_file = self.log_dir / "id_mapping.json"
            self.id_mapping = self._load_mapping()
    
    def _load_mapping(self) -> Dict[str, str]:
        """Load existing ID mapping if it exists."""
        if self.mapping_file.exists():
            with open(self.mapping_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_mapping(self):
        """Save ID mapping to file."""
        with open(self.mapping_file, "w") as f:
            json.dump(self.id_mapping, f, indent=2)
    
    def log_deidentification(
        self,
        file_path: str,
        original_patient_id: Optional[str],
        anonymized_patient_id: Optional[str],
        tags_modified: List[str],
        method: str = "metadata",
        additional_info: Optional[Dict] = None,
    ):
        """
        Log a de-identification operation.
        
        Args:
            file_path: Path to the file processed
            original_patient_id: Original patient ID (for mapping)
            anonymized_patient_id: New anonymized ID
            tags_modified: List of DICOM tags that were modified
            method: De-identification method used
            additional_info: Any additional information to log
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "method": method,
            "tags_modified": tags_modified,
        }
        
        if additional_info:
            log_entry.update(additional_info)
        
        # Log the operation
        self.logger.info(f"Deidentified: {file_path} - Method: {method}")
        self.logger.debug(json.dumps(log_entry, indent=2))
        
        # Update ID mapping
        if self.create_hash_mapping and original_patient_id and anonymized_patient_id:
            if original_patient_id not in self.id_mapping:
                self.id_mapping[original_patient_id] = anonymized_patient_id
                self._save_mapping()
    
    def log_batch_operation(
        self,
        results: Dict[str, any],
        operation: str = "batch_deidentification",
    ):
        """
        Log a batch operation.
        
        Args:
            results: Results dictionary from batch operation
            operation: Type of operation performed
        """
        summary = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "total_files": results.get("total_files", 0),
            "successful": results.get("successful", 0),
            "failed": results.get("failed", 0),
        }
        
        self.logger.info(
            f"{operation}: {summary['successful']}/{summary['total_files']} successful"
        )
        self.logger.debug(json.dumps(summary, indent=2))
        
        # Log errors if any
        if results.get("errors"):
            for error in results["errors"]:
                self.logger.error(
                    f"Failed: {error.get('file', 'unknown')} - {error.get('error', 'unknown error')}"
                )
    
    def log_validation(
        self,
        validation_results: Dict[str, any],
    ):
        """
        Log validation results.
        
        Args:
            validation_results: Results from validation
        """
        self.logger.info(
            f"Validation: {validation_results.get('passed', 0)}/{validation_results.get('files_checked', 0)} passed"
        )
        
        if validation_results.get("failures_by_file"):
            for failure in validation_results["failures_by_file"]:
                self.logger.warning(
                    f"Validation failed: {failure.get('file', 'unknown')}"
                )
    
    def create_session_report(
        self,
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """
        Create a summary report of the current session.
        
        Args:
            output_path: Optional path to save report
        
        Returns:
            Report as string
        """
        report_lines = [
            "=" * 60,
            "DE-IDENTIFICATION SESSION REPORT",
            "=" * 60,
            f"Session Start: {datetime.now().isoformat()}",
            f"Log Directory: {self.log_dir}",
            "",
        ]
        
        if self.create_hash_mapping:
            report_lines.extend([
                f"Patient IDs Processed: {len(self.id_mapping)}",
                f"ID Mapping File: {self.mapping_file}",
                "",
            ])
        
        report_lines.extend([
            "Log Files Created:",
            "-" * 60,
        ])
        
        for log_file in self.log_dir.glob("audit_*.log"):
            size = log_file.stat().st_size
            report_lines.append(f"  {log_file.name} ({size:,} bytes)")
        
        report_lines.append("\n" + "=" * 60)
        
        report = "\n".join(report_lines)
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)
        
        return report
    
    def export_mapping(
        self,
        output_path: Union[str, Path],
        include_timestamp: bool = True,
    ):
        """
        Export ID mapping to a separate file.
        
        Args:
            output_path: Path to save mapping
            include_timestamp: Include timestamp in export
        """
        if not self.create_hash_mapping:
            raise RuntimeError("ID mapping not enabled")
        
        export_data = {
            "mapping": self.id_mapping,
        }
        
        if include_timestamp:
            export_data["exported_at"] = datetime.now().isoformat()
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Exported ID mapping to: {output_path}")
    
    def verify_mapping(
        self,
        original_id: str,
        anonymized_id: str,
    ) -> bool:
        """
        Verify that an ID mapping is correct.
        
        Args:
            original_id: Original patient ID
            anonymized_id: Anonymized patient ID
        
        Returns:
            True if mapping matches
        """
        if not self.create_hash_mapping:
            return False
        
        return self.id_mapping.get(original_id) == anonymized_id
