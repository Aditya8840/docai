# Data Extraction
AI-powered document processing tool that extracts structured data from resumes, driving licenses, and shop receipts using OCR and LLM models.

## Features

- **Document Processing**: Extract structured data from resumes, driving licenses, and shop receipts
- **Custom Prompts**: Use your own prompts for specific extraction needs
- **Batch Processing**: Process entire directories of documents
- **Validation**: Pydantic-based self-validation with retry logic
- **Output Management**: JSON results with processing summaries

## Setup

### Requirements
- Python 3.11+
- uv package manager
- Google Gemini API key

### Installation

1. Clone and navigate to the project:
```bash
git clone https://github.com/Aditya8840/docai.git
cd docai
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
```
Edit the `.env` file and add your keys.

## Usage

### CLI Tool

Process documents using the command line interface:

```bash
# Basic usage
uv run python cli.py --type <document_type> --dataset <dataset_directory>

# With custom prompt
uv run python cli.py --type <document_type> --dataset <dataset_directory> --custom-prompt <prompt_file>
```

**Document Types:**
- `resume` - Extract name, email, phone, skills, experience
- `driving_license` - Extract license details and personal information  
- `shop_receipt` - Extract items, prices, totals, store information

**Examples:**

```bash
# Process resumes
uv run python cli.py --type resume --dataset datasets/Resume

# Process driving licenses with custom prompt
uv run python cli.py --type driving_license --dataset datasets/Drivers_license --custom-prompt custom_dl_prompt.txt

# Process shop receipts
uv run python cli.py --type shop_receipt --dataset datasets/shop_receipts
```

### Quick Test

Run the basic example:
```bash
uv run python main.py
```

## Project Structure

```
├── cli.py              # Command-line interface
├── main.py             # Basic usage example
├── core/
│   ├── document_processor.py  # Main processing logic
│   ├── llm_handler.py         # LLM integration
│   ├── ocr_handler.py         # OCR processing
│   └── validator.py           # Data validation models
├── prompts/            # Document-specific prompts
├── datasets/           # Input data directories
└── outputs/            # Generated results
```

## Output

Results are saved as JSON files in the `outputs/` directory with:
- Processing summary (success/failure counts, timestamp)
- Individual file results with extracted data
- Error messages for failed extractions

Example [output structure](/outputs/driving_license_Drivers_license_20250621_153820.json)


## Custom Prompts

Create custom extraction prompts by providing a text file with your specific instructions. The system will use your prompt instead of the default ones.

---