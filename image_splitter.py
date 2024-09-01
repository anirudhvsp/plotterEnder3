import cv2
import numpy as np
from colorthief import ColorThief
from PIL import Image
import matplotlib.pyplot as plt
import argparse

def generate_outline(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply edge detection (Canny)
    edges = cv2.Canny(gray, 100, 200)
    return edges

def fill_black_regions(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Threshold to fill black regions
    _, filled = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    return filled

def generate_halftone(image, color, threshold=100):
    # Create a halftone pattern based on a specific color
    mask = cv2.inRange(image, np.array(color) - threshold, np.array(color) + threshold)
    halftone = np.zeros_like(image)
    dot_size = 20

    # Generate halftone dots within the masked regions
    for y in range(0, mask.shape[0], dot_size):
        for x in range(0, mask.shape[1], dot_size):
            if mask[y, x] > 0:
                cv2.circle(halftone, (x, y), dot_size // 2, color[::-1], -1)  # Reverse RGB to BGR for OpenCV

    return halftone

def visualize_output(layers):
    # Visualize all layers side-by-side
    fig, axs = plt.subplots(1, len(layers), figsize=(15, 5))
    for i, (title, layer) in enumerate(layers.items()):
        if len(layer.shape) == 2:  # Grayscale
            axs[i].imshow(layer, cmap='gray')
        else:  # Color
            axs[i].imshow(cv2.cvtColor(layer, cv2.COLOR_BGR2RGB))
        axs[i].set_title(title)
        axs[i].axis('off')
    plt.show()

def save_layer(layer, filename):
    # Save the layer as an image file
    if len(layer.shape) == 2:  # Grayscale
        cv2.imwrite(filename, layer)
    else:  # Color
        cv2.imwrite(filename, cv2.cvtColor(layer, cv2.COLOR_BGR2RGB))

def main(image_path, n_colors):
    # Load image
    image = cv2.imread(image_path)

    # Generate layers
    outline_layer = generate_outline(image)
    filled_black_layer = fill_black_regions(image)

    # Detect dominant colors
    color_thief = ColorThief(image_path)
    dominant_colors = [color_thief.get_palette(color_count=n_colors+1)[i] for i in range(n_colors)]

    # Generate halftone layers for each color
    halftone_layers = [generate_halftone(image, color) for color in dominant_colors]

    # Combine results into layers dictionary for visualization and saving
    layers = {
        "Gen_Outline": outline_layer,
        "Gen_Filled Black": filled_black_layer
    }

    for i, halftone_layer in enumerate(halftone_layers):
        layers[f"Gen_Halftone{i+1}"] = halftone_layer

    # Visualize the results
    visualize_output(layers)

    # Save the layers
    for title, layer in layers.items():
        filename = f"{title.replace(' ', '_')}.png"
        save_layer(layer, filename)
        print(f"Saved {title} as {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image Splitter")
    parser.add_argument("image_path", help="Path to the input image file")
    parser.add_argument("--n_colors", type=int, default=5, help="Number of dominant colors to extract (default: 5)")
    args = parser.parse_args()

    main(args.image_path, args.n_colors)
