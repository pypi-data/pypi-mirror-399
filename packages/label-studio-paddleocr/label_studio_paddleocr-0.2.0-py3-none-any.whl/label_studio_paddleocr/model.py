import base64
import logging
import urllib
import urllib.parse
from dataclasses import dataclass
from typing import Dict, List, Optional
from uuid import uuid4

import requests
from label_studio_ml.model import LabelStudioMLBase
from label_studio_ml.response import ModelResponse
from label_studio_sdk.label_interface.objects import PredictionValue

from label_studio_paddleocr.config import settings

logger = logging.getLogger(__name__)


@dataclass
class Block:
    """A text block detected by OCR."""

    label: str
    content: str
    x1: int
    y1: int
    x2: int
    y2: int
    width: int
    height: int


class PaddleOCR(LabelStudioMLBase):
    """Use PaddleOCR to extract text from images."""

    def setup(self):
        # Get configuration for RectangleLabels and TextArea
        self.rl_from_name, self.rl_to_name, _ = self.get_first_tag_occurence(
            "RectangleLabels", "Image"
        )
        self.ta_from_name, self.ta_to_name, _ = self.get_first_tag_occurence(
            "TextArea", "Image"
        )

    def predict(
        self, tasks: List[Dict], context: Optional[Dict] = None, **kwargs
    ) -> ModelResponse:
        """Write the inference logic here
        :param tasks: [Label Studio tasks in JSON format](https://labelstud.io/guide/task_format.html)
        :param context: [Label Studio context in JSON format](https://labelstud.io/guide/ml_create#Implement-prediction-logic)
        :return model_response
            ModelResponse(predictions=predictions) with
            predictions: [Predictions array in JSON format](https://labelstud.io/guide/export.html#Label-Studio-JSON-format-of-annotated-tasks)
        """
        logger.debug(f"Run prediction on {tasks}")

        predictions = []
        for task in tasks:
            task_id = task["id"]
            task_image = task["data"]["image"]
            logger.info(f"Processing task {task_id} with image {task_image}")

            image_local_path = self.get_local_path(
                task_image,
                task_id=task_id,
                ls_host=settings.label_studio_url,
                ls_access_token=settings.label_studio_api_key,
            )

            blocks = self._ocr(image_local_path)
            prediction = self._generate_predications(blocks)
            predictions.append(prediction)

        return ModelResponse(
            model_version=settings.model_version, predictions=predictions
        )

    def _ocr(self, image_path: str) -> list[Block]:
        """Send image to PaddleOCR and handle OCR results
        :param image_path: Local path to the image file
        :return: OCR results as a dictionary
        """

        # https://www.paddleocr.ai/main/version3.x/pipeline_usage/PaddleOCR-VL.html#43
        with open(image_path, "rb") as file:
            image_bytes = file.read()
            image_data = base64.b64encode(image_bytes).decode("ascii")

        payload = {
            "file": image_data,
            "fileType": 1,  # 0 for pdf, 1 for image
        }
        url = urllib.parse.urljoin(settings.paddleocr_url, "/layout-parsing")
        logger.info(f"Sending request to {url}")
        response = requests.post(url, json=payload)

        # handle response
        blocks = []
        if response.status_code != 200:
            logger.warning(
                f"Request failed with status {response.status_code}: {response.text}"
            )
            return blocks

        for layout_parsing_result in response.json()["result"]["layoutParsingResults"]:
            pruned_result = layout_parsing_result["prunedResult"]
            width = pruned_result["width"]
            height = pruned_result["height"]
            for res in pruned_result["parsing_res_list"]:
                bbox = res["block_bbox"]
                block = Block(
                    res["block_label"],
                    res["block_content"],
                    bbox[0],
                    bbox[1],
                    bbox[2],
                    bbox[3],
                    width=width,
                    height=height,
                )
                blocks.append(block)
        return blocks

    def _generate_predications(self, blocks: list[Block]) -> PredictionValue:
        """Generate predictions from OCR blocks
        :param blocks: List of OCR blocks
        :return: SingleTaskPredictions object
        """
        result = []
        for block in blocks:
            # https://github.com/PaddlePaddle/PaddleX/blob/37f1ffdc1daae40bbc5e17141d064951be9796ed/paddlex/inference/pipelines/paddleocr_vl/pipeline.py#L259
            category = "OCR:"
            if block.label == "table":
                category = "Table Recognition:"
            elif block.label == "chart":
                category = "Chart Recognition:"
            elif "formula" in block.label and block.label != "formula_number":
                category = "Formula Recognition:"

            rectangle_sizes = {
                "x": block.x1 / block.width * 100,
                "y": block.y1 / block.height * 100,
                "width": (block.x2 - block.x1) / block.width * 100,
                "height": (block.y2 - block.y1) / block.height * 100,
            }
            id = str(uuid4())

            result.append(
                {
                    "id": id,
                    "from_name": self.rl_from_name,
                    "to_name": self.rl_to_name,
                    "type": "rectanglelabels",
                    "value": {
                        **rectangle_sizes,
                        "rectanglelabels": [category],
                    },
                }
            )
            result.append(
                {
                    "id": id,
                    "from_name": self.ta_from_name,
                    "to_name": self.ta_to_name,
                    "type": "textarea",
                    "value": {
                        **rectangle_sizes,
                        "text": [block.content],
                    },
                }
            )
        return PredictionValue(result=result)
