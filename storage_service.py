#!/usr/bin/env python3
"""
Storage Service for CloneGallery
Handles both local file storage and S3-compatible storage (MinIO/AWS S3)
"""

import os
import io
import uuid
from typing import Optional, Tuple, BinaryIO
from PIL import Image
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import logging

logger = logging.getLogger(__name__)

class StorageService:
    """Unified storage service for local and S3 storage."""
    
    def __init__(self):
        self.storage_type = os.getenv('STORAGE_TYPE', 'local')  # 'local', 's3', 'minio'
        self.local_upload_path = os.getenv('LOCAL_UPLOAD_PATH', 'uploads')
        self.s3_bucket = os.getenv('S3_BUCKET', 'clonegallery-images')
        self.s3_thumbnail_bucket = os.getenv('S3_THUMBNAIL_BUCKET', 'clonegallery-thumbnails')
        
        # Ensure local upload directory exists
        if self.storage_type == 'local':
            os.makedirs(self.local_upload_path, exist_ok=True)
            os.makedirs(os.path.join(self.local_upload_path, 'thumbnails'), exist_ok=True)
        
        # Initialize S3 client if needed
        self.s3_client = None
        if self.storage_type in ['s3', 'minio']:
            self._init_s3_client()
    
    def _init_s3_client(self):
        """Initialize S3 client for MinIO or AWS S3."""
        try:
            if self.storage_type == 'minio':
                # MinIO configuration
                endpoint_url = os.getenv('MINIO_ENDPOINT', 'http://minio:9000')
                access_key = os.getenv('MINIO_ACCESS_KEY', 'clonegallery')
                secret_key = os.getenv('MINIO_SECRET_KEY', 'clonegallery123')
                
                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=endpoint_url,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name='us-east-1'
                )
            else:  # AWS S3
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_REGION', 'us-east-1')
                )
            
            logger.info(f"S3 client initialized for {self.storage_type}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise
    
    def _generate_file_key(self, filename: str, folder: str = 'images') -> str:
        """Generate unique file key for storage."""
        file_ext = os.path.splitext(filename)[1]
        unique_id = str(uuid.uuid4())
        return f"{folder}/{unique_id}{file_ext}"
    
    def _create_thumbnail(self, image_data: bytes, max_size: Tuple[int, int] = (300, 300)) -> bytes:
        """Create thumbnail from image data."""
        try:
            image = Image.open(io.BytesIO(image_data))
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85, optimize=True)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create thumbnail: {e}")
            return image_data  # Return original if thumbnail creation fails
    
    def upload_file(self, file_data: bytes, filename: str, content_type: str = 'image/jpeg') -> Tuple[str, str]:
        """
        Upload file and return (file_url, thumbnail_url).
        
        Args:
            file_data: Raw file data
            filename: Original filename
            content_type: MIME type
            
        Returns:
            Tuple of (file_url, thumbnail_url)
        """
        try:
            file_key = self._generate_file_key(filename, 'images')
            thumbnail_key = self._generate_file_key(filename, 'thumbnails')
            
            if self.storage_type == 'local':
                return self._upload_local(file_data, file_key, thumbnail_key, content_type)
            else:
                return self._upload_s3(file_data, file_key, thumbnail_key, content_type)
                
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise
    
    def _upload_local(self, file_data: bytes, file_key: str, thumbnail_key: str, content_type: str) -> Tuple[str, str]:
        """Upload file to local storage."""
        # Upload original file
        file_path = os.path.join(self.local_upload_path, file_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Create and upload thumbnail
        thumbnail_data = self._create_thumbnail(file_data)
        thumbnail_path = os.path.join(self.local_upload_path, thumbnail_key)
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        
        with open(thumbnail_path, 'wb') as f:
            f.write(thumbnail_data)
        
        # Return URLs (assuming web server serves from /uploads)
        file_url = f"/uploads/{file_key}"
        thumbnail_url = f"/uploads/{thumbnail_key}"
        
        return file_url, thumbnail_url
    
    def _upload_s3(self, file_data: bytes, file_key: str, thumbnail_key: str, content_type: str) -> Tuple[str, str]:
        """Upload file to S3-compatible storage."""
        try:
            # Upload original file
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=file_key,
                Body=file_data,
                ContentType=content_type,
                ACL='public-read'
            )
            
            # Create and upload thumbnail
            thumbnail_data = self._create_thumbnail(file_data)
            self.s3_client.put_object(
                Bucket=self.s3_thumbnail_bucket,
                Key=thumbnail_key,
                Body=thumbnail_data,
                ContentType='image/jpeg',
                ACL='public-read'
            )
            
            # Generate public URLs
            if self.storage_type == 'minio':
                endpoint_url = os.getenv('MINIO_ENDPOINT', 'http://minio:9000')
                file_url = f"{endpoint_url}/{self.s3_bucket}/{file_key}"
                thumbnail_url = f"{endpoint_url}/{self.s3_thumbnail_bucket}/{thumbnail_key}"
            else:  # AWS S3
                file_url = f"https://{self.s3_bucket}.s3.amazonaws.com/{file_key}"
                thumbnail_url = f"https://{self.s3_thumbnail_bucket}.s3.amazonaws.com/{thumbnail_key}"
            
            return file_url, thumbnail_url
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")
            raise
    
    def delete_file(self, file_url: str, thumbnail_url: str) -> bool:
        """Delete file and thumbnail from storage."""
        try:
            if self.storage_type == 'local':
                return self._delete_local(file_url, thumbnail_url)
            else:
                return self._delete_s3(file_url, thumbnail_url)
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False
    
    def _delete_local(self, file_url: str, thumbnail_url: str) -> bool:
        """Delete file from local storage."""
        try:
            # Extract file paths from URLs
            file_path = os.path.join(self.local_upload_path, file_url.replace('/uploads/', ''))
            thumbnail_path = os.path.join(self.local_upload_path, thumbnail_url.replace('/uploads/', ''))
            
            # Delete files if they exist
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            
            return True
        except Exception as e:
            logger.error(f"Local file deletion failed: {e}")
            return False
    
    def _delete_s3(self, file_url: str, thumbnail_url: str) -> bool:
        """Delete file from S3 storage."""
        try:
            # Extract keys from URLs
            file_key = file_url.split('/')[-2] + '/' + file_url.split('/')[-1]
            thumbnail_key = thumbnail_url.split('/')[-2] + '/' + thumbnail_url.split('/')[-1]
            
            # Delete files
            self.s3_client.delete_object(Bucket=self.s3_bucket, Key=file_key)
            self.s3_client.delete_object(Bucket=self.s3_thumbnail_bucket, Key=thumbnail_key)
            
            return True
        except ClientError as e:
            logger.error(f"S3 deletion failed: {e}")
            return False
    
    def get_file_info(self, file_url: str) -> Optional[dict]:
        """Get file information from storage."""
        try:
            if self.storage_type == 'local':
                return self._get_local_file_info(file_url)
            else:
                return self._get_s3_file_info(file_url)
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return None
    
    def _get_local_file_info(self, file_url: str) -> Optional[dict]:
        """Get local file information."""
        file_path = os.path.join(self.local_upload_path, file_url.replace('/uploads/', ''))
        
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'exists': True
        }
    
    def _get_s3_file_info(self, file_url: str) -> Optional[dict]:
        """Get S3 file information."""
        try:
            file_key = file_url.split('/')[-2] + '/' + file_url.split('/')[-1]
            response = self.s3_client.head_object(Bucket=self.s3_bucket, Key=file_key)
            
            return {
                'size': response['ContentLength'],
                'modified': response['LastModified'].timestamp(),
                'exists': True,
                'content_type': response.get('ContentType', 'application/octet-stream')
            }
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return {'exists': False}
            logger.error(f"S3 file info failed: {e}")
            return None

# Global storage service instance
storage_service = StorageService()
