import os
import time
from PIL import Image
import torch
os.environ['USE_TORCH'] = '1'
from doctr.io import DocumentFile
from doctr.models import detection_predictor
from doctr.utils.geometry import detach_scores
from doctr.models.builder import DocumentBuilder
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
import requests
import numpy as np
import cv2
from io import BytesIO
import json
from parsedata import UnifiedDataProcessor
#from stringTojson import ExamDataProcessor
from stringToJSONClass import ExamDataProcessor

def get_image_dimensions(image_url):
    """
    Get the dimensions of an image given its URL.
    
    :param image_url: URL of the image.
    :return: A tuple (width, height) of the image.
    """
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # Check if the request was successful
        img = Image.open(BytesIO(response.content))  # Open the image from the byte content
        return img.size  # Returns (width, height)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image from URL {image_url}: {e}")
        return None
    except Exception as e:
        print(f"Error processing image {image_url}: {e}")
        return None

class OCRPipeline:
    def __init__(self, trocr_model_dir="epoch_2_outliers_removed"):
        # Initialize OCR and TrOCR models
        self.det_predictor = self._initialize_ocr_model()
        self.processor, self.model_trocr = self._initialize_trocr_model(trocr_model_dir)
        self.results = []  # Store structured results

    def _initialize_ocr_model(self):
        print("Initializing OCR Model...")
        start_time = time.time()
        det_predictor = detection_predictor(
            arch="fast_base",
            pretrained=True,
            assume_straight_pages=True,
            symmetric_pad=True,
            preserve_aspect_ratio=True
        ).cuda().half() if torch.cuda.is_available() else detection_predictor(
            arch="fast_base",
            pretrained=True,
            assume_straight_pages=True,
            symmetric_pad=True,
            preserve_aspect_ratio=True
        )
        det_predictor.model.postprocessor.bin_thresh = 0.1
        det_predictor.model.postprocessor.box_thresh = 0.1
        print(f"OCR Model initialized in {time.time() - start_time:.2f} seconds")
        return det_predictor
    
    def _initialize_trocr_model(self, model_directory):
        print("Initializing TrOCR Model...")
        start_time = time.time()
        processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-handwritten")
        model_trocr = VisionEncoderDecoderModel.from_pretrained(model_directory)
        model_trocr = model_trocr.to('cuda') if torch.cuda.is_available() else model_trocr
        print(f"TrOCR Model initialized in {time.time() - start_time:.2f} seconds")
        return processor, model_trocr

    def _process_image(self, image_url):
        """
        Process the entire image using OCR and TrOCR models.
        :param image_url: URL of the image to be processed.
        :return: The OCR results for the image.
        """
        print(f"Processing image from URL: {image_url}")
        return self._process_single_image(image_url, section_type="Original_Image")

    def process_images(self, image_data_list):
        """
        Process multiple images from a list of data entries.
        
        :param image_data_list: A list of dictionaries, each containing image data to process.
        :return: A list of results from OCR processing.
        """
        print(f"Processing {len(image_data_list)} entries...")
        print(image_data_list)
        for image_data in image_data_list:
            # Ensure the entry contains the 'data' key
            if "data" not in image_data:
                print("Skipping entry: 'data' key not found.")
                continue
            print(image_data)
            uid = image_data["uid"]
            for image_name, sections in image_data["data"].items():
                print(f"Processing image: {image_name}")
                original_url = sections["original_image"]
                
                
                # OCR on Original Image
                original_text = self._process_image(original_url)

                # Store results
                self.results.append({
                    "image_path": original_url,
                    "generated_uid": uid,
                    "full_information": original_text
                })
        
        return self.results


    def _process_single_image(self, image_url, section_type="default"):
        """
        Process a single image for text detection and recognition.
        :param image_url: The URL of the image to process.
        :param section_type: The type of section (for logging purposes).
        :return: OCR results for the image.
        """
        print(f"Processing {image_url}...")
        start_time = time.time()

        # Download and process the image
        image_file = requests.get(image_url).content
        image_data = cv2.imdecode(np.frombuffer(image_file, np.uint8), cv2.IMREAD_COLOR)
        single_img_doc = DocumentFile.from_images([image_file])
        results = self.det_predictor(single_img_doc)
        builder = DocumentBuilder(resolve_lines=True)

        documents, placeholder = [], []
        for doc, res in zip(single_img_doc, results):
            img_shape = (doc.shape[0], doc.shape[1])
            detached_coords, prob_scores = detach_scores([res.get("words")])
            document = builder(
                [doc],
                detached_coords,
                prob_scores,
                [[("None", 1)] * len(detached_coords[0])],
                [img_shape],
                [[{"value": 0, "confidence": None} for _ in detached_coords[0]]],
            )
            documents.append(document)

        for result in documents:
            placeholder.append(result.export())
        
        image = Image.open(BytesIO(image_file))
        image_height, image_width = placeholder[0]['pages'][0]['dimensions']
        cropped_images, bounding_boxes = self._get_cropped_images(placeholder, image, image_width, image_height)
        
        detected_text = self._perform_text_recognition(cropped_images)

        # Build structured JSON output
        current = {
            f"{section_type}": image_url,
            "dimensions": (image_width, image_height),
            "detected_text": " ".join(detected_text).strip(),
            "bounding_boxes": {
                "boxes": bounding_boxes,
                "text": detected_text
            }
        }

        print(f"Processed {image_url} in {time.time() - start_time:.2f} seconds")
        return current

    def _get_cropped_images(self, placeholder, image, image_width, image_height):
        """
        Extract cropped images from the placeholders (bounding boxes).
        :param placeholder: Detected blocks and lines.
        :param image: The original image to crop from.
        :param image_width: The width of the original image.
        :param image_height: The height of the original image.
        :return: Cropped images and bounding boxes.
        """
        cropped_images, bounding_boxes = [], []
        
        for block in placeholder[0]['pages'][0]['blocks']:
            for line in block['lines']:
                for word in line['words']:
                    geometry = word['geometry']
                    pixel_box = self._convert_to_pixels(geometry, image_width, image_height)
                    cropped_images.append(image.crop(pixel_box))
                    bounding_boxes.append(pixel_box)
        
        return cropped_images, bounding_boxes

    def _convert_to_pixels(self, geometry, image_width, image_height):
        """
        Convert normalized geometry coordinates to pixel values.
        :param geometry: Normalized geometry of the word.
        :param image_width: The width of the image.
        :param image_height: The height of the image.
        :return: Bounding box in pixel coordinates.
        """
        top_left, bottom_right = geometry
        x_min, y_min = int(top_left[0] * image_width), int(top_left[1] * image_height)
        x_max, y_max = int(bottom_right[0] * image_width), int(bottom_right[1] * image_height)
        return (x_min, y_min, x_max, y_max)

    def _perform_text_recognition(self, cropped_images):
        """
        Perform text recognition using the TrOCR model.
        :param cropped_images: List of cropped images for OCR.
        :return: Recognized text.
        """
        # Move model to the appropriate device (GPU/CPU)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_trocr.to(device)

        # Process the images using the processor in batch
        pixel_values = self.processor(cropped_images, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)

        with torch.no_grad():
            # Generate text from the images
            generated_ids = self.model_trocr.generate(pixel_values)

        # Decode the generated IDs into readable text (batch decoding)
        return self.processor.batch_decode(generated_ids, skip_special_tokens=True)


    def display_results(self):
        for result in self.results:
            print(f"Image: {result['image_path']}, Detected Text: {result['detected_text']}")
