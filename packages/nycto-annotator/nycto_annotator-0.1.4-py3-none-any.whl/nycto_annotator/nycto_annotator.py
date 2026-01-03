import os
from nycto_annotator.grounding_dino.run import GroundingDINORun


available_models = ["grounding_dino"]

class AutoAnnotator:
    def __init__(self, model_name):
        self.model_name = model_name

        if self.model_name not in available_models:
            raise ValueError(f"Model {self.model_name} is not available. Available models: {available_models}")

    def run(self, input_folder, output_folder, classes_prompt):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.classes_prompt = classes_prompt 

        os.makedirs(self.output_folder, exist_ok=True)   

        if self.model_name == "grounding_dino":
            try:
                runner = GroundingDINORun(self.input_folder, self.output_folder, self.classes_prompt)
                runner.run_GroundingDINORun()
            except Exception as e:
                print(f"Error running GroundingDINORun: {e}")




        
