# OpeAIBatcher

OpeAIBatcher is a Python wrapper for the OpenAI Batch API, designed to streamline the process of handling large datasets with OpenAI's powerful language models. This utility facilitates tasks such as file uploads, batch creation, status tracking, and result retrieval, making it easier to manage extensive API requests efficiently.

## Features

- **File Upload:** Easily upload files to OpenAI for batch processing.
- **Batch Creation:** Create batches from uploaded files for processing with OpenAI's API.
- **Status Tracking:** Track the status of your batches in real-time.
- **Result Retrieval:** Retrieve and save batch results once processing is complete.
- **Content Extraction:** Extract relevant content from batch responses and save it in a structured format.(Just json surppoted for now)

## Installation

To use OpeAIBatcher, ensure you have the necessary dependencies installed. You can install them using pip:

```bash
pip install openai tqdm jsonlines
```

## Usage

Here's a basic example of how to use OpeAIBatcher:

```python
from opeai_batcher import OpeAIBatcher

# Initialize the batcher with your OpenAI API key
batcher = OpeAIBatcher(api_key="your-api-key")

# Upload a file for batch processing
input_file = batcher.file_upload("example.jsonl")

# Create a batch from the uploaded file
batch = batcher.create_batch(input_file)

# Track the status of your batch
batcher.retrieve_batch_status(batch)

# Retrieve and save the batch results
batcher.retrieve_batch_results(batch, retrive_path="output")

# Extract content from the batch responses
batcher.extract_content_from_response("output/" + batch.output_file_id + ".jsonl", "output")
```

## Methods

### `__init__(self, base_url: str = "www.openai.com", api_key: str = "sk-example", headers: dict = None, log_level: str = "INFO")`

Initializes the OpeAIBatcher with the given parameters.

- `base_url`: The base URL for the OpenAI API.
- `api_key`: Your OpenAI API key.
- `headers`: Optional headers for the API requests.
- `log_level`: Logging level (default: "INFO").

### `file_upload(self, file_path: str) -> FileObject`

Uploads a file to OpenAI for batch processing.

- `file_path`: Path to the file to be uploaded.

### `list_files(self) -> List[FileObject]`

Lists all files uploaded for batch processing.

### `create_batch(self, file: FileObject) -> Batch`

Creates a batch from the uploaded file.

- `file`: The file object returned from the `file_upload` method.

### `list_batches(self) -> List[Batch]`

Lists all batches created for processing.

### `retrieve_batch_status(self, batch: Optional[Batch])`

Retrieves the status of the specified batch and tracks its progress.

- `batch`: The batch object or batch ID.

### `retrieve_batch_results(self, batch: Optional[Batch], retrive_path: str = ".") -> bool`

Retrieves the results of the specified batch and saves them to the specified path.

- `batch`: The batch object or batch ID.
- `retrive_path`: Path to save the retrieved results.

### `extract_content_from_response(self, source_jsonl_path: str, target_jsonl_path: str) -> bool`

Extracts content from batch responses and saves it in a structured format.

- `source_jsonl_path`: Path to the source JSONL file containing the batch responses.
- `target_jsonl_path`: Path to save the extracted content.

## License

This project is licensed under the MIT License.

---

Feel free to contribute, open issues, or submit pull requests to improve OpeAIBatcher!