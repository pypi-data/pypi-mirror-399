"""
DICOM File Generator

Generates sample DICOM files with and without PHI for testing the medimagecleaner package.
Creates realistic test files with various types of PHI.
"""

import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
import numpy as np
from datetime import datetime, timedelta
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class DICOMGenerator:
    """Generate sample DICOM files for testing."""
    
    def __init__(self, output_dir: str = "./sample_dicoms"):
        """
        Initialize the DICOM generator.
        
        Args:
            output_dir: Directory to save generated DICOM files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sample patient data
        self.sample_patients = [
            {
                "name": "Doe^John",
                "id": "12345678",
                "dob": "19800515",
                "sex": "M",
                "address": "123 Main St, New York, NY 10001",
                "phone": "(555) 123-4567",
            },
            {
                "name": "Smith^Jane",
                "id": "87654321",
                "dob": "19920308",
                "sex": "F",
                "address": "456 Oak Ave, Los Angeles, CA 90001",
                "phone": "(555) 987-6543",
            },
            {
                "name": "Johnson^Robert",
                "id": "11223344",
                "dob": "19750920",
                "sex": "M",
                "address": "789 Pine Rd, Chicago, IL 60601",
                "phone": "(555) 246-8135",
            },
        ]
        
        # Sample physicians
        self.sample_physicians = [
            "Smith^Emily^MD",
            "Johnson^Michael^MD",
            "Williams^Sarah^DO",
        ]
        
        # Sample institutions
        self.sample_institutions = [
            "General Hospital",
            "Medical Center",
            "University Hospital",
        ]
    
    def create_base_dicom(self, modality: str = "CT") -> FileDataset:
        """
        Create a base DICOM dataset with minimal required fields.
        
        Args:
            modality: DICOM modality (CT, MR, XR, etc.)
        
        Returns:
            Base DICOM dataset
        """
        # File meta information
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
        file_meta.MediaStorageSOPInstanceUID = generate_uid()
        file_meta.TransferSyntaxUID = '1.2.840.10008.1.2'  # Implicit VR Little Endian
        file_meta.ImplementationClassUID = generate_uid()
        
        # Create the FileDataset instance
        ds = FileDataset(
            None,
            {},
            file_meta=file_meta,
            preamble=b"\0" * 128
        )
        
        # Required DICOM fields
        ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
        ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        ds.StudyInstanceUID = generate_uid()
        ds.SeriesInstanceUID = generate_uid()
        ds.Modality = modality
        
        return ds
    
    def add_phi_metadata(
        self,
        ds: FileDataset,
        patient_info: dict,
        include_full_phi: bool = True
    ) -> FileDataset:
        """
        Add PHI to DICOM metadata.
        
        Args:
            ds: DICOM dataset
            patient_info: Patient information dictionary
            include_full_phi: If True, include all PHI types
        
        Returns:
            DICOM dataset with PHI
        """
        # Patient information
        ds.PatientName = patient_info["name"]
        ds.PatientID = patient_info["id"]
        ds.PatientBirthDate = patient_info["dob"]
        ds.PatientSex = patient_info["sex"]
        
        if include_full_phi:
            ds.PatientAddress = patient_info["address"]
            ds.PatientTelephoneNumbers = patient_info["phone"]
        
        # Institution information
        ds.InstitutionName = random.choice(self.sample_institutions)
        ds.InstitutionAddress = "1000 Medical Plaza, City, ST 12345"
        
        # Physician information
        ds.ReferringPhysicianName = random.choice(self.sample_physicians)
        ds.PerformingPhysicianName = random.choice(self.sample_physicians)
        
        # Study information
        study_date = datetime.now() - timedelta(days=random.randint(1, 365))
        ds.StudyDate = study_date.strftime("%Y%m%d")
        ds.StudyTime = study_date.strftime("%H%M%S")
        ds.AccessionNumber = f"ACC{random.randint(100000, 999999)}"
        ds.StudyDescription = f"{ds.Modality} Study"
        
        # Series information
        ds.SeriesDate = ds.StudyDate
        ds.SeriesTime = ds.StudyTime
        ds.SeriesDescription = f"{ds.Modality} Series"
        ds.SeriesNumber = "1"
        
        # Equipment information
        ds.Manufacturer = "Sample Manufacturer"
        ds.ManufacturerModelName = "Model X1000"
        ds.DeviceSerialNumber = f"SN{random.randint(10000, 99999)}"
        ds.StationName = f"STATION{random.randint(1, 10)}"
        
        return ds
    
    def create_image_with_text(
        self,
        width: int = 512,
        height: int = 512,
        text_content: str = None,
        include_face: bool = False
    ) -> np.ndarray:
        """
        Create a sample medical image with optional burned-in text.
        
        Args:
            width: Image width
            height: Image height
            text_content: Text to burn into image
            include_face: Add a simple face representation
        
        Returns:
            Image as numpy array
        """
        # Create base image (simulate CT/MR)
        image = np.random.randint(0, 256, (height, width), dtype=np.uint8)
        
        # Add some structure (simulate anatomy)
        center_y, center_x = height // 2, width // 2
        y, x = np.ogrid[:height, :width]
        
        # Circular structure (simulate organ)
        mask = (x - center_x)**2 + (y - center_y)**2 <= (min(width, height) // 4)**2
        image[mask] = np.clip(image[mask] + 100, 0, 255)
        
        # Convert to PIL for text/face drawing
        pil_image = Image.fromarray(image)
        draw = ImageDraw.Draw(pil_image)
        
        # Add text if provided
        if text_content:
            try:
                # Try to use a default font, fallback to basic if not available
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Add text to top-left corner
            draw.text((10, 10), text_content, fill=255, font=font)
        
        # Add simple face representation if requested
        if include_face:
            # Face circle in top-right
            face_x, face_y = width - 100, 80
            face_radius = 40
            
            # Face outline
            draw.ellipse(
                [face_x - face_radius, face_y - face_radius,
                 face_x + face_radius, face_y + face_radius],
                outline=255, width=2
            )
            
            # Eyes
            draw.ellipse([face_x - 20, face_y - 10, face_x - 10, face_y], fill=255)
            draw.ellipse([face_x + 10, face_y - 10, face_x + 20, face_y], fill=255)
            
            # Smile
            draw.arc(
                [face_x - 20, face_y - 5, face_x + 20, face_y + 20],
                start=0, end=180, fill=255, width=2
            )
        
        return np.array(pil_image)
    
    def add_pixel_data(
        self,
        ds: FileDataset,
        pixel_array: np.ndarray
    ) -> FileDataset:
        """
        Add pixel data to DICOM dataset.
        
        Args:
            ds: DICOM dataset
            pixel_array: Image data as numpy array
        
        Returns:
            DICOM dataset with pixel data
        """
        ds.Rows = pixel_array.shape[0]
        ds.Columns = pixel_array.shape[1]
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 0
        
        # Convert to 16-bit for DICOM
        pixel_array_16bit = pixel_array.astype(np.uint16) * 256
        ds.PixelData = pixel_array_16bit.tobytes()
        
        return ds
    
    def generate_dicom_with_phi(
        self,
        filename: str = "sample_with_phi.dcm",
        include_burned_text: bool = True,
        include_face: bool = True,
    ) -> str:
        """
        Generate a DICOM file with PHI.
        
        Args:
            filename: Output filename
            include_burned_text: Include burned-in patient info
            include_face: Include a face in the image
        
        Returns:
            Path to generated file
        """
        # Create base DICOM
        ds = self.create_base_dicom(modality="CT")
        
        # Add PHI metadata
        patient = random.choice(self.sample_patients)
        ds = self.add_phi_metadata(ds, patient, include_full_phi=True)
        
        # Create image with burned-in text
        burned_text = None
        if include_burned_text:
            burned_text = f"{patient['name']} | {patient['id']} | DOB: {patient['dob']}"
        
        pixel_array = self.create_image_with_text(
            text_content=burned_text,
            include_face=include_face
        )
        
        # Add pixel data
        ds = self.add_pixel_data(ds, pixel_array)
        
        # Save
        output_path = self.output_dir / filename
        ds.save_as(output_path, write_like_original=False)
        
        return str(output_path)
    
    def generate_dicom_without_phi(
        self,
        filename: str = "sample_no_phi.dcm",
    ) -> str:
        """
        Generate a de-identified DICOM file.
        
        Args:
            filename: Output filename
        
        Returns:
            Path to generated file
        """
        # Create base DICOM
        ds = self.create_base_dicom(modality="CT")
        
        # Add anonymized metadata
        ds.PatientName = "ANONYMIZED"
        ds.PatientID = "ANON123456"
        ds.PatientBirthDate = ""
        ds.PatientSex = "O"
        
        # Minimal study information
        ds.StudyDate = "20240101"
        ds.StudyTime = "120000"
        ds.StudyDescription = "CT Study"
        
        ds.SeriesDate = ds.StudyDate
        ds.SeriesTime = ds.StudyTime
        ds.SeriesDescription = "CT Series"
        ds.SeriesNumber = "1"
        
        # Create clean image (no text, no face)
        pixel_array = self.create_image_with_text(
            text_content=None,
            include_face=False
        )
        
        # Add pixel data
        ds = self.add_pixel_data(ds, pixel_array)
        
        # Save
        output_path = self.output_dir / filename
        ds.save_as(output_path, write_like_original=False)
        
        return str(output_path)
    
    def generate_test_dataset(self) -> dict:
        """
        Generate a complete test dataset with various scenarios.
        
        Returns:
            Dictionary with paths to generated files
        """
        files = {
            "with_phi": [],
            "without_phi": [],
        }
        
        print("Generating test DICOM dataset...")
        print(f"Output directory: {self.output_dir}")
        
        # Create subdirectories
        phi_dir = self.output_dir / "with_phi"
        no_phi_dir = self.output_dir / "no_phi"
        phi_dir.mkdir(exist_ok=True)
        no_phi_dir.mkdir(exist_ok=True)
        
        # Generate files WITH PHI (10 files)
        print("\nGenerating files WITH PHI...")
        for i in range(10):
            filename = f"patient_{i+1:03d}_with_phi.dcm"
            
            # Vary the PHI types
            include_text = (i % 2 == 0)  # Every other has burned text
            include_face = (i % 3 == 0)  # Every third has face
            
            filepath = self.generate_dicom_with_phi(
                filename=f"with_phi/{filename}",
                include_burned_text=include_text,
                include_face=include_face
            )
            files["with_phi"].append(filepath)
            
            phi_types = []
            if include_text:
                phi_types.append("burned text")
            if include_face:
                phi_types.append("face")
            phi_types.append("metadata PHI")
            
            print(f"  ✓ {filename} ({', '.join(phi_types)})")
        
        # Generate files WITHOUT PHI (10 files)
        print("\nGenerating files WITHOUT PHI (clean)...")
        for i in range(10):
            filename = f"patient_{i+1:03d}_no_phi.dcm"
            filepath = self.generate_dicom_without_phi(
                filename=f"no_phi/{filename}"
            )
            files["without_phi"].append(filepath)
            print(f"  ✓ {filename}")
        
        # Generate mixed directory for testing
        mixed_dir = self.output_dir / "mixed"
        mixed_dir.mkdir(exist_ok=True)
        
        print("\nGenerating MIXED directory (for batch testing)...")
        for i in range(5):
            # Some with PHI
            self.generate_dicom_with_phi(
                filename=f"mixed/scan_{i+1:03d}_phi.dcm",
                include_burned_text=True,
                include_face=(i % 2 == 0)
            )
            # Some without
            self.generate_dicom_without_phi(
                filename=f"mixed/scan_{i+6:03d}_clean.dcm"
            )
        print(f"  ✓ Created 10 files (5 with PHI, 5 clean)")
        
        return files


def main():
    """Generate sample DICOM files."""
    print("=" * 60)
    print("DICOM Test File Generator")
    print("=" * 60)
    
    generator = DICOMGenerator(output_dir="./sample_dicoms")
    files = generator.generate_test_dataset()
    
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\nGenerated files:")
    print(f"  • Files WITH PHI: {len(files['with_phi'])}")
    print(f"  • Files WITHOUT PHI: {len(files['without_phi'])}")
    print(f"  • Total: {len(files['with_phi']) + len(files['without_phi'])}")
    
    print(f"\nDirectory structure:")
    print(f"  ./sample_dicoms/")
    print(f"    ├── with_phi/        (10 files with various PHI)")
    print(f"    ├── no_phi/          (10 clean files)")
    print(f"    └── mixed/           (10 files - 5 with PHI, 5 clean)")
    
    print("\n" + "=" * 60)
    print("TEST SCENARIOS")
    print("=" * 60)
    print("\n1. PHI Detection Test:")
    print("   python -c \"from medimagecleaner import PHIDetector; \\")
    print("   detector = PHIDetector(); \\")
    print("   report = detector.check_file('./sample_dicoms/with_phi/patient_001_with_phi.dcm'); \\")
    print("   print(f'PHI Detected: {report[\\\"phi_detected\\\"]}')")
    print('"')
    
    print("\n2. Batch Detection Test:")
    print("   python -c \"from medimagecleaner import PHIDetector; \\")
    print("   detector = PHIDetector(); \\")
    print("   results = detector.check_directory('./sample_dicoms/mixed'); \\")
    print("   print(f'Files with PHI: {results[\\\"files_with_phi\\\"]} / {results[\\\"total_files\\\"]}')")
    print('"')
    
    print("\n3. De-identification Test:")
    print("   python -c \"from medimagecleaner import BatchProcessor; \\")
    print("   processor = BatchProcessor(); \\")
    print("   results = processor.process_directory('./sample_dicoms/with_phi', './deidentified')")
    print('"')
    
    print("\n4. Validation Test:")
    print("   python -c \"from medimagecleaner import DeidentificationValidator; \\")
    print("   validator = DeidentificationValidator(); \\")
    print("   result = validator.validate_dicom('./sample_dicoms/no_phi/patient_001_no_phi.dcm'); \\")
    print("   print(f'Passed: {result[\\\"passed\\\"]}')")
    print('"')
    
    print("\n" + "=" * 60)
    print("\nNext Steps:")
    print("  1. Examine the generated DICOM files")
    print("  2. Test PHI detection features")
    print("  3. Test de-identification workflow")
    print("  4. Verify validation works correctly")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
