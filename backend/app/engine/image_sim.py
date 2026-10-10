import cv2
from skimage.metrics import structural_similarity as ssim

def calculate_logo_similarity(official_img_path: str, detected_img_path: str) -> float:
    """Compares two images and returns a similarity percentage (0-100)."""
    try:
        # Load images in grayscale
        img1 = cv2.imread(official_img_path, cv2.IMREAD_GRAYSCALE)
        img2 = cv2.imread(detected_img_path, cv2.IMREAD_GRAYSCALE)
        
        # Resize to standard dimensions for accurate comparison
        img1 = cv2.resize(img1, (256, 256))
        img2 = cv2.resize(img2, (256, 256))
        
        # Calculate SSIM (Structural Similarity Index)
        score, _ = ssim(img1, img2, full=True)
        
        # Convert SSIM score (-1 to 1) to a 0-100 percentage
        match_percentage = max(0, (score * 100))
        return round(match_percentage, 2)
    except Exception as e:
        return 0.0 # Return 0 if images are missing or broken