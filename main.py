import os
from core.document_processor import DocumentProcessor, DocumentType

def main():
    print("Hello from data-extraction!")
    print("Note: For advanced usage with custom prompts and flexible I/O, use the CLI tool:")
    print("  python cli.py --type driving_license --dataset datasets/Drivers_license")
    print("  python cli.py --help for more options")
    print()
    print("Running basic example with Drivers_license dataset...")
    
    document_processor = DocumentProcessor()
    
    drivers_license_dir = "datasets/Drivers_license"
    if not os.path.exists(drivers_license_dir):
        print(f"Dataset directory '{drivers_license_dir}' not found.")
        print("Please ensure the datasets/Drivers_license directory exists with resume files.")
        return
    
    files = os.listdir(drivers_license_dir)
    if not files:
        print(f"No files found in '{drivers_license_dir}' directory.")
        return
    
    print(f"Processing {len(files)} files from {drivers_license_dir}:")
    
    for i, file in enumerate(files, 1):
        if file.startswith('.'):
            continue
            
        print(f"[{i}/{len(files)}] Processing: {file}")
        try:
            result = document_processor.process_document(DocumentType.DRIVING_LICENSE, f"{drivers_license_dir}/{file}")
            
            if result['success']:
                print(f"  ✓ SUCCESS")
                if result.get('validated_data'):
                    data = result['validated_data']
                    if data.get('full_name'):
                        print(f"    Name: {data['full_name']}")
                    if data.get('email'):
                        print(f"    Email: {data['email']}")
            else:
                print(f"  ✗ FAILED: {result.get('error_message', 'Unknown error')}")
                
        except Exception as e:
            print(f"  ✗ ERROR: {str(e)}")
        
        print()

if __name__ == "__main__":
    main()
