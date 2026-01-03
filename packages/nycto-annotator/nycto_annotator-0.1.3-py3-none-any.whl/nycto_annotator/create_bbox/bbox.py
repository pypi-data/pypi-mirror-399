class BBox:
    def __init__(self, results, image, output_path):
        self.results = results
        self.image = image
        self.output_path = output_path

    def create_bbox(self):
        
        from PIL import ImageDraw

        draw = ImageDraw.Draw(self.image)
        for result in self.results:
            boxes = result["boxes"].cpu().numpy()
            scores = result["scores"].cpu().numpy()
            labels = result["labels"]

            for box, score, label in zip(boxes, scores, labels):
                # box is [x_min, y_min, x_max, y_max]
                draw.rectangle(list(box), outline="red", width=3)
        
        # save the image
        self.image.save(self.output_path)

            