"""
Batch Processor Module

Orchestrates complete de-identification workflows with multiple steps.
"""

from typing import Union, Optional, Dict, List
from pathlib import Path
from .dicom_deidentifier import DicomDeidentifier
from .text_remover import TextRemover
from .format_converter import FormatConverter
from .validator import DeidentificationValidator
from .audit_logger import AuditLogger


class BatchProcessor:
    """Orchestrates complete de-identification workflows."""
    
    def __init__(
        self,
        log_dir: Union[str, Path] = "./deidentification_logs",
        enable_logging: bool = True,
        enable_validation: bool = True,
    ):
        """
        Initialize the batch processor.
        
        Args:
            log_dir: Directory for audit logs
            enable_logging: Enable audit logging
            enable_validation: Enable validation after processing
        """
        self.enable_logging = enable_logging
        self.enable_validation = enable_validation
        
        # Initialize components
        self.deidentifier = DicomDeidentifier()
        self.text_remover = TextRemover()
        self.converter = FormatConverter()
        self.validator = DeidentificationValidator()
        
        if enable_logging:
            self.logger = AuditLogger(log_dir)
    
    def process_single_file(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        remove_metadata: bool = True,
        remove_burned_text: bool = False,
        convert_format: Optional[str] = None,
        text_removal_method: str = "ocr",
        validate_output: bool = True,
    ) -> Dict[str, any]:
        """
        Process a single DICOM file through complete workflow.
        
        Args:
            input_path: Input DICOM file
            output_path: Output file path
            remove_metadata: Remove PHI from metadata
            remove_burned_text: Remove burned-in text from pixels
            convert_format: Convert to format ('png', 'jpg', etc.) or None
            text_removal_method: Method for text removal ('ocr', 'crop', 'edges')
            validate_output: Validate the output
        
        Returns:
            Dictionary with processing results
        """
        results = {
            "input": str(input_path),
            "output": str(output_path),
            "steps_completed": [],
            "errors": [],
        }
        
        current_path = Path(input_path)
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Remove metadata PHI
        if remove_metadata:
            try:
                result = self.deidentifier.deidentify(
                    current_path,
                    output_path if not remove_burned_text else None,
                )
                results["steps_completed"].append("metadata_removal")
                results["metadata_changes"] = result["changes"]
                
                # Log the operation
                if self.enable_logging:
                    self.logger.log_deidentification(
                        file_path=str(input_path),
                        original_patient_id=result["changes"].get("original_patient_id"),
                        anonymized_patient_id=None,
                        tags_modified=result["changes"]["tags_modified"],
                        method="metadata",
                    )
                
                # Update current path for next step
                if not remove_burned_text:
                    current_path = output_path
                
            except Exception as e:
                results["errors"].append(f"Metadata removal failed: {str(e)}")
                return results
        
        # Step 2: Remove burned-in text
        if remove_burned_text:
            try:
                result = self.text_remover.process_dicom(
                    current_path if remove_metadata else input_path,
                    output_path if not convert_format else None,
                    method=text_removal_method,
                )
                results["steps_completed"].append("text_removal")
                results["text_removal"] = result["results"]
                
                # Update current path
                if not convert_format:
                    current_path = output_path
                
            except Exception as e:
                results["errors"].append(f"Text removal failed: {str(e)}")
                return results
        
        # Step 3: Convert format
        if convert_format:
            try:
                converter_map = {
                    "png": self.converter.dicom_to_png,
                    "jpg": self.converter.dicom_to_jpg,
                    "jpeg": self.converter.dicom_to_jpg,
                    "tiff": self.converter.dicom_to_tiff,
                    "npy": self.converter.dicom_to_numpy,
                }
                
                if convert_format.lower() not in converter_map:
                    raise ValueError(f"Unsupported format: {convert_format}")
                
                # Update output path extension
                output_path = output_path.with_suffix(f".{convert_format}")
                
                converter_map[convert_format.lower()](current_path, output_path)
                results["steps_completed"].append("format_conversion")
                results["output_format"] = convert_format
                
            except Exception as e:
                results["errors"].append(f"Format conversion failed: {str(e)}")
                return results
        
        # Step 4: Validate
        if validate_output and self.enable_validation and not convert_format:
            try:
                validation = self.validator.validate_dicom(output_path)
                results["validation"] = validation
                
                if self.enable_logging:
                    self.logger.log_validation({"files_checked": 1, **validation})
                
            except Exception as e:
                results["errors"].append(f"Validation failed: {str(e)}")
        
        results["success"] = len(results["errors"]) == 0
        return results
    
    def process_directory(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        remove_metadata: bool = True,
        remove_burned_text: bool = False,
        convert_format: Optional[str] = None,
        text_removal_method: str = "ocr",
        validate_output: bool = True,
        recursive: bool = True,
        validation_sample_rate: float = 0.1,
    ) -> Dict[str, any]:
        """
        Process entire directory of DICOM files.
        
        Args:
            input_dir: Directory containing DICOM files
            output_dir: Directory to save processed files
            remove_metadata: Remove PHI from metadata
            remove_burned_text: Remove burned-in text from pixels
            convert_format: Convert to format or None
            text_removal_method: Method for text removal
            validate_output: Validate outputs
            recursive: Process subdirectories
            validation_sample_rate: Fraction of files to validate (0.0-1.0)
        
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
            "validation_results": None,
        }
        
        # Process each file
        for dcm_file in dicom_files:
            try:
                # Preserve directory structure
                rel_path = dcm_file.relative_to(input_dir)
                output_path = output_dir / rel_path
                
                file_result = self.process_single_file(
                    dcm_file,
                    output_path,
                    remove_metadata=remove_metadata,
                    remove_burned_text=remove_burned_text,
                    convert_format=convert_format,
                    text_removal_method=text_removal_method,
                    validate_output=False,  # We'll do batch validation later
                )
                
                if file_result["success"]:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].extend(file_result["errors"])
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "file": str(dcm_file),
                    "error": str(e)
                })
        
        # Batch validation
        if validate_output and self.enable_validation and not convert_format:
            validation_results = self.validator.validate_batch(
                output_dir,
                recursive=recursive,
                sample_rate=validation_sample_rate,
            )
            results["validation_results"] = validation_results
            
            if self.enable_logging:
                self.logger.log_validation(validation_results)
        
        # Log batch operation
        if self.enable_logging:
            self.logger.log_batch_operation(results, "batch_deidentification")
        
        return results
    
    def generate_complete_report(
        self,
        processing_results: Dict[str, any],
        output_path: Union[str, Path],
    ) -> str:
        """
        Generate a comprehensive report of the entire workflow.
        
        Args:
            processing_results: Results from process_directory()
            output_path: Path to save report
        
        Returns:
            Report as string
        """
        report_lines = [
            "=" * 70,
            "COMPLETE DE-IDENTIFICATION WORKFLOW REPORT",
            "=" * 70,
            "",
            "PROCESSING SUMMARY",
            "-" * 70,
            f"Total Files: {processing_results['total_files']}",
            f"Successful: {processing_results['successful']}",
            f"Failed: {processing_results['failed']}",
            "",
        ]
        
        if processing_results['total_files'] > 0:
            success_rate = processing_results['successful'] / processing_results['total_files']
            report_lines.append(f"Success Rate: {success_rate:.1%}")
            report_lines.append("")
        
        # Validation results
        if processing_results.get("validation_results"):
            val_results = processing_results["validation_results"]
            report_lines.extend([
                "VALIDATION SUMMARY",
                "-" * 70,
                f"Files Validated: {val_results.get('files_checked', 0)}",
                f"Validation Passed: {val_results.get('passed', 0)}",
                f"Validation Failed: {val_results.get('failed', 0)}",
                "",
            ])
            
            if val_results.get("summary"):
                summary = val_results["summary"]
                report_lines.extend([
                    f"Validation Pass Rate: {summary.get('pass_rate', 0):.1%}",
                    f"Average Warnings: {summary.get('avg_warnings', 0):.2f}",
                    "",
                ])
        
        # Errors
        if processing_results.get("errors"):
            report_lines.extend([
                "ERRORS",
                "-" * 70,
            ])
            for i, error in enumerate(processing_results["errors"][:20], 1):
                if isinstance(error, dict):
                    report_lines.append(
                        f"{i}. {error.get('file', 'Unknown')}: {error.get('error', 'Unknown error')}"
                    )
                else:
                    report_lines.append(f"{i}. {error}")
            
            if len(processing_results["errors"]) > 20:
                report_lines.append(
                    f"\n... and {len(processing_results['errors']) - 20} more errors"
                )
            report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "RECOMMENDATIONS",
            "-" * 70,
            "✓ Review validation failures manually",
            "✓ Verify a sample of de-identified files",
            "✓ Check audit logs for complete operation history",
            "✓ Store original data separately and securely",
            "✓ Document the de-identification process used",
            "",
        ])
        
        report_lines.append("=" * 70)
        
        report = "\n".join(report_lines)
        
        # Save report
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report)
        
        return report
