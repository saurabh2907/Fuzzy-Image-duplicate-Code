import os
from PIL import Image
import imagehash
import matplotlib.pyplot as plt
import fitz  # PyMuPDF

def calculate_phash(image_path):
    image = Image.open(image_path)
    phash = imagehash.phash(image)
    return phash

def find_duplicates(folder_path):
    image_hashes = {}
    duplicate_images = {}
    total_images = 0

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            total_images += 1
            phash = calculate_phash(file_path)

            # Compare perceptual hashes using Hamming distance
            matched_hash = None
            for existing_hash, existing_filename in image_hashes.items():
                if phash - existing_hash < 5:  # Adjust the threshold based on your needs
                    matched_hash = existing_hash
                    break

            if matched_hash is not None:
                duplicate_images[filename] = (image_hashes[matched_hash], filename)  # Store filenames as strings
            else:
                image_hashes[phash] = filename  # Store filename as string

        elif filename.lower().endswith('.pdf'):
            total_images += 1
            pdf_document = fitz.open(file_path)
            for page_number in range(pdf_document.page_count):
                page = pdf_document.load_page(page_number)
                image = page.get_pixmap()

                image_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}_page_{page_number+1}.png"
                image_path = os.path.join(folder_path, image_filename)
                image.save(image_path)

                phash = calculate_phash(image_path)

                # Compare perceptual hashes using Hamming distance
                matched_hash = None
                for existing_hash, existing_filename in image_hashes.items():
                    if phash - existing_hash < 3:  # Adjust the threshold based on your needs
                        matched_hash = existing_hash
                        break

                if matched_hash is not None:
                    duplicate_images[image_filename] = (image_hashes[matched_hash], image_filename)  # Store filenames as strings
                else:
                    image_hashes[phash] = image_filename  # Store filename as string

            pdf_document.close()

    return duplicate_images, image_hashes, total_images

if __name__ == "__main__":
    folder_path = r"\\mdibkstorage\DataAnalytics&Infographics\PRojects\Saurabh\OtherTestPDFs"
    duplicates, image_hashes, total_images = find_duplicates(folder_path)

    print(f"Total images in the folder: {total_images}")

    if not duplicates:
        print("No duplicate images found.")
    else:
        print("Duplicate images found:")
        for image_filename, (original_image_filename, duplicate_image_filename) in duplicates.items():
            print(f"{image_filename} is a duplicate of {original_image_filename}.")

            # Display the original and duplicate images side by side
            plt.figure()
            plt.subplot(1, 2, 1)
            plt.imshow(Image.open(os.path.join(folder_path, original_image_filename)))
            plt.title("Original")
            plt.axis("off")

            plt.subplot(1, 2, 2)
            plt.imshow(Image.open(os.path.join(folder_path, duplicate_image_filename)))
            plt.title("Duplicate")
            plt.axis("off")

            plt.show()
