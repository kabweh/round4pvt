"""
Test module for upload handlers in the AI Tutor application.
Tests image, PDF, and DOCX upload and processing functionality.
"""
import os
import pytest
import tempfile
from PIL import Image
import io

from upload_handlers import UploadManager, ImageHandler, PDFHandler, DOCXHandler

class TestImageHandler:
    """Tests for the ImageHandler class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.image_handler = ImageHandler(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Remove test files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_save_image(self):
        """Test saving an image file."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        # Save the image
        filename = "test_image.jpg"
        file_path = self.image_handler.save_image(img_io, filename)
        
        # Check if file exists
        assert os.path.exists(file_path)
        assert os.path.basename(file_path) == filename
    
    def test_extract_text(self):
        """Test extracting text from an image."""
        # This test is limited since we can't easily create an image with text
        # In a real test environment, you would use a known image with text
        
        # Create a test image
        img = Image.new('RGB', (100, 100), color='white')
        img_path = os.path.join(self.temp_dir, "test_extract.jpg")
        img.save(img_path)
        
        # Extract text (will likely be empty, but should not error)
        text = self.image_handler.extract_text(img_path)
        
        # Just check that it returns a string without error
        assert isinstance(text, str)
    
    def test_process_image(self):
        """Test the complete image processing workflow."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='blue')
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        # Process the image
        filename = "test_process.png"
        file_path, extracted_text = self.image_handler.process_image(img_io, filename)
        
        # Check results
        assert os.path.exists(file_path)
        assert os.path.basename(file_path) == filename
        assert isinstance(extracted_text, str)

class TestPDFHandler:
    """Tests for the PDFHandler class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.pdf_handler = PDFHandler(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Remove test files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_save_pdf(self):
        """Test saving a PDF file."""
        # Create a mock PDF file
        pdf_content = b"%PDF-1.5\n%Test PDF content"
        pdf_io = io.BytesIO(pdf_content)
        
        # Save the PDF
        filename = "test_document.pdf"
        file_path = self.pdf_handler.save_pdf(pdf_io, filename)
        
        # Check if file exists
        assert os.path.exists(file_path)
        assert os.path.basename(file_path) == filename
        
        # Check file content
        with open(file_path, 'rb') as f:
            content = f.read()
            assert content == pdf_content
    
    def test_process_pdf(self):
        """Test the complete PDF processing workflow."""
        # Create a mock PDF file
        pdf_content = b"%PDF-1.5\n%Test PDF content"
        pdf_io = io.BytesIO(pdf_content)
        
        # Process the PDF
        filename = "test_process.pdf"
        file_path, extracted_text = self.pdf_handler.process_pdf(pdf_io, filename)
        
        # Check results
        assert os.path.exists(file_path)
        assert os.path.basename(file_path) == filename
        assert isinstance(extracted_text, str)

class TestDOCXHandler:
    """Tests for the DOCXHandler class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.docx_handler = DOCXHandler(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Remove test files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_save_docx(self):
        """Test saving a DOCX file."""
        # Create a mock DOCX file
        docx_content = b"PK\x03\x04\x14\x00\x00\x00\x00\x00"  # Minimal DOCX header
        docx_io = io.BytesIO(docx_content)
        
        # Save the DOCX
        filename = "test_document.docx"
        file_path = self.docx_handler.save_docx(docx_io, filename)
        
        # Check if file exists
        assert os.path.exists(file_path)
        assert os.path.basename(file_path) == filename
        
        # Check file content
        with open(file_path, 'rb') as f:
            content = f.read()
            assert content == docx_content

class TestUploadManager:
    """Tests for the UploadManager class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.upload_manager = UploadManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Remove test files
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)
    
    def test_process_image_upload(self):
        """Test processing an image upload."""
        # Create a test image
        img = Image.new('RGB', (100, 100), color='green')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        # Process the upload
        file_info = self.upload_manager.process_upload(img_io, "test_upload.jpg")
        
        # Check results
        assert file_info["success"] is True
        assert file_info["file_type"] == "image"
        assert file_info["original_filename"] == "test_upload.jpg"
        assert os.path.exists(file_info["file_path"])
    
    def test_process_unsupported_file(self):
        """Test processing an unsupported file type."""
        # Create a mock file with unsupported extension
        file_content = b"Test content"
        file_io = io.BytesIO(file_content)
        
        # Process the upload
        file_info = self.upload_manager.process_upload(file_io, "test.xyz")
        
        # Check results
        assert file_info["success"] is False
        assert "Unsupported file type" in file_info["error"]
    
    def test_get_file_path(self):
        """Test getting the file path for a saved file."""
        # Create and process a test image
        img = Image.new('RGB', (50, 50), color='black')
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        file_info = self.upload_manager.process_upload(img_io, "path_test.png")
        
        # Get file path
        retrieved_path = self.upload_manager.get_file_path(
            file_info["saved_filename"], 
            file_info["file_type"]
        )
        
        # Check results
        assert retrieved_path == file_info["file_path"]
        
        # Test invalid file type
        invalid_path = self.upload_manager.get_file_path("filename.txt", "invalid_type")
        assert invalid_path is None
