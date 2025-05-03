"""
Test module for text-to-speech functionality in the AI Tutor application.
Tests TTS conversion and audio player components.
"""
import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch

from tts import TextToSpeech, TTSComponent

class TestTextToSpeech:
    """Tests for the TextToSpeech class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.tts = TextToSpeech(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Remove test files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    @patch('tts.text_to_speech.gTTS')
    def test_generate_speech(self, mock_gtts):
        """Test speech generation functionality."""
        # Setup mock
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        # Test with sample text
        result = self.tts.generate_speech("This is a test", "en", False)
        
        # Check if gTTS was called correctly
        mock_gtts.assert_called_once_with(text="This is a test", lang="en", slow=False)
        mock_tts_instance.save.assert_called_once()
        
        # Check result
        assert result["success"] is True
        assert result["file_path"].startswith(self.temp_dir)
        assert result["file_path"].endswith(".mp3")
        assert result["error"] is None
    
    @patch('tts.text_to_speech.gTTS')
    def test_generate_speech_error(self, mock_gtts):
        """Test speech generation with error."""
        # Setup mock to raise an exception
        mock_gtts.side_effect = Exception("Test error")
        
        # Test with sample text
        result = self.tts.generate_speech("This is a test")
        
        # Check result
        assert result["success"] is False
        assert result["file_path"] is None
        assert result["error"] == "Test error"
    
    @patch('tts.text_to_speech.gTTS')
    def test_generate_speech_for_explanation(self, mock_gtts):
        """Test speech generation for explanations."""
        # Setup mock
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        # Test with short explanation
        short_text = "This is a short explanation."
        result = self.tts.generate_speech_for_explanation(short_text)
        
        # Check if gTTS was called correctly
        mock_gtts.assert_called_with(text=short_text, lang="en", slow=False)
        assert result["success"] is True
        
        # Reset mock
        mock_gtts.reset_mock()
        
        # Test with long explanation (over 5000 chars)
        long_text = "A" * 5100 + ". B" * 100
        result = self.tts.generate_speech_for_explanation(long_text)
        
        # Should have been called with a chunk of the text
        mock_gtts.assert_called()
        assert result["success"] is True
    
    def test_get_audio_url(self):
        """Test getting audio URL."""
        # Test with valid filename
        filename = "test.mp3"
        url = self.tts.get_audio_url(filename)
        assert url == f"/{self.temp_dir}/{filename}"
        
        # Test with None filename
        url = self.tts.get_audio_url(None)
        assert url is None

class TestTTSComponent:
    """Tests for the TTSComponent class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.tts_handler = MagicMock()
        self.tts_component = TTSComponent(self.tts_handler)
        
        # Save original session state and create a mock one
        self.original_session_state = getattr(self.tts_component, 'st', None)
        mock_session_state = MagicMock()
        mock_session_state.current_audio = None
        self.tts_component.st = mock_session_state
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Restore original session state
        if self.original_session_state:
            self.tts_component.st = self.original_session_state
    
    def test_generate_audio_for_text(self):
        """Test generating audio for text."""
        # Setup mock
        expected_result = {"success": True, "file_path": "/path/to/audio.mp3"}
        self.tts_handler.generate_speech_for_explanation.return_value = expected_result
        
        # Test with sample text
        text = "This is a test"
        result = self.tts_component.generate_audio_for_text(text)
        
        # Check if handler was called correctly
        self.tts_handler.generate_speech_for_explanation.assert_called_once_with(text)
        
        # Check result
        assert result == expected_result
