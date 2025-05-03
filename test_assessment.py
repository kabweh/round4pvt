"""
Test module for assessment and reporting functionality in the AI Tutor application.
Tests quiz generation, database operations, and report generation.
"""
import os
import pytest
import tempfile
import json
import sqlite3
from unittest.mock import MagicMock, patch
import datetime

from assessment import Database, QuizGenerator, ReportGenerator, QuizComponent, ReportComponent

class TestDatabase:
    """Tests for the Database class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Use in-memory SQLite database for testing
        self.db = Database(":memory:")
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        self.db.close_connection()
    
    def test_add_user(self):
        """Test adding a user to the database."""
        # Add a test user
        user_id = self.db.add_user("testuser", "hashed_password", "test@example.com")
        
        # Check if user was added successfully
        assert user_id > 0
        
        # Try to add the same user again (should fail)
        duplicate_id = self.db.add_user("testuser", "another_password", "another@example.com")
        assert duplicate_id == -1
    
    def test_get_user_by_username(self):
        """Test retrieving a user by username."""
        # Add a test user
        self.db.add_user("getuser", "hashed_password", "get@example.com")
        
        # Retrieve the user
        user = self.db.get_user_by_username("getuser")
        
        # Check user data
        assert user is not None
        assert user['username'] == "getuser"
        assert user['password_hash'] == "hashed_password"
        assert user['email'] == "get@example.com"
        
        # Try to get a non-existent user
        nonexistent = self.db.get_user_by_username("nonexistent")
        assert nonexistent is None
    
    def test_create_quiz(self):
        """Test creating a quiz."""
        # Create a test quiz
        quiz_id = self.db.create_quiz("Test Quiz", "Test material", 1)
        
        # Check if quiz was created successfully
        assert quiz_id > 0
        
        # Add a question to the quiz
        question_id = self.db.add_question(
            quiz_id,
            "What is the answer?",
            "multiple_choice",
            "The answer",
            json.dumps(["The answer", "Wrong 1", "Wrong 2"])
        )
        
        # Check if question was added successfully
        assert question_id > 0
        
        # Get the quiz with questions
        quiz = self.db.get_quiz_with_questions(quiz_id)
        
        # Check quiz data
        assert quiz is not None
        assert quiz['title'] == "Test Quiz"
        assert quiz['source_material'] == "Test material"
        assert len(quiz['questions']) == 1
        assert quiz['questions'][0]['question_text'] == "What is the answer?"
    
    def test_quiz_attempt(self):
        """Test quiz attempt workflow."""
        # Create a test quiz
        quiz_id = self.db.create_quiz("Attempt Quiz", "Test material", 1)
        
        # Add a question
        question_id = self.db.add_question(
            quiz_id,
            "Test question?",
            "multiple_choice",
            "Correct",
            json.dumps(["Correct", "Wrong"])
        )
        
        # Start a quiz attempt
        attempt_id = self.db.start_quiz_attempt(quiz_id, 1)
        assert attempt_id > 0
        
        # Record a response
        response_id = self.db.record_question_response(
            attempt_id,
            question_id,
            "Correct",
            True
        )
        assert response_id > 0
        
        # Complete the attempt
        result = self.db.complete_quiz_attempt(attempt_id, 1, 1)
        assert result is True
        
        # Get quiz history
        history = self.db.get_user_quiz_history(1)
        assert len(history) > 0
        assert history[0]['quiz_id'] == quiz_id
        assert history[0]['score'] == 1

class TestQuizGenerator:
    """Tests for the QuizGenerator class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.quiz_generator = QuizGenerator()
    
    def test_preprocess_content(self):
        """Test content preprocessing."""
        # Test with special characters and whitespace
        content = "This is a test.\n\nIt has special @#$% characters and   extra   spaces."
        processed = self.quiz_generator._preprocess_content(content)
        
        # Check if special characters are removed and whitespace is normalized
        assert "@#$%" not in processed
        assert "  " not in processed
        assert "This is a test" in processed
    
    def test_extract_key_facts(self):
        """Test extracting key facts from content."""
        # Create test content with facts
        content = "The Earth is the third planet from the Sun. It has one natural satellite called the Moon. Water covers about 71% of the Earth's surface."
        
        facts = self.quiz_generator._extract_key_facts(content)
        
        # Check if facts were extracted
        assert len(facts) > 0
        assert any("Earth" in fact for fact in facts)
    
    def test_generate_quiz(self):
        """Test generating a complete quiz."""
        # Create test content
        content = """
        The water cycle is the process by which water circulates between the Earth's oceans, atmosphere, and land.
        It involves evaporation, condensation, and precipitation.
        Evaporation occurs when the sun heats water in rivers, lakes, and oceans, turning it into vapor.
        Condensation happens when water vapor cools and forms clouds.
        Precipitation occurs when water droplets in clouds become too heavy and fall as rain, snow, or hail.
        """
        
        # Generate a quiz
        quiz = self.quiz_generator.generate_quiz(content, "Water Cycle Quiz", 5)
        
        # Check quiz structure
        assert quiz["title"] == "Water Cycle Quiz"
        assert "water cycle" in quiz["source_material"].lower()
        assert len(quiz["questions"]) == 5
        
        # Check question structure
        for question in quiz["questions"]:
            assert "question_text" in question
            assert "question_type" in question
            assert "correct_answer" in question
            assert question["question_type"] in ["multiple_choice", "short_answer"]
            
            if question["question_type"] == "multiple_choice":
                options = json.loads(question["options"])
                assert len(options) > 1
                assert question["correct_answer"] in options

class TestReportGenerator:
    """Tests for the ReportGenerator class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.template_dir = tempfile.mkdtemp()
        self.report_generator = ReportGenerator(self.temp_dir, self.template_dir)
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Remove test files
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)
        
        for root, dirs, files in os.walk(self.template_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.template_dir)
    
    def test_create_default_templates(self):
        """Test creation of default templates."""
        # Check if template file was created
        template_path = os.path.join(self.template_dir, "progress_report.html")
        assert os.path.exists(template_path)
        
        # Check template content
        with open(template_path, 'r') as f:
            content = f.read()
            assert "<!DOCTYPE html>" in content
            assert "{{ report_title }}" in content
    
    def test_prepare_report_data(self):
        """Test preparing data for a report."""
        # Create test user data
        user_data = {
            "username": "testuser",
            "id": 1
        }
        
        # Create test quiz attempts
        quiz_attempts = [
            {
                "id": 1,
                "quiz_id": 1,
                "quiz_title": "Test Quiz 1",
                "score": 8,
                "max_score": 10,
                "completed_at": datetime.datetime.now().isoformat()
            },
            {
                "id": 2,
                "quiz_id": 2,
                "quiz_title": "Test Quiz 2",
                "score": 7,
                "max_score": 10,
                "completed_at": datetime.datetime.now().isoformat()
            }
        ]
        
        # Prepare report data
        report_data = self.report_generator.prepare_report_data(user_data, quiz_attempts)
        
        # Check report data
        assert report_data["student_name"] == "testuser"
        assert report_data["total_quizzes"] == 2
        assert report_data["average_score"] == 75.0  # (80% + 70%) / 2
        assert len(report_data["quiz_results"]) == 2
        assert "improvement_areas" in report_data
    
    @patch('assessment.report_generator.weasyprint')
    def test_generate_pdf_report(self, mock_weasyprint):
        """Test generating a PDF report."""
        # Setup mock
        mock_html = MagicMock()
        mock_weasyprint.HTML.return_value = mock_html
        
        # Create test report data
        report_data = {
            "report_title": "Test Report",
            "student_name": "testuser",
            "report_period": "Last 30 days",
            "generation_date": "April 26, 2025",
            "total_quizzes": 2,
            "average_score": 75.0,
            "quiz_results": [],
            "improvement_areas": ["Focus on improving understanding of science concepts."],
            "trend_description": "improved",
            "trend_period": "month",
            "current_year": 2025
        }
        
        # Generate PDF report
        pdf_path = self.report_generator.generate_pdf_report(report_data)
        
        # Check if HTML was generated
        html_path = pdf_path.replace('.pdf', '.html')
        assert os.path.exists(html_path)
        
        # Check if weasyprint was called
        mock_weasyprint.HTML.assert_called_once_with(filename=html_path)
        mock_html.write_pdf.assert_called_once()

class TestQuizComponent:
    """Tests for the QuizComponent class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.quiz_generator = MagicMock()
        self.database = MagicMock()
        self.quiz_component = QuizComponent(self.quiz_generator, self.database)
        
        # Save original session state and create a mock one
        self.original_session_state = getattr(self.quiz_component, 'st', None)
        mock_session_state = MagicMock()
        mock_session_state.current_quiz = None
        mock_session_state.quiz_attempt_id = None
        mock_session_state.quiz_responses = {}
        mock_session_state.quiz_results = None
        self.quiz_component.st = mock_session_state
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Restore original session state
        if self.original_session_state:
            self.quiz_component.st = self.original_session_state
    
    def test_get_quiz_history(self):
        """Test getting quiz history."""
        # Setup mock
        expected_history = [{"id": 1, "quiz_title": "Test Quiz"}]
        self.database.get_user_quiz_history.return_value = expected_history
        
        # Get quiz history
        history = self.quiz_component.get_quiz_history(1)
        
        # Check if database was called correctly
        self.database.get_user_quiz_history.assert_called_once_with(1)
        
        # Check result
        assert history == expected_history

class TestReportComponent:
    """Tests for the ReportComponent class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.report_generator = MagicMock()
        self.database = MagicMock()
        self.report_component = ReportComponent(self.report_generator, self.database)
    
    def test_get_user_reports(self):
        """Test getting user reports."""
        # Setup mock
        expected_reports = [{"id": 1, "title": "Test Report"}]
        self.database.get_user_progress_reports.return_value = expected_reports
        
        # Get user reports
        reports = self.report_component.get_user_reports(1)
        
        # Check if database was called correctly
        self.database.get_user_progress_reports.assert_called_once_with(1)
        
        # Check result
        assert reports == expected_reports
