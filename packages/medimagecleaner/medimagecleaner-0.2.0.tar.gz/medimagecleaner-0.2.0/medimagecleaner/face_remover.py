"""
Face Detection and Removal Module

Detects and removes/blurs faces in medical images to protect patient privacy.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Union, Dict, Literal
from pathlib import Path
import pydicom


class FaceRemover:
    """Detects and removes faces from medical images."""
    
    def __init__(
        self,
        method: Literal["blur", "pixelate", "black_box", "remove"] = "blur",
        blur_strength: int = 25,
        pixelate_size: int = 10,
        detection_confidence: float = 0.5,
        cascade_path: Optional[str] = None,
    ):
        """
        Initialize the face remover.
        
        Args:
            method: Method for face removal ('blur', 'pixelate', 'black_box', 'remove')
            blur_strength: Gaussian blur kernel size (must be odd)
            pixelate_size: Size of pixelation blocks
            detection_confidence: Confidence threshold for DNN-based detection
            cascade_path: Path to custom Haar cascade file
        """
        self.method = method
        self.blur_strength = blur_strength if blur_strength % 2 == 1 else blur_strength + 1
        self.pixelate_size = pixelate_size
        self.detection_confidence = detection_confidence
        
        # Load Haar cascade for face detection
        if cascade_path:
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        else:
            # Use OpenCV's pre-trained model
            cascade_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_file)
        
        # Try to load DNN model for better detection
        self.use_dnn = False
        try:
            # OpenCV DNN face detector (more accurate)
            model_file = "deploy.prototxt"
            weights_file = "res10_300x300_ssd_iter_140000.caffemodel"
            # Note: These files need to be downloaded separately
            # self.net = cv2.dnn.readNetFromCaffe(model_file, weights_file)
            # self.use_dnn = True
        except:
            pass
    
    def detect_faces_haar(
        self,
        image: np.ndarray,
        scale_factor: float = 1.1,
        min_neighbors: int = 5,
        min_size: Tuple[int, int] = (30, 30),
    ) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using Haar cascade.
        
        Args:
            image: Input image
            scale_factor: Scale factor for multi-scale detection
            min_neighbors: Minimum neighbors for detection
            min_size: Minimum face size
        
        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors,
            minSize=min_size
        )
        
        return [(x, y, w, h) for (x, y, w, h) in faces]
    
    def detect_faces_dnn(
        self,
        image: np.ndarray,
    ) -> List[Tuple[int, int, int, int]]:
        """
        Detect faces using DNN (more accurate but requires model files).
        
        Args:
            image: Input image
        
        Returns:
            List of face bounding boxes (x, y, w, h)
        """
        if not self.use_dnn:
            return self.detect_faces_haar(image)
        
        h, w = image.shape[:2]
        
        # Prepare image for DNN
        blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)),
            1.0,
            (300, 300),
            (104.0, 177.0, 123.0)
        )
        
        self.net.setInput(blob)
        detections = self.net.forward()
        
        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            
            if confidence > self.detection_confidence:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                x, y, x2, y2 = box.astype("int")
                faces.append((x, y, x2 - x, y2 - y))
        
        return faces
    
    def _apply_blur(
        self,
        image: np.ndarray,
        x: int, y: int, w: int, h: int,
    ) -> np.ndarray:
        """Apply Gaussian blur to face region."""
        result = image.copy()
        face_region = result[y:y+h, x:x+w]
        blurred = cv2.GaussianBlur(face_region, (self.blur_strength, self.blur_strength), 0)
        result[y:y+h, x:x+w] = blurred
        return result
    
    def _apply_pixelate(
        self,
        image: np.ndarray,
        x: int, y: int, w: int, h: int,
    ) -> np.ndarray:
        """Apply pixelation to face region."""
        result = image.copy()
        face_region = result[y:y+h, x:x+w]
        
        # Downscale then upscale for pixelation effect
        temp = cv2.resize(
            face_region,
            (self.pixelate_size, self.pixelate_size),
            interpolation=cv2.INTER_LINEAR
        )
        pixelated = cv2.resize(
            temp,
            (w, h),
            interpolation=cv2.INTER_NEAREST
        )
        
        result[y:y+h, x:x+w] = pixelated
        return result
    
    def _apply_black_box(
        self,
        image: np.ndarray,
        x: int, y: int, w: int, h: int,
    ) -> np.ndarray:
        """Cover face with black box."""
        result = image.copy()
        cv2.rectangle(result, (x, y), (x+w, y+h), (0, 0, 0), -1)
        return result
    
    def _apply_removal(
        self,
        image: np.ndarray,
        x: int, y: int, w: int, h: int,
    ) -> np.ndarray:
        """Remove face region using inpainting."""
        result = image.copy()
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.rectangle(mask, (x, y), (x+w, y+h), 255, -1)
        
        # Use inpainting to fill the region
        inpainted = cv2.inpaint(result, mask, 3, cv2.INPAINT_TELEA)
        return inpainted
    
    def remove_faces(
        self,
        image: np.ndarray,
        padding: int = 10,
    ) -> Tuple[np.ndarray, List[Dict[str, any]]]:
        """
        Detect and remove faces from image.
        
        Args:
            image: Input image
            padding: Additional pixels around detected face
        
        Returns:
            Tuple of (processed image, detected face info)
        """
        # Detect faces
        faces = self.detect_faces_haar(image)
        
        face_info = []
        result = image.copy()
        
        for (x, y, w, h) in faces:
            # Add padding
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            
            # Apply selected method
            if self.method == "blur":
                result = self._apply_blur(result, x, y, w, h)
            elif self.method == "pixelate":
                result = self._apply_pixelate(result, x, y, w, h)
            elif self.method == "black_box":
                result = self._apply_black_box(result, x, y, w, h)
            elif self.method == "remove":
                result = self._apply_removal(result, x, y, w, h)
            
            face_info.append({
                "bbox": (x, y, w, h),
                "method": self.method,
            })
        
        return result, face_info
    
    def process_image(
        self,
        input_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> Dict[str, any]:
        """
        Process a standard image file.
        
        Args:
            input_path: Path to input image
            output_path: Path to save processed image
            **kwargs: Additional arguments for remove_faces()
        
        Returns:
            Dictionary with processing results
        """
        # Load image
        image = cv2.imread(str(input_path))
        
        # Process
        processed, face_info = self.remove_faces(image, **kwargs)
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(str(output_path), processed)
        
        return {
            "success": True,
            "faces_detected": len(face_info),
            "faces": face_info,
            "output_path": str(output_path) if output_path else None,
        }
    
    def process_dicom(
        self,
        input_path: Union[str, Path, pydicom.Dataset],
        output_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> Dict[str, any]:
        """
        Process a DICOM file.
        
        Args:
            input_path: Path to DICOM file or DICOM dataset
            output_path: Path to save processed file
            **kwargs: Additional arguments for remove_faces()
        
        Returns:
            Dictionary with processing results
        """
        # Load DICOM
        if isinstance(input_path, (str, Path)):
            ds = pydicom.dcmread(str(input_path))
        else:
            ds = input_path
        
        # Get pixel array
        pixel_array = ds.pixel_array
        
        # Convert to appropriate format for OpenCV
        if pixel_array.dtype != np.uint8:
            pixel_array = cv2.normalize(
                pixel_array, None, 0, 255, cv2.NORM_MINMAX
            ).astype(np.uint8)
        
        # Convert to 3-channel if grayscale
        if len(pixel_array.shape) == 2:
            pixel_array = cv2.cvtColor(pixel_array, cv2.COLOR_GRAY2BGR)
        
        # Process
        processed, face_info = self.remove_faces(pixel_array, **kwargs)
        
        # Convert back to grayscale if needed
        if len(ds.pixel_array.shape) == 2:
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
        
        # Update DICOM pixel data
        ds.PixelData = processed.tobytes()
        ds.Rows, ds.Columns = processed.shape[:2]
        
        # Save if output path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            ds.save_as(str(output_path))
        
        return {
            "dataset": ds,
            "success": True,
            "faces_detected": len(face_info),
            "faces": face_info,
            "output_path": str(output_path) if output_path else None,
        }
    
    def batch_process(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        file_pattern: str = "*.jpg",
        recursive: bool = True,
    ) -> Dict[str, any]:
        """
        Process multiple image files.
        
        Args:
            input_dir: Directory containing images
            output_dir: Directory to save processed images
            file_pattern: File pattern to match (e.g., "*.jpg", "*.dcm")
            recursive: Process subdirectories
        
        Returns:
            Dictionary with batch processing results
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find files
        if recursive:
            files = list(input_dir.rglob(file_pattern))
        else:
            files = list(input_dir.glob(file_pattern))
        
        results = {
            "total_files": len(files),
            "successful": 0,
            "failed": 0,
            "total_faces_detected": 0,
            "errors": [],
        }
        
        for file_path in files:
            try:
                # Preserve directory structure
                rel_path = file_path.relative_to(input_dir)
                output_path = output_dir / rel_path
                
                # Process based on file type
                if file_path.suffix.lower() == '.dcm':
                    result = self.process_dicom(file_path, output_path)
                else:
                    result = self.process_image(file_path, output_path)
                
                if result["success"]:
                    results["successful"] += 1
                    results["total_faces_detected"] += result["faces_detected"]
            
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
        
        return results
