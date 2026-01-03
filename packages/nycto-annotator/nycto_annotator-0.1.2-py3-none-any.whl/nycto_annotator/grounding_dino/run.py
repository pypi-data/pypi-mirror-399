
class GroundingDINORun:
    def __init__(self, *args, **kwargs):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.device = "cuda" if torch.cuda.is_available() else "cpu" 
        self.model_id = "IDEA-Research/grounding-dino-base"
        self.text_prompt = text_prompt
        self.text = self.process_text_prompt()
        self.threshold = threshold

    def run_GroundingDINORun(self):

        import torch
        import os
        from PIL import Image
        from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection 
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from create_bbox.bbox import BBox 

        processor = AutoProcessor.from_pretrained(self.model_id)
        model = AutoModelForZeroShotObjectDetection.from_pretrained(self.model_id).to(self.device)

        for image_path in os.listdir(self.input_folder):
            image = Image.open(os.path.join(self.input_folder, image_path)).convert("RGB")
            inputs = processor(images=image, text=self.text, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = model(**inputs)
            
            results = processor.post_process_grounded_object_detection(
                outputs,
                inputs.input_ids,
                threshold=self.threshold,
                target_sizes=[image.size[::-1]]
            )
            
            bbox = BBox(results, image, os.path.join(self.output_folder, image_path))
            bbox.create_bbox()
    

    def process_text_prompt(self):
        values = self.text_prompt.values()
        text = ". ".join(values) 
        return text




            



