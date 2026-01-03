from nycto_annotator import AutoAnnotator 
from pathlib import Path

ROOT = Path(__file__).parent.parent

def test_auto_annotate():
    input_folder = ROOT / "tests/input"
    output_folder = ROOT / "tests/output"
    model_name = "grounding_dino"
    classes_prompt = {"classes": "person, car, bike"}
    annotator = AutoAnnotator(model_name)
    annotator.run(input_folder, output_folder, classes_prompt)
    assert annotator is not None

if __name__ == "__main__":
    test_auto_annotate()
