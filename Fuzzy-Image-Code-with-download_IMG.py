import os
import numpy as np
from skimage import io, color
import skfuzzy as fuzz
import matplotlib.pyplot as plt
from PIL import Image


def get_image_files(folder_path):
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    image_files = [f for f in os.listdir(folder_path) if os.path.splitext(f)[1].lower() in image_extensions]
    return image_files


def compute_image_features(folder_path):
    image_files = get_image_files(folder_path)
    image_features = []
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        img = io.imread(image_path)
        gray_img = color.rgb2gray(img)
        # Extract a simple feature (mean intensity value) for demonstration purposes
        feature = np.mean(gray_img)
        image_features.append(feature)
    return np.array(image_features)


def fuzzy_similarity(features):
    # Define the fuzzy sets
    similarity = np.arange(0, 1.01, 0.01)

    # Define the membership functions for each set
    similarity_very_similar = fuzz.trapmf(similarity, [0, 0, 0.2, 0.5])
    similarity_somewhat_similar = fuzz.trimf(similarity, [0.2, 0.5, 0.8])
    similarity_less_similar = fuzz.trapmf(similarity, [0.5, 0.8, 1, 1])

    # Calculate membership degrees for each image feature
    degrees_very_similar = fuzz.interp_membership(similarity, similarity_very_similar, features)
    degrees_somewhat_similar = fuzz.interp_membership(similarity, similarity_somewhat_similar, features)
    degrees_less_similar = fuzz.interp_membership(similarity, similarity_less_similar, features)

    # Calculate the overall similarity scores
    similarity_score_very_similar = np.max(degrees_very_similar)
    similarity_score_somewhat_similar = np.max(degrees_somewhat_similar)
    similarity_score_less_similar = np.max(degrees_less_similar)

    return similarity_score_very_similar, similarity_score_somewhat_similar, similarity_score_less_similar



def download_duplicate_images(folder_path, duplicate_images):
    output_folder = os.path.join(folder_path, "duplicate_images")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for image_file in duplicate_images:
        image_path = os.path.join(folder_path, image_file)
        output_path = os.path.join(output_folder, image_file)

        # Copy the duplicate image to the output folder
        with open(image_path, 'rb') as image_file:
            with open(output_path, 'wb') as output_file:
                output_file.write(image_file.read())

    print(f"Duplicate images downloaded to: {output_folder}")


if __name__ == "__main__":
    folder_path = r"\\mdibkstorage\DataAnalytics&Infographics\PRojects\Saurabh\TEST_FILES"
    image_features = compute_image_features(folder_path)
    similarity_score_very_similar, similarity_score_somewhat_similar, similarity_score_less_similar = fuzzy_similarity(
        image_features
    )

    # Thresholds for similarity levels
    threshold_very_similar = 0.5
    threshold_somewhat_similar = 0.8

    # Find duplicate and similar images
    duplicate_images = [
        f for f, sim in zip(get_image_files(folder_path), image_features) if sim >= threshold_very_similar
    ]
    similar_images = [
        f for f, sim in zip(get_image_files(folder_path), image_features)
        if threshold_somewhat_similar <= sim < threshold_very_similar
    ]

    print("Duplicate images:")
    print(duplicate_images)
    print(len(duplicate_images))
    print("Similar images:")
    print(similar_images)

    # Display the duplicate images using Matplotlib
    num_cols = 4  # Number of columns in the grid
    num_rows = int(np.ceil(len(duplicate_images) / num_cols))  # Calculate the number of rows needed
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(12, 8))  # Create the subplot grid

    for i, image_file in enumerate(duplicate_images):
        row_idx = i // num_cols  # Calculate the row index for the current image
        col_idx = i % num_cols  # Calculate the column index for the current image
        image_path = os.path.join(folder_path, image_file)
        img = io.imread(image_path)
        axs[row_idx, col_idx].imshow(img)
        axs[row_idx, col_idx].axis('off')  # Turn off axis labels

    # Hide any empty subplots
    for i in range(len(duplicate_images), num_cols * num_rows):
        row_idx = i // num_cols
        col_idx = i % num_cols
        axs[row_idx, col_idx].axis('off')

    plt.tight_layout()
    plt.show()

    # Download the duplicate images
    download_duplicate_images(folder_path, duplicate_images)
