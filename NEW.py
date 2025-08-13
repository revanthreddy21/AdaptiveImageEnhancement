import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2

# Step 1: Load and Convert Image to Grayscale
def load_image(image_path):
    image = Image.open(image_path).convert("L")  # Convert to grayscale
    return np.array(image)

# Step 2: Compute Histogram
def compute_histogram(image_array):
    histogram, _ = np.histogram(image_array.flatten(), bins=256, range=(0, 255))
    return histogram

# Step 3: Compute PDF
def compute_pdf(histogram):
    total_pixels = np.sum(histogram)
    pdf = histogram / total_pixels  # Normalized histogram
    return pdf

# Step 4: Compute Mean and Average PDF
def compute_mean_and_average_pdf(pdf):
    mean_pdf = np.mean(pdf)
    average_pdf = np.sum(pdf) / len(pdf)
    return mean_pdf, average_pdf

# Step 5: Adaptive PDF
def compute_adaptive_pdf(pdf, mean_pdf, average_pdf):
    adaptive_pdf = np.where(pdf < average_pdf, average_pdf, pdf / mean_pdf)
    return adaptive_pdf

# Step 6: Apply Modified PDF to Enhance Image
def modify_image_with_pdf(image_array, adaptive_pdf):
    cdf = np.cumsum(adaptive_pdf)  # Compute CDF from Adaptive PDF
    cdf_normalized = np.floor(cdf * 255 / cdf[-1]).astype(np.uint8)  # Normalize to [0, 255]
    enhanced_image = cdf_normalized[image_array]  # Map original pixels to new values
    return enhanced_image

# Step 7: Compute CDF
def compute_cdf(histogram):
    cdf = np.cumsum(histogram)  # Cumulative sum of histogram
    cdf_normalized = cdf / cdf[-1]  # Normalize CDF to range [0, 1]
    return cdf_normalized

# Step 8: Compute Mean and Average CDF
def compute_mean_and_average_cdf(cdf):
    mean_cdf = np.mean(cdf)
    average_cdf = np.sum(cdf) / len(cdf)
    return mean_cdf, average_cdf

# Step 9: Adaptive CDF
def compute_adaptive_cdf(cdf, mean_cdf, average_cdf):
    # Apply a power-law transformation to enhance intensity differences
    gamma = 2  # Adjust this value for more or less enhancement
    enhanced_cdf = np.power(cdf, gamma)

    # Normalize enhanced CDF to range [0, 1]
    enhanced_cdf = (enhanced_cdf - np.min(enhanced_cdf)) / (np.max(enhanced_cdf) - np.min(enhanced_cdf))

    # Combine with original adaptive adjustment logic
    adaptive_cdf = np.where(enhanced_cdf > average_cdf, enhanced_cdf, enhanced_cdf - average_cdf + mean_cdf)
    return adaptive_cdf

# Step 10: Apply Modified CDF to Enhance Image
def modify_image_with_cdf(image_array, adaptive_cdf):
    min_val = np.min(adaptive_cdf)
    max_val = np.max(adaptive_cdf)

    # Safeguard normalization
    if max_val == min_val:
        cdf_normalized = np.zeros_like(adaptive_cdf)
    else:
        cdf_normalized = (adaptive_cdf - min_val) / (max_val - min_val)

    cdf_normalized = np.floor(cdf_normalized * 255).astype(np.uint8)  # Map to [0, 255]
    enhanced_image = cdf_normalized[image_array]
    return enhanced_image

# Step 11: Contrast Adjustment
def contrast_adjustment(image_array, alpha=2.5, beta=1.5):
    # Normalize image to [0, 1]
    normalized_image = image_array / 255.0

    # Apply sigmoidal contrast enhancement
    adjusted_image = 1 / (1 + np.exp(-alpha * (normalized_image - beta)))

    # Rescale back to the range [0, 255]
    adjusted_image = (adjusted_image * 255).astype('uint8')

    return adjusted_image


# Step 12: Gamma Correction
def gamma_correction(image_array, gamma=2.2):
    if not isinstance(image_array, np.ndarray):
        raise ValueError("Input must be a numpy array.")

    if image_array.ndim != 2:  # Ensure image is grayscale (2D)
        raise ValueError("Only grayscale images are supported.")

    # Normalize the pixel values to the range [0, 1]
    normalized_image = image_array / 255.0

    # Apply gamma correction
    corrected_image = np.power(normalized_image, gamma)

    # Rescale back to [0, 255] and clip values to ensure they're within valid range
    corrected_image = (corrected_image * 255).clip(0, 255).astype('uint8')

    return corrected_image

# Step 13: Multi-Scale Enhancement

def multi_scale_enhancement(image_array):
    # Convert the image to grayscale if it's not already
    if len(image_array.shape) == 3:
        gray_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image_array

    # Initialize CLAHE with clip limit and tile grid size
    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(10, 10))

    # Apply CLAHE to the grayscale image
    enhanced_image = clahe.apply(gray_image)

    # If the original image was in color, merge the enhanced grayscale with original channels
    if len(image_array.shape) == 3:
        enhanced_image = cv2.merge([enhanced_image] * 3)  # Merge into 3 channels (RGB)

    return np.clip(enhanced_image, 0, 255).astype(np.uint8)

# Step 15: Display Results
def display_results(original_image, pdf_enhanced_image, cdf_enhanced_image, contrast_image, gamma_image, multi_scale_image):
    plt.figure(figsize=(20, 10))

    # Original Image
    plt.subplot(2, 4, 1)
    plt.title("Original Image")
    plt.imshow(original_image, cmap="gray")
    plt.axis("off")

    # PDF Enhanced Image
    plt.subplot(2, 4, 2)
    plt.title("PDF Enhanced Image")
    plt.imshow(pdf_enhanced_image, cmap="gray")
    plt.axis("off")

    # CDF Enhanced Image
    plt.subplot(2, 4, 3)
    plt.title("CDF Enhanced Image")
    plt.imshow(cdf_enhanced_image, cmap="gray")
    plt.axis("off")

    # Contrast Enhanced Image
    plt.subplot(2, 4, 4)
    plt.title("Contrast Enhanced Image")
    plt.imshow(contrast_image, cmap="gray")
    plt.axis("off")

    # Gamma Corrected Image
    plt.subplot(2, 4, 5)
    plt.title("Gamma Corrected Image")
    plt.imshow(gamma_image, cmap="gray")
    plt.axis("off")

    # Multi-Scale Enhanced Image
    plt.subplot(2, 4, 6)
    plt.title("Multi-Scale Enhanced Image")
    plt.imshow(multi_scale_image, cmap="gray")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

# Main Workflow
def process_image(image_path, pdf_output_path, cdf_output_path, contrast_output_path, gamma_output_path, multi_scale_output_path):
    # Load image
    image_array = load_image(image_path)

    # PDF Enhancement
    histogram = compute_histogram(image_array)
    pdf = compute_pdf(histogram)
    mean_pdf, average_pdf = compute_mean_and_average_pdf(pdf)
    adaptive_pdf = compute_adaptive_pdf(pdf, mean_pdf, average_pdf)
    pdf_enhanced_image = modify_image_with_pdf(image_array, adaptive_pdf)
    Image.fromarray(pdf_enhanced_image).save(pdf_output_path)

    # CDF Enhancement
    cdf = compute_cdf(histogram)
    mean_cdf, average_cdf = compute_mean_and_average_cdf(cdf)
    adaptive_cdf = compute_adaptive_cdf(cdf, mean_cdf, average_cdf)
    cdf_enhanced_image = modify_image_with_cdf(image_array, adaptive_cdf)
    Image.fromarray(cdf_enhanced_image).save(cdf_output_path)

    # Contrast Adjustment
    contrast_image = contrast_adjustment(image_array)
    Image.fromarray(contrast_image).save(contrast_output_path)

    # Gamma Correction
    gamma_image = gamma_correction(image_array)
    Image.fromarray(gamma_image).save(gamma_output_path)

    # Multi-Scale Enhancement
    multi_scale_image = multi_scale_enhancement(image_array)
    Image.fromarray(multi_scale_image).save(multi_scale_output_path)

    # Display Results
    display_results(image_array, pdf_enhanced_image, cdf_enhanced_image, contrast_image, gamma_image, multi_scale_image)

    print(f"PDF Enhanced Image saved to: {pdf_output_path}")
    print(f"CDF Enhanced Image saved to: {cdf_output_path}")
    print(f"Contrast Enhanced Image saved to: {contrast_output_path}")
    print(f"Gamma Corrected Image saved to: {gamma_output_path}")
    print(f"Multi-Scale Enhanced Image saved to: {multi_scale_output_path}")

# Example Usage
if __name__ == "__main__":
    input_image_path = r"C:/Users/revan/OneDrive/Pictures/imgeh2.jpg"  # Replace with your image path
    pdf_output_path = r"C:/Users/revan/OneDrive/Pictures/pdfB_enhanced_image.jpg"  # Path for PDF enhanced image
    cdf_output_path = r"C:/Users/revan/OneDrive/Pictures/cdfB_enhanced_image.jpg"  # Path for CDF enhanced image
    contrast_output_path = r"C:/Users/revan/OneDrive/Pictures/contrast_enhanced_image.jpg"  # Path for Contrast enhanced image
    gamma_output_path = r"C:/Users/revan/OneDrive/Pictures/gamma_corrected_image.jpg"  # Path for Gamma corrected image
    multi_scale_output_path = r"C:/Users/revan/OneDrive/Pictures/multi_scale_output_path.jpg"
    process_image(input_image_path, pdf_output_path, cdf_output_path, contrast_output_path, gamma_output_path,
                  multi_scale_output_path)