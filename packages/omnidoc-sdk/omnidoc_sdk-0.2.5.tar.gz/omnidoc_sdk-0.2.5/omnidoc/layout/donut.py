from transformers import DonutProcessor, VisionEncoderDecoderModel
from PIL import Image

class DonutExtractor:
    def __init__(self):
        self.processor = DonutProcessor.from_pretrained(
            "naver-clova-ix/donut-base-finetuned-docvqa"
        )
        self.model = VisionEncoderDecoderModel.from_pretrained(
            "naver-clova-ix/donut-base-finetuned-docvqa"
        )

    def extract(self, image: Image.Image):
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        outputs = self.model.generate(pixel_values)
        return self.processor.decode(outputs[0], skip_special_tokens=True)
