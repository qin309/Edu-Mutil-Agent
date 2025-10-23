"""
Document scanning and correction service using computer vision
"""
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional, Dict, Any
import io


class DocScanner:
    """
    Document scanner for correcting skewed documents
    """

    @staticmethod
    def preprocess_image(image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better edge detection
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Edge detection using Canny
        edged = cv2.Canny(blurred, 50, 150)

        return edged

    @staticmethod
    def find_document_contour(edged: np.ndarray) -> Optional[np.ndarray]:
        """
        Find the document contour in the edged image
        """
        # Find contours
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        # Sort contours by area (largest first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        # Find the contour with approximately 4 corners (document)
        for contour in contours:
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)

            # Check if contour has 4 corners and is reasonably large
            if len(approx) == 4 and cv2.contourArea(contour) > 1000:
                return approx

        return None

    @staticmethod
    def order_points(pts: np.ndarray) -> np.ndarray:
        """
        Order points in clockwise order starting from top-left
        """
        # Sort by sum (top-left has smallest sum)
        # Sort by difference (top-right has smallest difference)
        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)

        rect[0] = pts[np.argmin(s)]  # Top-left
        rect[2] = pts[np.argmax(s)]  # Bottom-right
        rect[1] = pts[np.argmin(diff)]  # Top-right
        rect[3] = pts[np.argmax(diff)]  # Bottom-left

        return rect

    @staticmethod
    def calculate_skew_angle(contour: np.ndarray) -> float:
        """
        Calculate the skew angle of the document
        """
        # Fit a rotated rectangle to the contour
        rect = cv2.minAreaRect(contour)
        angle = rect[2]

        # Adjust angle if needed (cv2 returns angle between -90 and 0)
        if angle < -45:
            angle = 90 + angle

        return angle

    @staticmethod
    def correct_skew(image: np.ndarray, angle: float) -> np.ndarray:
        """
        Correct image skew by rotating by given angle
        """
        # Get image dimensions
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)

        # Create rotation matrix
        M = cv2.getRotationMatrix2D(center, angle, 1.0)

        # Rotate image
        corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return corrected

    @staticmethod
    def four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """
        Perspective transform using four corner points
        """
        # Order the points
        rect = DocScanner.order_points(pts)
        (tl, tr, br, bl) = rect

        # Compute width and height of the new image
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        # Construct destination points
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype="float32")

        # Compute perspective transform matrix
        M = cv2.getPerspectiveTransform(rect, dst)

        # Apply perspective transformation
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        return warped

    @classmethod
    def scan_document(cls, image_bytes: bytes) -> Dict[str, Any]:
        """
        Scan and correct a document image
        Returns dictionary with corrected image, skew angle, and processing info
        """
        try:
            # Load image from bytes
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if image is None:
                raise ValueError("Could not load image from bytes")

            # Preprocess image
            edged = cls.preprocess_image(image)

            # Find document contour
            contour = cls.find_document_contour(edged)

            result = {
                "success": False,
                "original_image": image,
                "corrected_image": image,  # fallback to original
                "skew_angle": 0.0,
                "contour_found": contour is not None
            }

            if contour is not None:
                # Calculate skew angle
                skew_angle = cls.calculate_skew_angle(contour.reshape(4, 2))

                # Correct skew
                corrected = cls.correct_skew(image, skew_angle)

                # Try perspective correction
                warped = cls.four_point_transform(image, contour.reshape(4, 2))

                result.update({
                    "success": True,
                    "corrected_image": warped,  # Use perspective corrected image
                    "skew_angle": skew_angle,
                    "deskewed_image": corrected
                })
            else:
                # Try simple deskewing based on text lines
                skew_angle = cls.detect_skew_angle_hough(image)
                if skew_angle != 0:
                    corrected = cls.correct_skew(image, skew_angle)
                    result.update({
                        "success": True,
                        "corrected_image": corrected,
                        "skew_angle": skew_angle,
                        "detected_by": "hough_lines"
                    })

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "original_image": None,
                "corrected_image": None,
                "skew_angle": 0.0,
                "contour_found": False
            }

    @classmethod
    def detect_skew_angle_hough(cls, image: np.ndarray) -> float:
        """
        Detect skew angle using Hough line transform as fallback
        """
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Apply threshold to get binary image
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Detect lines using Hough transform
            lines = cv2.HoughLinesP(thresh, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

            if lines is None:
                return 0.0

            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                # Normalize angle to [-90, 90]
                if angle > 90:
                    angle -= 180
                elif angle < -90:
                    angle += 180
                angles.append(angle)

            if not angles:
                return 0.0

            # Take median angle
            median_angle = np.median(angles)

            # Only correct if angle is significant (> 5 degrees)
            if abs(median_angle) > 5:
                return median_angle

            return 0.0

        except Exception:
            return 0.0