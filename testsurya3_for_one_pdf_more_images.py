from PIL import Image
from surya.ocr import run_ocr
from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor
import time
import pdf2image
import os
import pandas as pd
import re
starttime = time.time()

# Convert PDF pages to images
pdf_path = "/home/rajashekar/Desktop/teachers_data/t1.pdf"
pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
images = pdf2image.convert_from_path(pdf_path)

# Load OCR models and processors
langs = ["en"]
det_processor, det_model = load_det_processor(), load_det_model()
rec_model, rec_processor = load_rec_model(), load_rec_processor()

final_text = ""  # To store the final text from all images
image_texts = []  # To store the text from each image individually

# Create a directory to store PNG images
output_dir = "/home/rajashekar/Desktop/teachers_data/teachers_images"
os.makedirs(output_dir, exist_ok=True)

# Iterate over each image and extract text
for index, image in enumerate(images):
    # Convert image to black and white, then greyscale
    bw_image = image.convert("L")  # Converts to greyscale
    bw_image = bw_image.point(lambda x: 0 if x < 128 else 255, '1')  # Converts to black and white (binarization)

    # Save the processed image as PNG
    png_image_path = os.path.join(output_dir, f"{pdf_name}_page_{index + 1}.png")
    bw_image.save(png_image_path, format="PNG")

    # Load the PNG image back for OCR processing
    png_image = Image.open(png_image_path)

    # Run OCR on the current black and white image
    predictions = run_ocr([png_image], [langs], det_model, det_processor, rec_model, rec_processor)
    # for prediction in predictions:
    #     for text_line in prediction.text_lines:
    #         print("Text:", text_line.text)
    #         print("Confidence:", text_line.confidence)
    #         print("Bounding Box:", text_line.bbox)
    #         print("Polygon:", text_line.polygon)
    #         print("------------------------")
    target_text = ""  # To store the text for the current image
    highest = [165.0,1225.0,423.0,1250.0]
    lowest = [139.0,286.0,269.0,310.0]

    for prediction in predictions:
        for text_line in prediction.text_lines:
            if (lowest[0] <= text_line.bbox[0] <= highest[0] and
                    lowest[1] <= text_line.bbox[1] <= highest[1] and
                    lowest[2] <= text_line.bbox[2] <= highest[2] and
                    lowest[3] <= text_line.bbox[3] <= highest[3]):
                target_text += text_line.text + "\n"

    # Print the text for the current image
    print(f"Text for Image {index + 1}:\n{target_text.strip()}\n")

    # Add the current image's text to the list and final text
    image_texts.append(target_text.strip())
    final_text += target_text.strip() + "\n\n"

# Print the final text after iterating through all images
print("Final Text of PDF:\n")
print(final_text.strip())

# Split final text into a list of lines (assuming each line contains a teacher's name)
teacher_names = final_text.splitlines()

# Create a DataFrame from the list of teacher names
df = pd.DataFrame(teacher_names, columns=["Teachernames"])

# Filter rows to contain only valid teacher names (alphabetic characters and spaces)
df_filtered = df[df['Teachernames'].str.contains(r'^[a-zA-Z\s]+$', regex=True)]

# Define the file path and save the filtered DataFrame to an Excel file
file_path = f"/home/rajashekar/Desktop/teachers_data/Teachers_Excel/{pdf_name}_teachers.xlsx"
df_filtered.to_excel(file_path, index=False)

# Time taken for processing
endtime = time.time()
total_time = endtime - starttime
print(f"Total time taken: {total_time} seconds")


# [144.0, 309.0, 329.0, 334.0]
# [144.0, 613.0, 307.0, 637.0]
# [144.0, 914.0, 346.0, 938.0]
# [144.0, 946.0, 383.0, 970.0]
# [144.0, 1215.0, 346.0, 1241.0]
#[150.0, 286.0, 387.0, 311.0]
#
# [149.0,1215.0,383.0,1241.0]
# [139.0,309.0,307.0,334.0]