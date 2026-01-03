import os
from typing import Set, Tuple, Union, Optional

import cv2
import numpy as np
from imutils.perspective import four_point_transform
from PIL import Image

# Accept these image formats (case-insensitive)
SUPPORTED_IMAGE_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg"}


# =====================================================
# IMAGE ENHANCEMENT
# =====================================================
def image_processing(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    scan = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        15,
        10
    )
    return scan


# =====================================================
# DOCUMENT DETECTION (LARGEST QUAD)
# =====================================================
def scan_detection(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(2.0, (8, 8))
    gray = clahe.apply(gray)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)

    grad = cv2.morphologyEx(
        blur,
        cv2.MORPH_GRADIENT,
        cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    )

    _, thresh = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh = cv2.morphologyEx(
        thresh, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), iterations=3
    )

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise RuntimeError("No contours found")

    h, w = gray.shape
    img_area = h * w

    candidates = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 0.10 * img_area:
            continue

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            candidates.append(approx.reshape(4, 2))

    if candidates:
        # choose the biggest quad (by contour area)
        # cv2.contourArea expects a contour-like shape, so reshape back
        def quad_area(pts: np.ndarray) -> float:
            return cv2.contourArea(pts.reshape(-1, 1, 2).astype(np.float32))

        return max(candidates, key=quad_area)

    # fallback: minimum area rectangle
    largest = max(contours, key=cv2.contourArea)
    hull = cv2.convexHull(largest)
    rect = cv2.minAreaRect(hull)
    box = cv2.boxPoints(rect)
    return np.array(box, dtype="float32")


# =====================================================
# ROTATION / DESKEW
# =====================================================
def rotate_bound(image: np.ndarray, angle: float) -> np.ndarray:
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    cos = abs(M[0, 0])
    sin = abs(M[0, 1])
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    M[0, 2] += (nW / 2) - center[0]
    M[1, 2] += (nH / 2) - center[1]
    return cv2.warpAffine(
        image,
        M,
        (nW, nH),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )


def detect_skew_angle(image: np.ndarray, max_angle: float = 15) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
    if lines is None:
        return 0.0

    angles = []
    for rho, theta in lines[:, 0]:
        ang = (theta - np.pi / 2) * (180 / np.pi)
        if -max_angle <= ang <= max_angle:
            angles.append(ang)

    return float(np.median(angles)) if angles else 0.0


def correct_rotation(image: np.ndarray) -> np.ndarray:
    angle = detect_skew_angle(image)
    return rotate_bound(image, angle) if abs(angle) >= 0.5 else image


# =====================================================
# PUBLIC API
# =====================================================
def scan_document(
    image_path: str,
    output_pdf: str = "out.pdf",
    resolution: int = 300
) -> str:
    """
    Full pipeline:
    1) detect document contour (quad)
    2) perspective correction
    3) deskew rotation correction
    4) image enhancement
    5) save as PDF

    Supports: PNG / JPG / JPEG
    Returns: output_pdf path
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    ext = os.path.splitext(image_path)[1].lower()
    if ext not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_IMAGE_EXTENSIONS))}"
        )

    image = cv2.imread(image_path)
    if image is None:
        raise RuntimeError(f"Failed to load image: {image_path}")

    pts = scan_detection(image)
    warped = four_point_transform(image, pts)
    warped = correct_rotation(warped)
    scanned = image_processing(warped)

    Image.fromarray(scanned).save(output_pdf, "PDF", resolution=resolution)
    return output_pdf