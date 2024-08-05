from openai import OpenAI
from openai.types import *
from typing import List, Dict, Optional
import time
from tqdm import tqdm
import jsonlines
import json
import os
import logging
import re

class OpeAIBatcher():
    
    def __init__(self, base_url:str = "www.openai.com", api_key:str = "sk-example", headers:dict = None, log_level:str = "INFO"):
        
        if log_level == "DEBUG":
            logging.basicConfig(level=logging.DEBUG)
        elif log_level == "WARNING":
            logging.basicConfig(level=logging.WARNING)
        elif log_level == "ERROR":
            logging.basicConfig(level=logging.ERROR)
        else:
            logging.basicConfig(level=logging.INFO)
        
        self.logger = logging.getLogger(__name__)

        self.base_url = base_url
        self.api_key = api_key
        if headers is None:
            self.logger.warning("No headers provided, using default headers")
            self.headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer "+ self.api_key
            }
        else:
            self.headers = headers

        self.client = OpenAI(base_url=base_url, api_key=api_key, default_headers=headers)

    def file_upload(self, file_path:str) -> FileObject:
        batch_input_file = self.client.files.create(
            file=open(file_path, "rb"),
            purpose="batch"
        )
        return batch_input_file
    
    def list_files(self) -> List[FileObject]:
        files = self.client.files.list(purpose = "batch")
        return files

    def create_batch(self, file: FileObject) -> Batch:
        batch = self.client.batches.create(
            input_file_id=file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )

        return batch
    
    def list_batches(self) -> List[Batch]:
        batches = self.client.batches.list()
        return batches
    
    def retrieve_batch_status(self, batch: Optional[Batch]):
        if isinstance(batch, Batch):
            id = batch.id
        elif isinstance(batch, str):
            id = batch
        batch = self.client.batches.retrieve(id)
        status = batch.status
        count = batch.request_counts.total

        bar = tqdm(total=count, desc="Batch Progress", position=0, leave=True)
        while status != "completed":
            batch = self.client.batches.retrieve(id)
            status = batch.status
            if status == "failed":
                self.logger.warning("Batch failed")
                break
            current_count = batch.request_counts.completed
            bar.n = current_count
            bar.refresh()
            time.sleep(5)
        bar.close()

        return batch

    def retrieve_batch_results(self, batch: Optional[Batch], retrive_path:str = ".") -> bool:
        def clean_and_decode_json(content: str):
            # 去除转义字符
            content = re.sub(r'\"', '"', content)  # 去掉转义的引号
            try:
                # 解析JSON对象
                return json.loads(content)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to decode JSON content: {e}")
                return None
        os.makedirs(retrive_path, exist_ok=True)
        if isinstance(batch, str):
            batch = self.client.batches.retrieve(batch)
        if batch.error_file_id is not None:
            faild_file_content = self.client.files.content(batch.error_file_id).text
            with jsonlines.open(os.path.join(retrive_path, batch.error_file_id+".jsonl"), "w") as writer:
                content_str = json.loads(faild_file_content)
                list = content_str.split("\n")
                writer.write_all([clean_and_decode_json(i) for i in list])
                self.logger.info("Failed file content saved to: " + os.path.join(retrive_path, batch.error_file_id+".jsonl"))
            return False
        elif batch.output_file_id is not None:
            output_file_content = self.client.files.content(batch.output_file_id).text
            with jsonlines.open(os.path.join(retrive_path, batch.output_file_id+".jsonl"), "w") as writer:
                content_str = json.loads(output_file_content)
                list = content_str.split("\n")
                writer.write_all([clean_and_decode_json(i) for i in list])
                self.logger.info("Output file content saved to: " + os.path.join(retrive_path, batch.output_file_id+".jsonl"))
            return True
        else:
            self.logger.error("check whether the batch is completed")
            return False
    
    def extract_content_from_response(self, source_jsonl_path:str, target_jsonl_path:str) -> bool:
        error_count = 0
        os.makedirs(target_jsonl_path, exist_ok=True)
        file_name = os.path.basename(source_jsonl_path)
        target_jsonl_path = os.path.join(target_jsonl_path, "_"+file_name)
        with jsonlines.open(source_jsonl_path) as reader:
            with jsonlines.open(target_jsonl_path, "w") as writer:
                for obj in reader:
                    try:
                        content = json.loads(obj['response']['body']['choices'][0]['message']['content'])
                        writer.write(content)
                    except Exception as e:
                        self.logger.info(f"Failed to load json: {obj['response']['body']['choices'][0]['message']['content']}")
                        error_count += 1
        self.logger.info(f"Extracted content saved to: {target_jsonl_path}")
        self.logger.error(f"Failed to extract content from {error_count} responses")
        return True     
    
if __name__ == "__main__":
    batcher = OpeAIBatcher(base_url="", api_key="")
    #TODO build and save example.jsonl file

    # upload
    input_file = batcher.file_upload("example.jsonl")

    # create batch
    batch = batcher.create_batch(input_file)

    # show batch status
    batcher.retrieve_batch_status(batch)

    # retrieve batch results
    batcher.retrieve_batch_results(batch, retrive_path="output")

    # extract content from response
    batcher.extract_content_from_response("output/"+batch.output_file_id+".jsonl", "output")



    
