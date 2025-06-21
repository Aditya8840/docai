import argparse
import os
import json
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from core.document_processor import DocumentProcessor, DocumentType
from core.validator import Resume, DrivingLicense, ShopReceipt


class CustomPromptProcessor:
    def __init__(self, prompt_file_path: str, validator_class):
        self.prompt_file_path = prompt_file_path
        self.validator_class = validator_class
        self.custom_prompt = self._load_custom_prompt()
    
    def _load_custom_prompt(self) -> str:
        try:
            with open(self.prompt_file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Custom prompt file not found: {self.prompt_file_path}")
        except Exception as e:
            raise Exception(f"Error reading custom prompt file: {e}")
    
    def get_prompt(self) -> str:
        return self.custom_prompt


class DocumentProcessorCLI:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        self.validator_map = {
            DocumentType.RESUME: Resume,
            DocumentType.DRIVING_LICENSE: DrivingLicense,
            DocumentType.SHOP_RECEIPT: ShopReceipt
        }
    
    def _get_document_type(self, doc_type_str: str) -> DocumentType:
        type_mapping = {
            'resume': DocumentType.RESUME,
            'driving_license': DocumentType.DRIVING_LICENSE,
            'shop_receipt': DocumentType.SHOP_RECEIPT
        }
        
        if doc_type_str.lower() not in type_mapping:
            available_types = list(type_mapping.keys())
            raise ValueError(f"Invalid document type '{doc_type_str}'. Available types: {available_types}")
        
        return type_mapping[doc_type_str.lower()]
    
    def _get_supported_file_extensions(self) -> List[str]:
        return ['.jpg', '.jpeg', '.png', '.pdf', '.tiff', '.bmp']
    
    def _is_supported_file(self, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in self._get_supported_file_extensions()
    
    def _setup_custom_prompt(self, document_type: DocumentType, custom_prompt_path: str):
        validator_class = self.validator_map[document_type]
        custom_prompt_processor = CustomPromptProcessor(custom_prompt_path, validator_class)
        
        self.processor.document_configs[document_type]['prompt_func'] = custom_prompt_processor.get_prompt
    
    def _save_results(self, results: List[dict], document_type: DocumentType, 
                     dataset_name: str, custom_prompt_name: Optional[str] = None) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename_parts = [
            document_type.value,
            dataset_name,
            timestamp
        ]
        
        if custom_prompt_name:
            filename_parts.insert(-1, f"custom_{custom_prompt_name}")
        
        filename = "_".join(filename_parts) + ".json"
        output_path = self.output_dir / filename
        
        summary = {
            "processing_summary": {
                "document_type": document_type.value,
                "dataset_directory": dataset_name,
                "total_files": len(results),
                "successful_extractions": sum(1 for r in results if r.get("success", False)),
                "failed_extractions": sum(1 for r in results if not r.get("success", False)),
                "timestamp": timestamp,
                "custom_prompt_used": custom_prompt_name is not None,
                "custom_prompt_name": custom_prompt_name
            },
            "results": results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def process_dataset(self, document_type_str: str, dataset_dir: str, 
                       custom_prompt_path: Optional[str] = None) -> str:
        
        document_type = self._get_document_type(document_type_str)
        dataset_path = Path(dataset_dir)
        
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")
        
        if not dataset_path.is_dir():
            raise ValueError(f"Dataset path is not a directory: {dataset_dir}")
        
        custom_prompt_name = None
        if custom_prompt_path:
            if not Path(custom_prompt_path).exists():
                raise FileNotFoundError(f"Custom prompt file not found: {custom_prompt_path}")
            
            self._setup_custom_prompt(document_type, custom_prompt_path)
            custom_prompt_name = Path(custom_prompt_path).stem
            print(f"Using custom prompt from: {custom_prompt_path}")
        
        supported_files = []
        for file_path in dataset_path.rglob('*'):
            if file_path.is_file() and self._is_supported_file(str(file_path)):
                supported_files.append(file_path)
        
        if not supported_files:
            print(f"No supported files found in {dataset_dir}")
            print(f"Supported extensions: {', '.join(self._get_supported_file_extensions())}")
            return ""
        
        print(f"Found {len(supported_files)} supported files to process")
        print(f"Document type: {document_type.value}")
        print(f"Processing files...")
        
        results = []
        for i, file_path in enumerate(supported_files, 1):
            print(f"Processing [{i}/{len(supported_files)}]: {file_path.name}")
            
            try:
                result = self.processor.process_document(document_type, str(file_path))
                result['file_path'] = str(file_path)
                result['file_name'] = file_path.name
                results.append(result)
                
                status = "✓ SUCCESS" if result.get('success', False) else "✗ FAILED"
                print(f"  {status}")
                
                if not result.get('success', False) and result.get('error_message'):
                    print(f"    Error: {result['error_message']}")
                    
            except Exception as e:
                error_result = {
                    'success': False,
                    'document_type': document_type.value,
                    'file_path': str(file_path),
                    'file_name': file_path.name,
                    'error_message': str(e),
                    'raw_response': '',
                    'validated_data': None
                }
                results.append(error_result)
                print(f"  ✗ FAILED - {str(e)}")
        
        dataset_name = dataset_path.name
        output_file = self._save_results(results, document_type, dataset_name, custom_prompt_name)
        
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        print(f"\nProcessing completed!")
        print(f"Total files: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Results saved to: {output_file}")
        
        return output_file


def main():
    parser = argparse.ArgumentParser(
        description="CLI tool for document processing with custom prompt support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process resumes from datasets/Resume directory
  python cli.py --type resume --dataset datasets/Resume
  
  # Process driving licenses with custom prompt
  python cli.py --type driving_license --dataset datasets/Drivers_license --custom-prompt my_custom_prompt.txt
  
  # Process shop receipts
  python cli.py --type shop_receipt --dataset datasets/shop_receipts
  
Available document types: resume, driving_license, shop_receipt
Supported file formats: jpg, jpeg, png, pdf, tiff, bmp
        """
    )
    
    parser.add_argument(
        '--type', '-t',
        required=True,
        help='Document type to process (resume, driving_license, shop_receipt)'
    )
    
    parser.add_argument(
        '--dataset', '-d',
        required=True,
        help='Path to dataset directory containing documents to process'
    )
    
    parser.add_argument(
        '--custom-prompt', '-p',
        help='Path to custom prompt text file (optional)'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='Document Processor CLI v1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        cli = DocumentProcessorCLI()
        output_file = cli.process_dataset(
            document_type_str=args.type,
            dataset_dir=args.dataset,
            custom_prompt_path=args.custom_prompt
        )
        
        if output_file:
            print(f"\n🎉 All results saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 