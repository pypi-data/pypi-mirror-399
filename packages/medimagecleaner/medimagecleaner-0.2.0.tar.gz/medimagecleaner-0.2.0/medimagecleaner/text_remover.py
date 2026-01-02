"""
Text Removal Module

Handles detection and removal of burned-in text from medical images.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Union, Dict
from pathlib import Path
import pydicom

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class TextRemover:
    """Removes burned-in text from medical images."""
    
    def __init__(
        self,
        ocr_enabled: bool = True,
        confidence_threshold: float = 30.0,
        mask_color: Tuple[int, int, int] = (0, 0, 0),
        padding: int = 5,
    ):
        """
        Initialize the text remover.
        
        Args:
            ocr_enabled: Use OCR to detect text automatically
            confidence_threshold: Minimum OCR confidence to mask text
            mask_color: Color to use for masking (default: black)
            padding: Pixels to add around detected text boxes
        """
        self.ocr_enabled = ocr_enabled and TESSERACT_AVAILABLE
        self.confidence_threshold = confidence_threshold
        self.mask_color = mask_color
        self.padding = padding
        
        if ocr_enabled and not TESSERACT_AVAILABLE:
            print("Warning: pytesseract not available. OCR disabled.")
    
    def crop_region(
        self,
        image: np.ndarray,
        crop_top: float = 0.0,
        crop_bottom: float = 0.0,
        crop_left: float = 0.0,
        crop_right: float = 0.0,
    ) -> np.ndarray:
        """
        Crop specified regions from image (useful for removing fixed-location text).
        
        Args:
            image: Input image as numpy array
            crop_top: Fraction of height to crop from top (0.0-1.0)
            crop_bottom: Fraction of height to crop from bottom (0.0-1.0)
            crop_left: Fraction of width to crop from left (0.0-1.0)
            crop_right: Fraction of width to crop from right (0.0-1.0)
        
        Returns:
            Cropped image
        """
        h, w = image.shape[:2]
        
        top = int(h * crop_top)
        bottom = h - int(h * crop_bottom)
        left = int(w * crop_left)
        right = w - int(w * crop_right)
        
        return image[top:bottom, left:right]
    
    def mask_region(
        self,
        image: np.ndarray,
        regions: List[Tuple[int, int, int, int]],
    ) -> np.ndarray:
        """
        Mask specified rectangular regions in the image.
        
        Args:
            image: Input image as numpy array
            regions: List of (x, y, width, height) tuples
        
        Returns:
            Image with masked regions
        """
        result = image.copy()
        
        for x, y, w, h in regions:
            # Add padding
            x = max(0, x - self.padding)
            y = max(0, y - self.padding)
            w = w + 2 * self.padding
            h = h + 2 * self.padding
            
            cv2.rectangle(result, (x, y), (x + w, y + h), self.mask_color, -1)
        
        return result
    
    def detect_text_ocr(
        self,
        image: np.ndarray,
        language: str = "eng",
    ) -> List[Dict[str, any]]:
        """
        Detect text in image using OCR.
        
        Args:
            image: Input image as numpy array
            language: Language for OCR (default: English)
        
        Returns:
            List of detected text regions with confidence scores
        """
        if not self.ocr_enabled:
            raise RuntimeError("OCR not available. Install pytesseract.")
        
        # Convert to grayscale for better OCR
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Enhance contrast
        gray = cv2.equalizeHist(gray)
        
        # Run OCR
        data = pytesseract.image_to_data(
            gray,
            lang=language,
            output_type=pytesseract.Output.DICT
        )
        
        # Extract text regions above confidence threshold
        text_regions = []
        for i in range(len(data["text"])):
            text = data["text"][i].strip()
            conf = float(data["conf"][i])
            
            if text and conf >= self.confidence_threshold:
                text_regions.append({
                    "text": text,
                    "confidence": conf,
                    "bbox": (
                        data["left"][i],
                        data["top"][i],
                        data["width"][i],
                        data["height"][i],
                    ),
                })
        
        return text_regions
    
    def remove_text_ocr(
        self,
        image: np.ndarray,
        language: str = "eng",
    ) -> Tuple[np.ndarray, List[Dict[str, any]]]:
        """
        Automatically detect and remove text using OCR.
        
        Args:
            image: Input image as numpy array
            language: Language for OCR
        
        Returns:
            Tuple of (masked image, detected text regions)
        """
        text_regions = self.detect_text_ocr(image, language)
        bboxes = [region["bbox"] for region in text_regions]
        masked_image = self.mask_region(image, bboxes)
        
        return masked_image, text_regions
    
    def detect_text_edges(
        self,
        image: np.ndarray,
        min_area: int = 100,
        max_area: Optional[int] = None,
    ) -> List[Tuple[int, int, int, int]]:
        """
        Detect text-like regions using edge detection and contours.
        
        Args:
            image: Input image as numpy array
            min_area: Minimum contour area to consider
            max_area: Maximum contour area to consider
        
        Returns:
            List of bounding boxes (x, y, width, height)
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate to connect nearby edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(
            dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter contours by area and aspect ratio
        bboxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < min_area:
                continue
            if max_area and area > max_area:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            
            # Text typically has specific aspect ratios
            if 0.2 < aspect_ratio < 10:
                bboxes.append((x, y, w, h))
        
        return bboxes
    
    def process_dicom(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        method: str = "ocr",
        **kwargs
    ) -> Dict[str, any]:
        """
        Remove text from DICOM file's pixel data.
        
        Args:
            input_path: Path to input DICOM file
            output_path: Path to save processed file
            method: Method to use ('ocr', 'crop', 'edges')
            **kwargs: Additional arguments for specific methods
        
        Returns:
            Dictionary with processing results
        """
        # Load DICOM
        ds = pydicom.dcmread(str(input_path))
        
        # Get pixel array
        pixel_array = ds.pixel_array
        
        # Convert to appropriate format for OpenCV
        if pixel_array.dtype != np.uint8:
            # Normalize to 0-255
            pixel_array = cv2.normalize(
                pixel_array, None, 0, 255, cv2.NORM_MINMAX
            ).astype(np.uint8)
        
        # Apply method
        results = {"method": method}
        
        if method == "ocr":
            processed, text_regions = self.remove_text_ocr(pixel_array, **kwargs)
            results["text_regions"] = text_regions
        
        elif method == "crop":
            processed = self.crop_region(pixel_array, **kwargs)
        
        elif method == "edges":
            bboxes = self.detect_text_edges(pixel_array, **kwargs)
            processed = self.mask_region(pixel_array, bboxes)
            results["detected_regions"] = len(bboxes)
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Update DICOM pixel data
        ds.PixelData = processed.tobytes()
        ds.Rows, ds.Columns = processed.shape[:2]
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            ds.save_as(str(output_path))
            results["output_path"] = str(output_path)
        
        results["success"] = True
        return {"dataset": ds, "results": results}
    
    def process_image(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        method: str = "ocr",
        **kwargs
    ) -> Dict[str, any]:
        """
        Remove text from standard image file.
        
        Args:
            input_path: Path to input image
            output_path: Path to save processed image
            method: Method to use ('ocr', 'crop', 'edges')
            **kwargs: Additional arguments for specific methods
        
        Returns:
            Dictionary with processing results
        """
        # Load image
        image = cv2.imread(str(input_path))
        
        # Apply method
        results = {"method": method}
        
        if method == "ocr":
            processed, text_regions = self.remove_text_ocr(image, **kwargs)
            results["text_regions"] = text_regions
        
        elif method == "crop":
            processed = self.crop_region(image, **kwargs)
        
        elif method == "edges":
            bboxes = self.detect_text_edges(image, **kwargs)
            processed = self.mask_region(image, bboxes)
            results["detected_regions"] = len(bboxes)
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), processed)
            results["output_path"] = str(output_path)
        
        results["success"] = True
        return {"image": processed, "results": results}
