from PIL import Image
from surya.ocr import run_ocr
from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor
image = Image.open("/home/rajasekharreddy/Desktop/teachers/processed_images/page_3.png")
langs = ["en"] # Replace with your languages - optional but recommended
det_processor, det_model = load_det_processor(), load_det_model()
rec_model, rec_processor = load_rec_model(), load_rec_processor()
predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)
# print(predictions)
for prediction in predictions:
    for text_line in prediction.text_lines:
        print("Text:", text_line.text)
        print("Confidence:", text_line.confidence)
        print("Bounding Box:", text_line.bbox)
        print("Polygon:", text_line.polygon)
        print("------------------------")

##### in surya library in settings.py file change None to "cpu"