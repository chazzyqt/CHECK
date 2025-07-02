import cv2
import numpy as np
import json
import cloudinary
import cloudinary.uploader
import requests
import time 
import re
class MarkerDetector:
    def __init__(self, min_square_size=75, max_square_size=1000, aspect_ratio_tolerance=0.2):
        self.min_square_size = min_square_size
        self.max_square_size = max_square_size
        self.aspect_ratio_tolerance = aspect_ratio_tolerance
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name='djdjamrmj',
            api_key='535437436958957',
            api_secret='LbNXcB_CSw80U_4cIj7QC4-azJk'
        )
    def process_image_full(self, image, image_filename):
        # Check if image is a file path or URL
        image_path = image_filename
        if isinstance(image, str):
            if image.startswith('http://') or image.startswith('https://'):
                image = self.load_image_from_url(image)
            else:
                image = self.load_image(image)

        if image is None:
            raise ValueError("Error: Unable to load image")

        # Convert to grayscale and threshold
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        
        # Morphological operations to reduce noise
        kernel = np.ones((7, 7), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # List to store square markers
        square_markers = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.03 * cv2.arcLength(contour, True), True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                area = w * h
                contour_area = cv2.contourArea(contour)

                # Check square-like features
                lower_aspect_ratio = 1.0 - self.aspect_ratio_tolerance
                upper_aspect_ratio = 1.0 + self.aspect_ratio_tolerance
                
                if (lower_aspect_ratio < aspect_ratio < upper_aspect_ratio and 
                    self.min_square_size <= area <= self.max_square_size and
                    0.8 * area <= contour_area <= 1.2 * area):
                    square_markers.append(approx)

        name_section, answer_section = self.extract_sections(image, square_markers, image_path)
        original_url = None  # Initialize with a default value
        error = None  # Initialize error as None
        
        # Check if both sections are present before uploading the original image
        if name_section is not None and answer_section is not None: 
            original_url = self.upload_original_image(image, f'{image_path}') if image is not None else None
            if original_url is None:
                error = "Failed to upload the original image."

        # Upload sections to Cloudinary and get their URLs
        #name_url = self.upload_image(name_section, f'{image_path}_name_section') if name_section is not None else None
        #answer_url = self.upload_image(answer_section, f'{image_path}_answer_section') if answer_section is not None else None

        # Check if each upload was successful
        # if name_section is not None and name_url is None:
        #     error = "Failed to upload the name section image."
        # if answer_section is not None and answer_url is None:
        #     error = "Failed to upload the answer section image."

        # Return JSON output with URLs and error status
        return json.dumps({f"{image_path}": {
            "original_image": original_url,
            # "name_section_url": name_url,
            # "answer_section_url": answer_url,
            "error": error
        }})
    
    def process_image(self, image, image_filename):
        # Check if image is a file path or URL
        image_path = image_filename
        if isinstance(image, str):
            if image.startswith('http://') or image.startswith('https://'):
                image = self.load_image_from_url(image)
            else:
                image = self.load_image(image)

        if image is None:
            raise ValueError("Error: Unable to load image")

        # Convert to grayscale and threshold
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
        
        # Morphological operations to reduce noise
        kernel = np.ones((7, 7), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Find contours
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # List to store square markers
        square_markers = []
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.03 * cv2.arcLength(contour, True), True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                area = w * h
                contour_area = cv2.contourArea(contour)

                # Check square-like features
                lower_aspect_ratio = 1.0 - self.aspect_ratio_tolerance
                upper_aspect_ratio = 1.0 + self.aspect_ratio_tolerance
                
                if (lower_aspect_ratio < aspect_ratio < upper_aspect_ratio and 
                    self.min_square_size <= area <= self.max_square_size and
                    0.8 * area <= contour_area <= 1.2 * area):
                    square_markers.append(approx)

        #name_section, answer_section = self.extract_sections(image, square_markers, image_path)
        original_url = None  # Initialize with a default value
        error = None  # Initialize error as None
        name_section = None
        answer_section = None
        name_url = None
        answer_url = None
        # Check if both sections are present before uploading the original image
        # if name_section is not None and answer_section is not None: 
        #     original_url = self.upload_original_image(image, f'{image_path}') if image is not None else None
        #     if original_url is None:
        #         error = "Failed to upload the original image."
        original_url = self.upload_original_image(image, f'{image_path}') if image is not None else None
        # Upload sections to Cloudinary and get their URLs
        #name_url = self.upload_image(name_section, f'{image_path}_name_section') if name_section is not None else None
        #answer_url = self.upload_image(answer_section, f'{image_path}_answer_section') if answer_section is not None else None

        # Check if each upload was successful
        if name_section is not None and name_url is None:
            error = "Failed to upload the name section image."
        if answer_section is not None and answer_url is None:
            error = "Failed to upload the answer section image."

        # Return JSON output with URLs and error status
        return json.dumps({f"{image_path}": {
            "original_image": original_url,
            "name_section_url": name_url or "",
            "answer_section_url": answer_url or "",
            "error": error
        }})

    def load_image(self, image_path):
        """Load an image from a file path."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Error: Unable to load image from {image_path}")
        return image

    def load_image_from_url(self, image_url):
        """Load an image from a URL."""
        response = requests.get(image_url)
        if response.status_code == 200:
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        else:
            raise ValueError(f"Error: Unable to load image from {image_url}")
            return None

    def extract_sections(self, image, square_markers, image_path):
        # Calculate the center markers and sort them
        markers = []
        for marker in square_markers:
            M = cv2.moments(marker)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                markers.append((cX, cY))

        markers = sorted(markers, key=lambda m: (round(m[1] / 100) * 100, m[0]))
        if len(markers) == 6:
            x_start_name = min(markers[0][0], markers[1][0])
            x_end_name = max(markers[0][0], markers[1][0])
            y_start_name = min(markers[0][1], markers[2][1])
            y_end_name = max(markers[0][1], markers[2][1])
            name_section = image[y_start_name:y_end_name, x_start_name:x_end_name]
            
            x_start = min(markers[3][0], markers[4][0])
            x_end = max(markers[3][0], markers[4][0])
            y_start = min(markers[3][1], markers[4][1])
            y_end = max(markers[3][1], markers[4][1])

            if x_end - x_start > 0 and y_end - y_start > 0:
                answer_section = image[y_start:y_end, x_start:x_end]
            else:
                raise ValueError(f"Invalid dimensions for answer section of {image_path}")
                answer_section = None

            return name_section, answer_section

        raise ValueError(f"Error: Detected {len(markers)} markers on {image_path}, expected 6.")
        return None, None

    def upload_image(self, image_array, public_id):
        try:
            # Check if the image array is empty or None
            if image_array is None or image_array.size == 0:
                raise ValueError(f"Cannot upload. The image array for '{public_id}' is empty or None.")
            
            # Encode the NumPy array to an image format (e.g., JPEG)
            _, buffer = cv2.imencode('.jpg', image_array)
            image_data = buffer.tobytes()  # Convert to bytes
            public_id = public_id.replace("\\", "/").replace(" ", "_")  # Replace invalid characters
            print(f"Uploading image with public_id: {public_id}")
            
            # Upload the image to Cloudinary
            response = cloudinary.uploader.upload(
                image_data,
                filename=public_id,
                folder="CHECK",
                resource_type='image'
            )
            
            return response['url']  # Return the URL of the uploaded image

        except Exception as e:
            raise Exception(f"Error uploading image '{public_id}': {e}")

    
    def upload_original_image(self, image, public_id):
    # Check if the image is a NumPy array
        if not isinstance(image, np.ndarray):
            raise ValueError("The provided image is not a valid NumPy array.")

        # Debugging output to check the shape and type of the image
        print(f"Image type: {type(image)}")
        print(f"Image shape: {image.shape if isinstance(image, np.ndarray) else 'N/A'}")

        # Encode the NumPy array to a JPEG format
        success, encoded_image = cv2.imencode('.jpg', image)
        if not success:
            raise ValueError("Could not encode image to JPEG format")
        
        # Convert the encoded image to bytes
        image_bytes = encoded_image.tobytes()
        
        # Clean the public_id to remove any existing extension
        public_id = re.sub(r'\.\w+$', '', public_id)  # Remove any file extension
        public_id = public_id.replace("\\", "/").replace(" ", "_")
        print(f"Uploading image with public_id: {public_id}")
        
        # Upload the image to Cloudinary
        response = cloudinary.uploader.upload(
            image_bytes,
            public_id=public_id,
            folder="CHECK",
            resource_type='image'
        )
        
        return response['url']

    def process_images(self, images):
        results = []
        for image in images:
            start_time = time.time()
            try:
                json_result = self.process_image(image)
                if json_result:
                    results.append(json.loads(json_result))
            except Exception as e:
                results.append({"error": str(e)})
            end_time = time.time()
            print(f"Processed in {end_time - start_time:.2f} seconds.")
        
        return json.dumps(results)
