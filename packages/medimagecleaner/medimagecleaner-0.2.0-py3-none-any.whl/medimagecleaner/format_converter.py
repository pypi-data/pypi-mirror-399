"""
Format Converter Module

Converts DICOM files to standard image formats after de-identification.
"""

import numpy as np
from PIL import Image
import pydicom
from typing import Union, Optional, Tuple
from pathlib import Path
import cv2


class FormatConverter:
    """Converts de-identified DICOM files to standard image formats."""
    
    def __init__(
        self,
        normalize: bool = True,
        apply_windowing: bool = True,
        resize: Optional[Tuple[int, int]] = None,
    ):
        """
        Initialize the format converter.
        
        Args:
            normalize: Normalize pixel values to 0-255
            apply_windowing: Apply DICOM window/level settings
            resize: Optional (width, height) to resize images
        """
        self.normalize = normalize
        self.apply_windowing = apply_windowing
        self.resize = resize
    
    def _apply_window_level(
        self,
        pixel_array: np.ndarray,
        window_center: float,
        window_width: float,
    ) -> np.ndarray:
        """Apply DICOM windowing to pixel array."""
        lower = window_center - window_width / 2
        upper = window_center + window_width / 2
        
        windowed = np.clip(pixel_array, lower, upper)
        windowed = ((windowed - lower) / (upper - lower) * 255).astype(np.uint8)
        
        return windowed
    
    def _normalize_array(self, pixel_array: np.ndarray) -> np.ndarray:
        """Normalize pixel array to 0-255 range."""
        if pixel_array.dtype == np.uint8:
            return pixel_array
        
        # Normalize to 0-255
        normalized = cv2.normalize(
            pixel_array, None, 0, 255, cv2.NORM_MINMAX
        ).astype(np.uint8)
        
        return normalized
    
    def dicom_to_array(self, ds: pydicom.Dataset) -> np.ndarray:
        """
        Convert DICOM dataset to numpy array.
        
        Args:
            ds: DICOM dataset
        
        Returns:
            Processed pixel array
        """
        pixel_array = ds.pixel_array
        
        # Apply windowing if available and requested
        if self.apply_windowing:
            if hasattr(ds, "WindowCenter") and hasattr(ds, "WindowWidth"):
                window_center = ds.WindowCenter
                window_width = ds.WindowWidth
                
                # Handle multiple windows
                if isinstance(window_center, (list, tuple)):
                    window_center = window_center[0]
                if isinstance(window_width, (list, tuple)):
                    window_width = window_width[0]
                
                pixel_array = self._apply_window_level(
                    pixel_array, window_center, window_width
                )
        
        # Normalize if requested
        if self.normalize and pixel_array.dtype != np.uint8:
            pixel_array = self._normalize_array(pixel_array)
        
        # Handle photometric interpretation
        if hasattr(ds, "PhotometricInterpretation"):
            if ds.PhotometricInterpretation == "MONOCHROME1":
                # Invert grayscale
                pixel_array = 255 - pixel_array
        
        # Resize if requested
        if self.resize:
            pixel_array = cv2.resize(
                pixel_array, self.resize, interpolation=cv2.INTER_LANCZOS4
            )
        
        return pixel_array
    
    def dicom_to_png(
        self,
        input_path: Union[str, Path, pydicom.Dataset],
        output_path: Union[str, Path],
    ) -> bool:
        """
        Convert DICOM to PNG format.
        
        Args:
            input_path: Path to DICOM file or DICOM dataset
            output_path: Path to save PNG file
        
        Returns:
            True if successful
        """
        # Load DICOM if path provided
        if isinstance(input_path, (str, Path)):
            ds = pydicom.dcmread(str(input_path))
        else:
            ds = input_path
        
        # Convert to array
        pixel_array = self.dicom_to_array(ds)
        
        # Save as PNG
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        img = Image.fromarray(pixel_array)
        img.save(str(output_path), "PNG")
        
        return True
    
    def dicom_to_jpg(
        self,
        input_path: Union[str, Path, pydicom.Dataset],
        output_path: Union[str, Path],
        quality: int = 95,
    ) -> bool:
        """
        Convert DICOM to JPEG format.
        
        Args:
            input_path: Path to DICOM file or DICOM dataset
            output_path: Path to save JPEG file
            quality: JPEG quality (1-100)
        
        Returns:
            True if successful
        """
        # Load DICOM if path provided
        if isinstance(input_path, (str, Path)):
            ds = pydicom.dcmread(str(input_path))
        else:
            ds = input_path
        
        # Convert to array
        pixel_array = self.dicom_to_array(ds)
        
        # Save as JPEG
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        img = Image.fromarray(pixel_array)
        img.save(str(output_path), "JPEG", quality=quality)
        
        return True
    
    def dicom_to_tiff(
        self,
        input_path: Union[str, Path, pydicom.Dataset],
        output_path: Union[str, Path],
        compression: Optional[str] = "tiff_lzw",
    ) -> bool:
        """
        Convert DICOM to TIFF format.
        
        Args:
            input_path: Path to DICOM file or DICOM dataset
            output_path: Path to save TIFF file
            compression: Compression method (None, 'tiff_lzw', 'tiff_deflate')
        
        Returns:
            True if successful
        """
        # Load DICOM if path provided
        if isinstance(input_path, (str, Path)):
            ds = pydicom.dcmread(str(input_path))
        else:
            ds = input_path
        
        # Convert to array
        pixel_array = self.dicom_to_array(ds)
        
        # Save as TIFF
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        img = Image.fromarray(pixel_array)
        img.save(str(output_path), "TIFF", compression=compression)
        
        return True
    
    def dicom_to_numpy(
        self,
        input_path: Union[str, Path, pydicom.Dataset],
        output_path: Union[str, Path],
    ) -> bool:
        """
        Convert DICOM to numpy array file (.npy).
        
        Args:
            input_path: Path to DICOM file or DICOM dataset
            output_path: Path to save .npy file
        
        Returns:
            True if successful
        """
        # Load DICOM if path provided
        if isinstance(input_path, (str, Path)):
            ds = pydicom.dcmread(str(input_path))
        else:
            ds = input_path
        
        # Convert to array
        pixel_array = self.dicom_to_array(ds)
        
        # Save as numpy array
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        np.save(str(output_path), pixel_array)
        
        return True
    
    def batch_convert(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        output_format: str = "png",
        recursive: bool = True,
        **kwargs
    ) -> dict:
        """
        Batch convert DICOM files to specified format.
        
        Args:
            input_dir: Directory containing DICOM files
            output_dir: Directory to save converted files
            output_format: Output format ('png', 'jpg', 'tiff', 'npy')
            recursive: Process subdirectories recursively
            **kwargs: Additional arguments for specific converters
        
        Returns:
            Dictionary with conversion results
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all DICOM files
        if recursive:
            dicom_files = list(input_dir.rglob("*.dcm"))
        else:
            dicom_files = list(input_dir.glob("*.dcm"))
        
        # Select conversion method
        converter_map = {
            "png": self.dicom_to_png,
            "jpg": self.dicom_to_jpg,
            "jpeg": self.dicom_to_jpg,
            "tiff": self.dicom_to_tiff,
            "tif": self.dicom_to_tiff,
            "npy": self.dicom_to_numpy,
        }
        
        if output_format.lower() not in converter_map:
            raise ValueError(f"Unsupported format: {output_format}")
        
        converter = converter_map[output_format.lower()]
        
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
                output_path = output_dir / rel_path.with_suffix(f".{output_format}")
                
                converter(dcm_file, output_path, **kwargs)
                results["successful"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "file": str(dcm_file),
                    "error": str(e)
                })
        
        return results
