

class UnifiedDataProcessor:
    def __init__(self, data):
        """
        Initialize the UnifiedDataProcessor class with input data.
        
        :param data: List of dictionaries containing input data to process.
        """
        self.data = data
        self.all_results = []  # Initialize an empty list to store the results of all entries

    def process_full_section(self, whole):
        """
        Process the full_section of each entry.
        """
        if not isinstance(whole, dict):
            raise ValueError(f"Expected a dictionary, but got {type(whole)}: {whole}")
        
        full_data = []
        full_dimensions = whole.get('dimensions', None)
        full_information = whole.get('detected_text', None)

        # Combine full_section bounding boxes and text into unified_data
        full_data.extend([
            {"box": box, "text": text}
            for box, text in zip(whole['bounding_boxes']['boxes'], whole['bounding_boxes']['text'])
        ])

        return full_data, full_information, full_dimensions

    def process_name_section(self, name_section):
        """
        Process the name_section of each entry.
        
        :param name_section: Dictionary containing the name_section data for a single entry.
        :return: List of unified text and bounding boxes for the name section.
        """
        name_data = []
        score_position = name_section.get('score_positions', None)
        name_dimensions = name_section.get('dimensions', None)
        information = name_section.get('detected_text', None)

        # Combine name_section bounding boxes and text into unified_data
        name_data.extend([
            {"box": box, "text": text}
            for box, text in zip(name_section['bounding_boxes']['boxes'], name_section['bounding_boxes']['text'])
        ])

        return name_data, score_position, information, name_dimensions

    def process_answer_section(self, answer_section):
        """
        Process the answer_section of each entry.
        
        :param answer_section: Dictionary containing the answer_section data for a single entry.
        :return: List of unified text and bounding boxes for the answer section.
        """
        answer_data = []
        placeholder_position = answer_section.get('placeholder_positions', None)
        answer_dimensions = answer_section.get('dimensions', None)
        answers = answer_section.get('detected_text', None)

        # Combine answer_section bounding boxes and text into unified_data
        answer_data.extend([
            {"box": box, "text": text}
            for box, text in zip(answer_section['bounding_boxes']['boxes'], answer_section['bounding_boxes']['text'])
        ])

        return answer_data, placeholder_position, answers, answer_dimensions

    def process_entry(self, entry):
        """
        Process a single entry and return the unified result.
        
        :param entry: Dictionary representing a single entry to process.
        :return: Dictionary containing the unified result for the entry.
        """
        original = entry.get("image_path", "")
        original_size = entry.get("original_size", "")
        
        name_data = [] 
        answer_data = [] # Initialize an empty list to store the combined results for this entry
        score_position = None
        placeholder_position = None
        information = None
        answers = None


        # Processing name_section_text
        for name_section in entry.get('name_section_text', []):
            section_data, score_position, information,name_dimension= self.process_name_section(name_section)
            name_data.extend(section_data)

        # Processing answer_section_text
        for answer_section in entry.get('answer_section_text', []):
            section_data, placeholder_position, answers, answer_dimension = self.process_answer_section(answer_section)
            answer_data.extend(section_data)

        # Now the result combines both name_section and answer_section data
        result = {
            "original_url": original,
            "original_size":original_size,
            "name_size":name_dimension,
            "answer_size": answer_dimension,
            "name_data": name_data,
            "answer_data": answer_data,
            "name_section": information,
            "answer_section": answers,
            "score_positions": score_position,
            "placeholder_position": placeholder_position
        }

        return result
    
    def process_full_entry(self, entry):
        generated_uid = entry.get("generated_uid", "")
        original = entry.get("image_path", "")
        full_info = entry.get("full_information", "")
        
        # Check and adapt based on the type of full_info
        if isinstance(full_info, dict):
            # Wrap the single dictionary in a list for uniform processing
            full_info = [full_info]
        elif not isinstance(full_info, list):
            raise ValueError(f"Expected a list or dict for 'full_information', but got {type(full_info)}: {full_info}")

        full_data = []

        # Processing each full_section
        for full_section in full_info:
            if not isinstance(full_section, dict):
                raise ValueError(f"Each section must be a dictionary, but got {type(full_section)}: {full_section}")

            section_data, full_information, full_dimensions = self.process_full_section(full_section)
            full_data.extend(section_data)

        result = {
            "original_url": original,
            "generated_uid": generated_uid,
            "original_size": full_dimensions,
            "full_data": full_data,
            "full_section": full_information,
        }

        return result




    def process_all_entries(self):
        """
        Process all entries and return the results as a list.
        
        :return: List of dictionaries containing the unified results for all entries.
        """
        for entry in self.data:
            result = self.process_entry(entry)
            self.all_results.append(result)
        
        return self.all_results
    
    def process_all_full_entries(self):
        """
        Process all entries and return the results as a list.
        
        :return: List of dictionaries containing the unified results for all entries.
        """
        for entry in self.data:
            result = self.process_full_entry(entry)
            self.all_results.append(result)
        
        return self.all_results


# Example usage for integrating into an API:
# Assuming `data` is the input data you want to process
