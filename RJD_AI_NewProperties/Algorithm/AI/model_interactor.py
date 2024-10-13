import requests
from pydantic import BaseModel
from typing import List
from json_response import JsonResponse

class ProductCategory(BaseModel):
    product_category: str

class ProductParameter(BaseModel):
    parameter_name: str
    parameter_value: str

class ProductParameters(BaseModel):
    product_parameters: List[ProductParameter]

class ModelInteractor:
    def __init__(self, ai_model: str, api_url: str):
        self.ai_model = ai_model
        self.api_url = api_url

    def classify(self, text: str) -> str:
        request_body = {
            "model": self.ai_model,
            "prompt": f"Выбери общую категорию для продукта: {text}",
            "max_tokens": 512,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "product_category_response",
                    "strict": "true",
                    "language": "ru",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "product_category": {
                                "type": "string"
                            }
                        },
                        "required": ["product_category"]
                    }
                }
            },
            "temperature": 0.9
        }

        response = requests.post(self.api_url, json=request_body)
        response.raise_for_status()
        json_response = JsonResponse.model_validate_json(response.text)

        category = ProductCategory.model_validate_json(json_response.choices[0].text)
        return category.product_category

    def parameterize(self, text: str) -> List[ProductParameter]:
        request_body = {
            "model": self.ai_model,
            "prompt": f"Укажи список основных параметров (не более 10) этого продукта: {text}",
            "max_tokens": 512,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "product_parameters_response",
                    "strict": "true",
                    "language": "ru",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "product_parameters": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "parameter_name": {"type": "string"},
                                        "parameter_value": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "required": ["product_parameters"]
                    }
                }
            },
            "temperature": 0.6
        }

        response = requests.post(self.api_url, json=request_body)
        response.raise_for_status()
        json_response = JsonResponse.model_validate_json(response.text)

        parameters = ProductParameters.model_validate_json(json_response.choices[0].text)
        return parameters.product_parameters
