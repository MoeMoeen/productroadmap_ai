# brain/services/validators.py

import os
import mimetypes
from typing import List, Dict, Any, Optional
from django.core.files.uploadedfile import UploadedFile

from brain.cognitive_pipeline.schema import DocumentParsingValidationResult


class FileValidator:
	"""
	Comprehensive file validation service for the Perception Layer.
	Validates file format, size, integrity, and content quality.
	"""
    
	SUPPORTED_MIME_TYPES = {
		'application/pdf',
		'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
		'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
		'application/msword',
		'text/plain',
	}
    
	MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
	MIN_FILE_SIZE = 10  # 10 bytes
    
	SECURITY_EXTENSIONS_BLOCKED = {
		'.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
		'.jar', '.app', '.deb', '.pkg', '.dmg', '.msi'
	}
    
	@classmethod
	def validate_uploaded_files(cls, files: List[UploadedFile]) -> DocumentParsingValidationResult:
		"""
		Validate a list of uploaded files before processing.
        
		Args:
			files: List of Django UploadedFile objects
        
		Returns:
			ValidationResult with overall validation status
		"""
		errors: list[str] = []
		warnings: list[str] = []
		details: dict = {}
        
		if not files:
			errors.append("No files provided for validation")
			return DocumentParsingValidationResult(
				is_valid=False,
				quality_score=0.0,
				errors=errors,
				warnings=warnings,
				details=details
			)
        
		valid_files = 0
		total_size = 0
        
		for i, file in enumerate(files):
			file_errors, file_warnings = cls._validate_single_file(file)
            
			if file_errors:
				errors.extend([f"File {i+1} ({file.name}): {error}" for error in file_errors])
			else:
				valid_files += 1
            
			if file_warnings:
				warnings.extend([f"File {i+1} ({file.name}): {warning}" for warning in file_warnings])
            
			total_size += file.size
        
		# Overall validation
		is_valid = len(errors) == 0
		quality_score = valid_files / len(files) if files else 0.0
        
		details.update({
			'total_files': len(files),
			'valid_files': valid_files,
			'total_size_bytes': total_size,
			'file_details': [cls._get_file_details(f) for f in files]
		})
        
		return DocumentParsingValidationResult(
			is_valid=is_valid,
			quality_score=quality_score,
			errors=errors,
			warnings=warnings,
			details=details
		)
    
	@classmethod
	def _validate_single_file(cls, file: UploadedFile) -> tuple[List[str], List[str]]:
		"""Validate a single uploaded file."""
		errors = []
		warnings = []
        
		# File size validation
		if file.size > cls.MAX_FILE_SIZE:
			errors.append(f"File too large: {file.size} bytes (max: {cls.MAX_FILE_SIZE})")
		elif file.size < cls.MIN_FILE_SIZE:
			errors.append(f"File too small: {file.size} bytes (min: {cls.MIN_FILE_SIZE})")
        
		# File extension security check
		file_ext = os.path.splitext(file.name)[1].lower()
		if file_ext in cls.SECURITY_EXTENSIONS_BLOCKED:
			errors.append(f"File type not allowed for security reasons: {file_ext}")
        
		# MIME type validation
		mime_type = file.content_type or mimetypes.guess_type(file.name)[0]
		if mime_type not in cls.SUPPORTED_MIME_TYPES:
			errors.append(f"Unsupported file type: {mime_type}")
        
		# File name validation
		if not file.name or file.name.strip() == "":
			errors.append("File has no name")
		elif len(file.name) > 255:
			warnings.append("File name is very long and may cause issues")
        
		# Content validation (basic)
		if hasattr(file, 'read'):
			try:
				# Read first few bytes to check if file is readable
				file.seek(0)
				first_bytes = file.read(1024)
				file.seek(0)  # Reset file pointer
                
				if not first_bytes:
					errors.append("File appears to be empty or unreadable")
                
				# Basic file signature validation
				cls._validate_file_signature(first_bytes, mime_type, errors, warnings)
                
			except Exception as e:
				errors.append(f"Cannot read file content: {e}")
        
		return errors, warnings
    
	@classmethod
	def _validate_file_signature(cls, first_bytes: bytes, mime_type: Optional[str], 
								errors: List[str], warnings: List[str]) -> None:
		"""Validate file signature matches expected format."""
		if not first_bytes or len(first_bytes) < 4:
			warnings.append("Cannot validate file signature - insufficient data")
			return
        
		# PDF signature
		if mime_type == 'application/pdf':
			if not first_bytes.startswith(b'%PDF-'):
				errors.append("File claims to be PDF but doesn't have PDF signature")
        
		# ZIP-based formats (DOCX, XLSX)
		elif mime_type in [
			'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
			'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
		]:
			if not first_bytes.startswith(b'PK'):
				errors.append("File claims to be Office format but doesn't have ZIP signature")
        
		# DOC format (older format)
		elif mime_type == 'application/msword':
			if not (first_bytes.startswith(b'\xd0\xcf\x11\xe0') or  # OLE signature
				   first_bytes.startswith(b'PK')):  # Some DOC files are ZIP-based
				warnings.append("File claims to be DOC but signature is unclear")
    
	@classmethod
	def _get_file_details(cls, file: UploadedFile) -> Dict[str, Any]:
		"""Get detailed information about a file."""
		return {
			'name': file.name,
			'size': file.size,
			'content_type': file.content_type,
			'extension': os.path.splitext(file.name)[1].lower(),
			'charset': getattr(file, 'charset', None)
		}
    
	@classmethod
	def validate_file_paths(cls, file_paths: List[str]) -> DocumentParsingValidationResult:
		"""
		Validate a list of file paths for processing.
        
		Args:
			file_paths: List of absolute file paths
        
		Returns:
			ValidationResult with path validation status
		"""
		errors: list[str] = []
		warnings: list[str] = []
		details: dict = {}
        
		if not file_paths:
			errors.append("No file paths provided")
			return DocumentParsingValidationResult(
				is_valid=False,
				quality_score=0.0,
				errors=errors,
				warnings=warnings,
				details=details
			)
        
		valid_paths = 0
		total_size = 0
        
		for i, path in enumerate(file_paths):
			path_errors, path_warnings, path_size = cls._validate_file_path(path)
            
			if path_errors:
				errors.extend([f"Path {i+1} ({path}): {error}" for error in path_errors])
			else:
				valid_paths += 1
				total_size += path_size
            
			if path_warnings:
				warnings.extend([f"Path {i+1} ({path}): {warning}" for warning in path_warnings])
        
		is_valid = len(errors) == 0
		quality_score = valid_paths / len(file_paths) if file_paths else 0.0
        
		details.update({
			'total_paths': len(file_paths),
			'valid_paths': valid_paths,
			'total_size_bytes': total_size,
			'paths': file_paths
		})
        
		return DocumentParsingValidationResult(
			is_valid=is_valid,
			quality_score=quality_score,
			errors=errors,
			warnings=warnings,
			details=details
		)
    
	@classmethod
	def _validate_file_path(cls, file_path: str) -> tuple[list[str], list[str], int]:
		"""Validate a single file path."""
		errors: list[str] = []
		warnings: list[str] = []
		file_size: int = 0

		# Path existence check
		if not os.path.exists(file_path):
			errors.append("File does not exist")
			return errors, warnings, file_size

		# Path type check
		if not os.path.isfile(file_path):
			errors.append("Path is not a file")
			return errors, warnings, file_size

		# File accessibility check
		if not os.access(file_path, os.R_OK):
			errors.append("File is not readable")
			return errors, warnings, file_size

		try:
			# File size check
			file_size = os.path.getsize(file_path)
			if file_size > cls.MAX_FILE_SIZE:
				errors.append(f"File too large: {file_size} bytes (max: {cls.MAX_FILE_SIZE})")
			elif file_size < cls.MIN_FILE_SIZE:
				errors.append(f"File too small: {file_size} bytes (min: {cls.MIN_FILE_SIZE})")

			# File extension check
			file_ext = os.path.splitext(file_path)[1].lower()
			if file_ext in cls.SECURITY_EXTENSIONS_BLOCKED:
				errors.append(f"File type not allowed for security reasons: {file_ext}")

			# MIME type check
			mime_type, _ = mimetypes.guess_type(file_path)
			if mime_type not in cls.SUPPORTED_MIME_TYPES:
				errors.append(f"Unsupported file type: {mime_type}")

		except OSError as e:
			errors.append(f"Cannot access file: {e}")

		return errors, warnings, file_size


class ContentValidator:
	"""
	Validates the quality and content of processed documents.
	"""
    
	MIN_CONTENT_LENGTH = 50  # Minimum characters for meaningful content
	MIN_QUALITY_SCORE = 0.5  # Minimum quality score to consider valid
    
	@classmethod
	def validate_processed_content(cls, content: str, file_type: str) -> DocumentParsingValidationResult:
		"""
		Validate processed document content for quality.
        
		Args:
			content: Extracted text content
			file_type: Type of the source file
            
		Returns:
			ValidationResult with content quality assessment
		"""
		errors = []
		warnings = []
		quality_score = 1.0
        
		# Content length check
		if not content or not content.strip():
			errors.append("No content extracted from document")
			quality_score = 0.0
		elif len(content.strip()) < cls.MIN_CONTENT_LENGTH:
			warnings.append("Very little content extracted - document may be mostly images or formatting")
			quality_score *= 0.7
        
		# Content quality heuristics
		if content:
			# Check for reasonable text-to-special-character ratio
			text_chars = sum(1 for c in content if c.isalnum() or c.isspace())
			special_chars = len(content) - text_chars
            
			if len(content) > 0:
				special_ratio = special_chars / len(content)
				if special_ratio > 0.5:
					warnings.append("High ratio of special characters - may indicate extraction issues")
					quality_score *= 0.8
            
			# Check for reasonable word count
			words = content.split()
			if len(words) < 10:
				warnings.append("Very few words extracted")
				quality_score *= 0.6
            
			# Check for repeated patterns (potential extraction errors)
			if len(set(words)) < len(words) * 0.3 and len(words) > 20:
				warnings.append("High word repetition detected - may indicate extraction issues")
				quality_score *= 0.8
        
		is_valid = len(errors) == 0 and quality_score >= cls.MIN_QUALITY_SCORE
        
		details = {
			'content_length': len(content) if content else 0,
			'word_count': len(content.split()) if content else 0,
			'unique_words': len(set(content.split())) if content else 0,
			'file_type': file_type
		}
        
		return DocumentParsingValidationResult(
			is_valid=is_valid,
			quality_score=quality_score,
			errors=errors,
			warnings=warnings,
			details=details
		)
