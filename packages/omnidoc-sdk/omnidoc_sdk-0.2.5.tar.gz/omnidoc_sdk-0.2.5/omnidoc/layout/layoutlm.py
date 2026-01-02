from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
from PIL import Image

class LayoutLMExtractor:
    def __init__(self):
        self.processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")
        self.model = LayoutLMv3ForTokenClassification.from_pretrained(
            "microsoft/layoutlmv3-base"
        )

    def extract(self, image, words, boxes):
        encoding = self.processor(
            image, words, boxes=boxes, return_tensors="pt"
        )
        outputs = self.model(**encoding)
        return outputs
