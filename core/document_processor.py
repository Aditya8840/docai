from enum import Enum
from core.llm_handler import LLMHandler
from prompts.driving_license import get_driving_license_prompt
from core.validator import DrivingLicense, ShopReceipt, Resume
from pydantic import ValidationError
import json
from prompts.store_recipt import get_store_receipt_prompt
from prompts.resume import get_resume_prompt
from core.ocr_handler import OCRHandler
import time

class DocumentType(Enum):
    DRIVING_LICENSE = "driving_license"
    SHOP_RECEIPT = "shop_receipt"
    RESUME = "resume"

class ProcessingResult:
    def __init__(self, success: bool, document_type: DocumentType, raw_response: str, validated_data: dict, error_message: str = None):
        self.success = success
        self.document_type = document_type
        self.raw_response = raw_response
        self.validated_data = validated_data
        self.error_message = error_message

    def to_dict(self):
        return {
            "success": self.success,
            "document_type": self.document_type.value,
            "raw_response": self.raw_response,
            "validated_data": self.validated_data,
            "error_message": self.error_message
        }
    
    def __repr__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"ProcessingResult({status}, {self.document_type.value})"

class DocumentProcessor:
    def __init__(self):
        self.llm_handler = LLMHandler()
        self.ocr_handler = OCRHandler()

        self.document_configs = {
            DocumentType.DRIVING_LICENSE: {
                'prompt_func': get_driving_license_prompt,
                'validator_class': DrivingLicense,
                'uses_ocr': False
            },
            DocumentType.SHOP_RECEIPT: {
                'prompt_func': get_store_receipt_prompt,
                'validator_class': ShopReceipt,
                'uses_ocr': False
            },
            DocumentType.RESUME: {
                'prompt_func': get_resume_prompt,
                'validator_class': Resume,
                'uses_ocr': False
            }
        }

    def _create_result(self, success: bool, document_type: DocumentType, raw_response: str, 
                      validated_data: dict = None, error_message: str = None):
        """Helper method to create ProcessingResult objects"""
        return ProcessingResult(
            success=success,
            document_type=document_type,
            raw_response=raw_response,
            validated_data=validated_data,
            error_message=error_message
        ).to_dict()

    def _clean_response(self, response: str) -> str:
        """Clean LLM response by removing JSON markers"""
        response = response.replace("```json", "").replace("```", "")
        return response.strip()

    def _process_llm_response(self, response: str, validator_class, document_type: DocumentType):
        """Common logic for processing LLM responses and validation"""
        try:
            response = self._clean_response(response)
            data = json.loads(response)
            model = validator_class(**data)
            
            return self._create_result(
                success=True,
                document_type=document_type,
                raw_response=response,
                validated_data=model.model_dump()
            )
            
        except ValidationError as e:
            return self._create_result(
                success=False,
                document_type=document_type,
                raw_response=response,
                error_message=str(e)
            )
        except json.JSONDecodeError:
            return self._create_result(
                success=False,
                document_type=document_type,
                raw_response=response,
                error_message="Failed to parse JSON response"
            )

    def process_document(self, document_type: DocumentType, image_path: str | None = None, max_retries: int = 3):
        """Generic document processing method with simple retry logic"""
        if document_type not in self.document_configs:
            raise ValueError(f"Unsupported document type: {document_type}")
        
        config = self.document_configs[document_type]
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if config['uses_ocr'] and image_path: # TODO: We can use this to reduce cost of LLM calls
                    ocr_text = self.ocr_handler.process_image(image_path)
                    ocr_text_str = " ".join([result[1] for result in ocr_text]).strip()
                    prompt = config['prompt_func'](ocr_text_str)
                    response = self.llm_handler.generate_response(prompt)
                else:
                    prompt = config['prompt_func']()
                    response = self.llm_handler.generate_response(prompt, image_path)
                
                result = self._process_llm_response(response, config['validator_class'], document_type)
                
                if result['success']:
                    return result
                
                last_error = result['error_message'] # TODO: We can use this error to retry the request
                
                if attempt < max_retries - 1:
                    time.sleep(1.0 * (attempt + 1))
                    
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    time.sleep(1.0 * (attempt + 1))

        return self._create_result(
            success=False,
            document_type=document_type,
            raw_response="",
            error_message=f"Failed after {max_retries} attempts. Last error: {last_error}"
        )
