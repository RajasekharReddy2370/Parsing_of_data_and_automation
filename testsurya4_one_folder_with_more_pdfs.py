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

# Folder containing the PDFs
pdf_folder_path = "/home/rajasekharreddy/Desktop/teachers/Medak_Nizamabad_Adilabad_karimnagar"
output_dir = "/home/rajasekharreddy/Desktop/teachers/processed_images"
excel_output_dir = "/home/rajasekharreddy/Desktop/teachers/Teachers_excel"

# Create necessary directories if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(excel_output_dir, exist_ok=True)

# Load OCR models and processors
langs = ["en"]
det_processor, det_model = load_det_processor(), load_det_model()
rec_model, rec_processor = load_rec_model(), load_rec_processor()

# Iterate over each PDF in the folder
for pdf_file in os.listdir(pdf_folder_path):
    if pdf_file.endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder_path, pdf_file)
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

        # Convert PDF pages to images
        images = pdf2image.convert_from_path(pdf_path)
        final_text = ""  # To store the final text from all images
        image_texts = []  # To store the text from each image individually

        # Iterate over each image in the PDF
        for index, image in enumerate(images):
            # Convert image to black and white (binarization)
            bw_image = image.convert("L").point(lambda x: 0 if x < 128 else 255, '1')

            # Save the processed image as PNG
            png_image_path = os.path.join(output_dir, f"{pdf_name}_page_{index + 1}.png")
            bw_image.save(png_image_path, format="PNG")

            # Load the PNG image back for OCR processing
            png_image = Image.open(png_image_path)

            # Run OCR on the current black and white image
            predictions = run_ocr([png_image], [langs], det_model, det_processor, rec_model, rec_processor)
            target_text = ""  # To store the text for the current image

            # Bounding box values (example, adjust as needed)
            highest = [165.0, 1225.0, 423.0, 1250.0]
            lowest = [139.0, 286.0, 269.0, 310.0]

            # Extract text from the relevant bounding box area
            for prediction in predictions:
                for text_line in prediction.text_lines:
                    if (lowest[0] <= text_line.bbox[0] <= highest[0] and
                            lowest[1] <= text_line.bbox[1] <= highest[1] and
                            lowest[2] <= text_line.bbox[2] <= highest[2] and
                            lowest[3] <= text_line.bbox[3] <= highest[3]):
                        target_text += text_line.text + "\n"

            # Add the current image's text to the list and final text
            image_texts.append(target_text.strip())
            final_text += target_text.strip() + "\n\n"

        # Split final text into a list of lines (assuming each line contains a teacher's name)
        teacher_names = final_text.splitlines()

        # Create a DataFrame from the list of teacher names
        df = pd.DataFrame(teacher_names, columns=["Teachernames"])

        # Filter rows to contain only valid teacher names (alphabetic characters and spaces)
        df_filtered = df[df['Teachernames'].str.contains(r'^[a-zA-Z\s]+$', regex=True)]

        # Save the filtered DataFrame to an Excel file
        file_path = os.path.join(excel_output_dir, f"{pdf_name}_teachers.xlsx")
        df_filtered.to_excel(file_path, index=False)

        print(f"Processed {pdf_file} and saved to {file_path}")

# Time taken for processing
endtime = time.time()
total_time = endtime - starttime
print(f"Total time taken: {total_time} seconds")
