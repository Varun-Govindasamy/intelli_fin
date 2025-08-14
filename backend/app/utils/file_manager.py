import os
import asyncio
import aiofiles
from typing import List
from fastapi import UploadFile
import hashlib
from datetime import datetime

class FileManager:
    def __init__(self):
        self.upload_directory = os.getenv("UPLOAD_DIRECTORY", "./data/uploads")
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", 50000000))  # 50MB
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.upload_directory, exist_ok=True)
        os.makedirs("./data/vector_store", exist_ok=True)
        os.makedirs("./data", exist_ok=True)
    
    async def save_upload(self, file: UploadFile) -> str:
        """Save uploaded file and return the file path"""
        try:
            # Check file size
            content = await file.read()
            if len(content) > self.max_file_size:
                raise ValueError(f"File too large. Maximum size is {self.max_file_size} bytes")
            
            # Reset file pointer
            await file.seek(0)
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(content).hexdigest()[:8]
            filename = f"{timestamp}_{file_hash}_{file.filename}"
            file_path = os.path.join(self.upload_directory, filename)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"Error saving file: {str(e)}")
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    async def list_uploaded_files(self) -> List[dict]:
        """List all uploaded files with metadata"""
        try:
            files = []
            for filename in os.listdir(self.upload_directory):
                file_path = os.path.join(self.upload_directory, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    files.append({
                        "filename": filename,
                        "path": file_path,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    async def cleanup_old_files(self, days: int = 7):
        """Clean up files older than specified days"""
        try:
            import time
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            deleted_count = 0
            for filename in os.listdir(self.upload_directory):
                file_path = os.path.join(self.upload_directory, filename)
                if os.path.isfile(file_path):
                    if os.path.getmtime(file_path) < cutoff_time:
                        await self.delete_file(file_path)
                        deleted_count += 1
            
            return deleted_count
        except Exception as e:
            print(f"Error cleaning up files: {e}")
            return 0
    
    def get_file_info(self, file_path: str) -> dict:
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return {"error": "File not found"}
            
            stat = os.stat(file_path)
            return {
                "filename": os.path.basename(file_path),
                "path": file_path,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
