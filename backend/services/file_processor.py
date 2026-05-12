import logging
from typing import List
from fastapi import UploadFile
from sqlalchemy.orm import Session
from schemas.log import LogCreate
from services.log_parser import parse_log_line, parse_csv_content, parse_json_content
from repositories.log_repository import LogRepository
from database import SessionLocal

logger = logging.getLogger(__name__)

# 10MB chunk size for reading large files
CHUNK_SIZE = 10 * 1024 * 1024

async def process_log_file_async(file: UploadFile, db_session_factory) -> int:
    """
    Background task to process a log file asynchronously.
    Reads file in chunks to handle large files >10MB without OOM.
    """
    total_inserted = 0
    filename = file.filename.lower()
    
    content = ""
    while chunk := await file.read(CHUNK_SIZE):
        content += chunk.decode('utf-8', errors='replace')
    
    db = db_session_factory()
    try:
        repo = LogRepository(db)
        parsed_logs: List[LogCreate] = []
        
        if filename.endswith(".json"):
            parsed_logs = parse_json_content(content)
        elif filename.endswith(".csv"):
            parsed_logs = parse_csv_content(content)
        else:
            for line in content.splitlines():
                if line.strip():
                    log_entry = parse_log_line(line)
                    if log_entry:
                        parsed_logs.append(log_entry)
        
        if parsed_logs:
            batch_size = 5000
            for i in range(0, len(parsed_logs), batch_size):
                batch = parsed_logs[i:i + batch_size]
                inserted = repo.batch_insert(batch)
                total_inserted += inserted
                logger.info(f"Inserted batch of {inserted} logs.")
                
        logger.info(f"Finished processing {filename}. Total inserted: {total_inserted}")
    except Exception as e:
        logger.error(f"Error processing file {filename}: {e}", exc_info=True)
    finally:
        db.close()
        
    return total_inserted
