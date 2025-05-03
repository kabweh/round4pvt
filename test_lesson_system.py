"""
Test module for lesson system in the AI Tutor application.
Tests lesson explanation generation and UI components.
"""
import pytest
from unittest.mock import MagicMock

from lesson_system import LessonExplainer, ExplanationComponent

class TestLessonExplainer:
    """Tests for the LessonExplainer class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.explainer = LessonExplainer()
    
    def test_preprocess_text(self):
        """Test text preprocessing functionality."""
        # Test with multiple newlines
        text = "This is a test.\n\n\n\nWith multiple newlines."
        processed = self.explainer._preprocess_text(text)
        assert processed == "This is a test.\n\nWith multiple newlines."
        
        # Test with multiple spaces
        text = "This    has    too    many    spaces."
        processed = self.explainer._preprocess_text(text)
        assert processed == "This has too many spaces."
        
        # Test with both issues
        text = "Multiple   spaces.\n\n\n\nAnd newlines."
        processed = self.explainer._preprocess_text(text)
        assert processed == "Multiple spaces.\n\nAnd newlines."
    
    def test_identify_subject(self):
        """Test subject identification functionality."""
        # Test mathematics
        math_text = "The equation x^2 + 5x + 6 = 0 can be solved using the quadratic formula."
        subject = self.explainer._identify_subject(math_text)
        assert subject == "mathematics"
        
        # Test history
        history_text = "In the 18th century, the Industrial Revolution transformed society."
        subject = self.explainer._identify_subject(history_text)
        assert subject == "history"
        
        # Test science
        science_text = "The experiment demonstrated how chemical reactions can be catalyzed."
        subject = self.explainer._identify_subject(science_text)
        assert subject == "science"
        
        # Test literature
        literature_text = "The novel's protagonist faces a moral dilemma that shapes the story."
        subject = self.explainer._identify_subject(literature_text)
        assert subject == "literature"
        
        # Test language
        language_text = "Adjectives modify nouns and provide additional information about them."
        subject = self.explainer._identify_subject(language_text)
        assert subject == "language"
        
        # Test general (no specific subject)
        general_text = "This text doesn't contain any specific subject indicators."
        subject = self.explainer._identify_subject(general_text)
        assert subject == "general"
    
    def test_generate_explanation(self):
        """Test explanation generation at different complexity levels."""
        test_text = "The water cycle is the process by which water circulates between the Earth's oceans, atmosphere, and land. It involves evaporation, condensation, and precipitation."
        
        # Test simple explanation
        simple_explanation = self.explainer.generate_explanation(test_text, "simple")
        assert "simple terms" in simple_explanation.lower()
        assert "water cycle" in simple_explanation
        
        # Test medium explanation (default)
        medium_explanation = self.explainer.generate_explanation(test_text)
        assert "water cycle" in medium_explanation
        assert len(medium_explanation) > len(simple_explanation)
        
        # Test advanced explanation
        advanced_explanation = self.explainer.generate_explanation(test_text, "advanced")
        assert "water cycle" in advanced_explanation
        assert len(advanced_explanation) > len(medium_explanation)
        
        # Test with empty text
        empty_explanation = self.explainer.generate_explanation("")
        assert "don't see any content" in empty_explanation

class TestExplanationComponent:
    """Tests for the ExplanationComponent class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.lesson_explainer = LessonExplainer()
        self.explanation_component = ExplanationComponent(self.lesson_explainer)
        
        # Mock Streamlit
        self.mock_st = MagicMock()
        
        # Save original session state and create a mock one
        self.original_session_state = getattr(self.explanation_component, 'st', None)
        mock_session_state = MagicMock()
        mock_session_state.content_to_explain = None
        mock_session_state.current_explanation = None
        mock_session_state.explanation_history = []
        self.explanation_component.st = mock_session_state
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Restore original session state
        if self.original_session_state:
            self.explanation_component.st = self.original_session_state
    
    def test_explain_content(self):
        """Test setting content to be explained."""
        # Test with sample content
        test_text = "Sample text to explain"
        test_source = "test.txt"
        
        self.explanation_component.explain_content(test_text, test_source)
        
        # Check if content was set correctly
        assert self.explanation_component.st.content_to_explain == {
            'text': test_text,
            'source': test_source
        }
    
    def test_get_current_explanation(self):
        """Test getting the current explanation."""
        # Set a mock current explanation
        mock_explanation = {
            'text': 'This is an explanation',
            'source': 'test.txt',
            'complexity': 'medium'
        }
        self.explanation_component.st.current_explanation = mock_explanation
        
        # Get the current explanation
        result = self.explanation_component.get_current_explanation()
        
        # Check if the correct explanation was returned
        assert result == mock_explanation
