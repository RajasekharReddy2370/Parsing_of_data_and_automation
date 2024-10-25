from PIL import Image
from surya.ocr import run_ocr
from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor
import time
starttime = time.time()
# Load the image
image = Image.open("/home/rajasekharreddy/Desktop/teachers/Screenshot from 2024-10-22 16-58-31.png")

# Run OCR on the entire image
langs = ["en"]  # Replace with your languages - optional but recommended
det_processor, det_model = load_det_processor(), load_det_model()
rec_model, rec_processor = load_rec_model(), load_rec_processor()
predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)

# target_bbox = [55.0, 132.0, 147.0, 144.0]
highest = [60.0, 595.0, 178.0, 608.0]
lowest = [50.0, 127.0, 138.0, 139.0]
target_text = ""

for prediction in predictions:
    for text_line in prediction.text_lines:
        if (lowest[0] <= text_line.bbox[0] <= highest[0] and
            lowest[1] <= text_line.bbox[1] <= highest[1] and
            lowest[2] <= text_line.bbox[2] <= highest[2] and
            lowest[3] <= text_line.bbox[3] <= highest[3]):
            target_text += text_line.text + "\n"
            # break  # Remove this if you want all text lines

print(target_text.strip())
endtime = time.time()
time = endtime-starttime
print(time)