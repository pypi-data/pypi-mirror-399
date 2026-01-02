"""
Re-identification Risk Assessment Module

Assesses the risk of re-identifying patients from de-identified datasets.
"""

import pydicom
from typing import List, Dict, Set, Union, Optional
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
from datetime import datetime


class RiskAssessment:
    """Assesses re-identification risk for de-identified datasets."""
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize the risk assessment.
        
        Args:
            strict_mode: Use stricter thresholds for risk assessment
        """
        self.strict_mode = strict_mode
        
        # Quasi-identifiers: fields that combined could re-identify patients
        self.quasi_identifiers = [
            "PatientAge",
            "PatientSex",
            "StudyDate",
            "Modality",
            "BodyPartExamined",
            "InstitutionName",
        ]
        
        # Risk thresholds
        if strict_mode:
            self.k_threshold = 5  # K-anonymity: at least 5 identical records
            self.l_threshold = 3  # L-diversity: at least 3 different sensitive values
        else:
            self.k_threshold = 3
            self.l_threshold = 2
    
    def calculate_k_anonymity(
        self,
        records: List[Dict[str, any]],
        quasi_identifiers: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """
        Calculate k-anonymity for a dataset.
        
        K-anonymity ensures that each record is indistinguishable from at least
        k-1 other records with respect to certain identifying attributes.
        
        Args:
            records: List of record dictionaries
            quasi_identifiers: List of quasi-identifier field names
        
        Returns:
            Dictionary with k-anonymity results
        """
        if quasi_identifiers is None:
            quasi_identifiers = self.quasi_identifiers
        
        # Group records by quasi-identifier combinations
        equivalence_classes = defaultdict(list)
        
        for i, record in enumerate(records):
            # Create tuple of quasi-identifier values
            qi_values = tuple(
                str(record.get(qi, "MISSING")) for qi in quasi_identifiers
            )
            equivalence_classes[qi_values].append(i)
        
        # Calculate k (minimum group size)
        group_sizes = [len(group) for group in equivalence_classes.values()]
        k = min(group_sizes) if group_sizes else 0
        
        # Calculate percentage of records in groups < threshold
        risky_records = sum(
            len(group) for group in equivalence_classes.values()
            if len(group) < self.k_threshold
        )
        risk_percentage = (risky_records / len(records) * 100) if records else 0
        
        return {
            "k_value": k,
            "k_threshold": self.k_threshold,
            "meets_threshold": k >= self.k_threshold,
            "num_equivalence_classes": len(equivalence_classes),
            "average_class_size": np.mean(group_sizes) if group_sizes else 0,
            "risky_records": risky_records,
            "risk_percentage": risk_percentage,
            "group_size_distribution": Counter(group_sizes),
        }
    
    def calculate_l_diversity(
        self,
        records: List[Dict[str, any]],
        sensitive_attribute: str,
        quasi_identifiers: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """
        Calculate l-diversity for a dataset.
        
        L-diversity ensures that each equivalence class has at least l
        well-represented values for sensitive attributes.
        
        Args:
            records: List of record dictionaries
            sensitive_attribute: Name of the sensitive attribute
            quasi_identifiers: List of quasi-identifier field names
        
        Returns:
            Dictionary with l-diversity results
        """
        if quasi_identifiers is None:
            quasi_identifiers = self.quasi_identifiers
        
        # Group records by quasi-identifier combinations
        equivalence_classes = defaultdict(list)
        
        for record in records:
            qi_values = tuple(
                str(record.get(qi, "MISSING")) for qi in quasi_identifiers
            )
            sensitive_value = str(record.get(sensitive_attribute, "MISSING"))
            equivalence_classes[qi_values].append(sensitive_value)
        
        # Calculate l (minimum diversity in any group)
        diversity_per_class = []
        for group_values in equivalence_classes.values():
            unique_values = len(set(group_values))
            diversity_per_class.append(unique_values)
        
        l = min(diversity_per_class) if diversity_per_class else 0
        
        # Calculate percentage of classes with diversity < threshold
        risky_classes = sum(
            1 for div in diversity_per_class if div < self.l_threshold
        )
        risk_percentage = (
            risky_classes / len(equivalence_classes) * 100
        ) if equivalence_classes else 0
        
        return {
            "l_value": l,
            "l_threshold": self.l_threshold,
            "meets_threshold": l >= self.l_threshold,
            "num_equivalence_classes": len(equivalence_classes),
            "average_diversity": np.mean(diversity_per_class) if diversity_per_class else 0,
            "risky_classes": risky_classes,
            "risk_percentage": risk_percentage,
        }
    
    def calculate_uniqueness(
        self,
        records: List[Dict[str, any]],
        quasi_identifiers: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """
        Calculate the percentage of unique records in the dataset.
        
        High uniqueness indicates higher re-identification risk.
        
        Args:
            records: List of record dictionaries
            quasi_identifiers: List of quasi-identifier field names
        
        Returns:
            Dictionary with uniqueness results
        """
        if quasi_identifiers is None:
            quasi_identifiers = self.quasi_identifiers
        
        # Count occurrences of each combination
        combinations = []
        for record in records:
            qi_values = tuple(
                str(record.get(qi, "MISSING")) for qi in quasi_identifiers
            )
            combinations.append(qi_values)
        
        counter = Counter(combinations)
        unique_records = sum(1 for count in counter.values() if count == 1)
        uniqueness_percentage = (unique_records / len(records) * 100) if records else 0
        
        return {
            "total_records": len(records),
            "unique_records": unique_records,
            "uniqueness_percentage": uniqueness_percentage,
            "high_risk": uniqueness_percentage > 20,  # >20% unique is risky
        }
    
    def assess_dicom_file(
        self,
        dicom_path: Union[str, Path, pydicom.Dataset],
    ) -> Dict[str, any]:
        """
        Assess re-identification risk for a single DICOM file.
        
        Args:
            dicom_path: Path to DICOM file or DICOM dataset
        
        Returns:
            Dictionary with risk assessment
        """
        # Load DICOM
        if isinstance(dicom_path, (str, Path)):
            ds = pydicom.dcmread(str(dicom_path))
        else:
            ds = dicom_path
        
        risk_factors = []
        
        # Check for remaining PHI
        phi_tags = [
            "PatientName",
            "PatientID",
            "PatientBirthDate",
            "PatientAddress",
            "PatientTelephoneNumbers",
        ]
        
        remaining_phi = []
        for tag in phi_tags:
            if tag in ds:
                value = str(ds.data_element(tag).value)
                if value and value.upper() not in ["ANONYMIZED", "REMOVED", ""]:
                    remaining_phi.append(tag)
                    risk_factors.append(f"PHI tag not anonymized: {tag}")
        
        # Check quasi-identifiers
        qi_present = []
        for qi in self.quasi_identifiers:
            if qi in ds:
                value = str(ds.data_element(qi).value)
                if value and value.upper() not in ["ANONYMIZED", "REMOVED", ""]:
                    qi_present.append(qi)
        
        # Calculate risk score (0-100)
        risk_score = 0
        
        # PHI present = very high risk
        risk_score += len(remaining_phi) * 30
        
        # Multiple quasi-identifiers = medium risk
        if len(qi_present) >= 4:
            risk_score += 40
            risk_factors.append(f"{len(qi_present)} quasi-identifiers present")
        elif len(qi_present) >= 2:
            risk_score += 20
        
        # Private tags present = low risk
        private_tags = sum(1 for elem in ds if elem.tag.is_private)
        if private_tags > 0:
            risk_score += min(private_tags * 2, 20)
            risk_factors.append(f"{private_tags} private tags present")
        
        risk_score = min(risk_score, 100)
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "remaining_phi": remaining_phi,
            "quasi_identifiers_present": qi_present,
            "private_tags_count": private_tags,
            "risk_factors": risk_factors,
        }
    
    def assess_dataset(
        self,
        input_dir: Union[str, Path],
        recursive: bool = True,
        sample_size: Optional[int] = None,
    ) -> Dict[str, any]:
        """
        Assess re-identification risk for an entire dataset.
        
        Args:
            input_dir: Directory containing DICOM files
            recursive: Process subdirectories
            sample_size: Limit analysis to sample (for large datasets)
        
        Returns:
            Dictionary with comprehensive risk assessment
        """
        input_dir = Path(input_dir)
        
        # Find DICOM files
        if recursive:
            dicom_files = list(input_dir.rglob("*.dcm"))
        else:
            dicom_files = list(input_dir.glob("*.dcm"))
        
        # Sample if requested
        if sample_size and len(dicom_files) > sample_size:
            import random
            dicom_files = random.sample(dicom_files, sample_size)
        
        # Extract records for analysis
        records = []
        individual_risks = []
        
        for dcm_file in dicom_files:
            try:
                ds = pydicom.dcmread(str(dcm_file))
                
                # Extract quasi-identifiers
                record = {}
                for qi in self.quasi_identifiers:
                    if qi in ds:
                        record[qi] = str(ds.data_element(qi).value)
                
                records.append(record)
                
                # Individual file risk
                file_risk = self.assess_dicom_file(ds)
                individual_risks.append(file_risk)
            
            except Exception as e:
                pass
        
        # Calculate k-anonymity
        k_anonymity = self.calculate_k_anonymity(records)
        
        # Calculate l-diversity (using PatientSex as example sensitive attribute)
        l_diversity = None
        if records and "PatientSex" in records[0]:
            l_diversity = self.calculate_l_diversity(records, "PatientSex")
        
        # Calculate uniqueness
        uniqueness = self.calculate_uniqueness(records)
        
        # Aggregate individual risks
        risk_scores = [r["risk_score"] for r in individual_risks]
        avg_risk_score = np.mean(risk_scores) if risk_scores else 0
        
        high_risk_files = sum(1 for r in individual_risks if r["risk_level"] == "HIGH")
        medium_risk_files = sum(1 for r in individual_risks if r["risk_level"] == "MEDIUM")
        low_risk_files = sum(1 for r in individual_risks if r["risk_level"] == "LOW")
        
        # Overall risk level
        if (
            not k_anonymity["meets_threshold"] or
            uniqueness["high_risk"] or
            avg_risk_score >= 70 or
            high_risk_files > len(dicom_files) * 0.1  # >10% high-risk files
        ):
            overall_risk = "HIGH"
        elif (
            avg_risk_score >= 40 or
            medium_risk_files > len(dicom_files) * 0.2  # >20% medium-risk files
        ):
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"
        
        return {
            "overall_risk_level": overall_risk,
            "files_analyzed": len(dicom_files),
            "average_risk_score": avg_risk_score,
            "k_anonymity": k_anonymity,
            "l_diversity": l_diversity,
            "uniqueness": uniqueness,
            "file_risk_distribution": {
                "high": high_risk_files,
                "medium": medium_risk_files,
                "low": low_risk_files,
            },
            "recommendations": self._generate_recommendations(
                overall_risk,
                k_anonymity,
                uniqueness,
                high_risk_files,
            ),
        }
    
    def _generate_recommendations(
        self,
        overall_risk: str,
        k_anonymity: Dict,
        uniqueness: Dict,
        high_risk_files: int,
    ) -> List[str]:
        """Generate recommendations based on risk assessment."""
        recommendations = []
        
        if overall_risk == "HIGH":
            recommendations.append(
                "⚠️ HIGH RISK: Do not share this dataset without further de-identification"
            )
        
        if not k_anonymity["meets_threshold"]:
            recommendations.append(
                f"Improve k-anonymity: Current k={k_anonymity['k_value']}, "
                f"threshold={k_anonymity['k_threshold']}"
            )
            recommendations.append(
                "Consider generalizing quasi-identifiers (e.g., age ranges instead of exact age)"
            )
        
        if uniqueness["high_risk"]:
            recommendations.append(
                f"High uniqueness detected: {uniqueness['uniqueness_percentage']:.1f}% "
                "of records are unique"
            )
            recommendations.append(
                "Consider removing or generalizing additional quasi-identifiers"
            )
        
        if high_risk_files > 0:
            recommendations.append(
                f"{high_risk_files} files contain potential PHI - review and re-process"
            )
        
        if overall_risk == "LOW":
            recommendations.append(
                "✓ Risk assessment passed - dataset appears adequately de-identified"
            )
            recommendations.append(
                "Note: Always conduct additional review before data sharing"
            )
        
        return recommendations
    
    def generate_report(
        self,
        assessment_results: Dict[str, any],
        output_path: Optional[Union[str, Path]] = None,
    ) -> str:
        """
        Generate a human-readable risk assessment report.
        
        Args:
            assessment_results: Results from assess_dataset()
            output_path: Optional path to save report
        
        Returns:
            Report as string
        """
        report_lines = [
            "=" * 70,
            "RE-IDENTIFICATION RISK ASSESSMENT REPORT",
            "=" * 70,
            "",
            f"Overall Risk Level: {assessment_results['overall_risk_level']}",
            f"Files Analyzed: {assessment_results['files_analyzed']}",
            f"Average Risk Score: {assessment_results['average_risk_score']:.1f}/100",
            "",
            "K-ANONYMITY ANALYSIS",
            "-" * 70,
        ]
        
        k_anon = assessment_results["k_anonymity"]
        report_lines.extend([
            f"K-value: {k_anon['k_value']} (threshold: {k_anon['k_threshold']})",
            f"Meets Threshold: {'✓ YES' if k_anon['meets_threshold'] else '✗ NO'}",
            f"Equivalence Classes: {k_anon['num_equivalence_classes']}",
            f"Average Class Size: {k_anon['average_class_size']:.1f}",
            f"Risky Records: {k_anon['risky_records']} ({k_anon['risk_percentage']:.1f}%)",
            "",
        ])
        
        if assessment_results.get("l_diversity"):
            l_div = assessment_results["l_diversity"]
            report_lines.extend([
                "L-DIVERSITY ANALYSIS",
                "-" * 70,
                f"L-value: {l_div['l_value']} (threshold: {l_div['l_threshold']})",
                f"Meets Threshold: {'✓ YES' if l_div['meets_threshold'] else '✗ NO'}",
                f"Average Diversity: {l_div['average_diversity']:.1f}",
                "",
            ])
        
        uniqueness = assessment_results["uniqueness"]
        report_lines.extend([
            "UNIQUENESS ANALYSIS",
            "-" * 70,
            f"Total Records: {uniqueness['total_records']}",
            f"Unique Records: {uniqueness['unique_records']}",
            f"Uniqueness: {uniqueness['uniqueness_percentage']:.1f}%",
            f"High Risk: {'✗ YES' if uniqueness['high_risk'] else '✓ NO'}",
            "",
        ])
        
        file_dist = assessment_results["file_risk_distribution"]
        report_lines.extend([
            "FILE RISK DISTRIBUTION",
            "-" * 70,
            f"High Risk: {file_dist['high']}",
            f"Medium Risk: {file_dist['medium']}",
            f"Low Risk: {file_dist['low']}",
            "",
        ])
        
        report_lines.extend([
            "RECOMMENDATIONS",
            "-" * 70,
        ])
        for rec in assessment_results["recommendations"]:
            report_lines.append(f"• {rec}")
        
        report_lines.append("\n" + "=" * 70)
        
        report = "\n".join(report_lines)
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report)
        
        return report
