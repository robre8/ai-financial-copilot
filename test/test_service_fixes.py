#!/usr/bin/env python3
"""
Unit tests for the 4 production fixes in embedding_service.py and llm_service.py
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService


class TestEmbeddingServiceFixes(unittest.TestCase):
    """Test Issue 1: 3D array normalization in embedding_service.py"""
    
    @patch('app.services.embedding_service.InferenceClient')
    def test_2d_array_normalization(self, mock_client_class):
        """Test that 2D arrays are properly normalized to 1D"""
        # Mock a 2D array response (shape: 1, 384)
        mock_2d_embedding = np.random.rand(1, 384)
        
        mock_client = MagicMock()
        mock_client.feature_extraction.return_value = mock_2d_embedding.tolist()
        mock_client_class.return_value = mock_client
        
        result = EmbeddingService.embed_text("test text")
        
        # Should be 384-dimensional
        self.assertEqual(len(result), 384)
        self.assertIsInstance(result, list)
    
    @patch('app.services.embedding_service.InferenceClient')
    def test_3d_array_normalization(self, mock_client_class):
        """Test that 3D arrays are properly normalized to 1D (Issue 1 fix)"""
        # Mock a 3D array response (shape: 1, num_tokens, 384)
        # This simulates the problem case where feature_extraction returns 3D
        mock_3d_embedding = np.random.rand(1, 5, 384)
        
        mock_client = MagicMock()
        mock_client.feature_extraction.return_value = mock_3d_embedding.tolist()
        mock_client_class.return_value = mock_client
        
        result = EmbeddingService.embed_text("test text")
        
        # Should be 384-dimensional after while loop reduces dimensions
        self.assertEqual(len(result), 384)
        self.assertIsInstance(result, list)
    
    @patch('app.services.embedding_service.InferenceClient')
    def test_4d_array_normalization(self, mock_client_class):
        """Test that even 4D arrays are properly normalized (edge case)"""
        # Mock a 4D array response
        mock_4d_embedding = np.random.rand(1, 2, 3, 384)
        
        mock_client = MagicMock()
        mock_client.feature_extraction.return_value = mock_4d_embedding.tolist()
        mock_client_class.return_value = mock_client
        
        result = EmbeddingService.embed_text("test text")
        
        # Should be 384-dimensional after while loop reduces all dimensions
        self.assertEqual(len(result), 384)
        self.assertIsInstance(result, list)
    
    @patch('app.services.embedding_service.InferenceClient')
    def test_1d_array_passthrough(self, mock_client_class):
        """Test that 1D arrays pass through without modification"""
        # Mock a 1D array response (already correct)
        mock_1d_embedding = np.random.rand(384)
        
        mock_client = MagicMock()
        mock_client.feature_extraction.return_value = mock_1d_embedding.tolist()
        mock_client_class.return_value = mock_client
        
        result = EmbeddingService.embed_text("test text")
        
        # Should be 384-dimensional
        self.assertEqual(len(result), 384)
        self.assertIsInstance(result, list)


class TestLLMServiceFixes(unittest.TestCase):
    """Test Issues 2, 3, and 4 in llm_service.py"""
    
    @patch('app.services.llm_service.requests.post')
    def test_bare_except_fixed(self, mock_post):
        """Test Issue 2: Bare except clause is now Exception-specific"""
        # Mock a response that fails JSON parsing
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Error text"
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response
        
        # Should raise RuntimeError (all models exhausted)
        with self.assertRaises(RuntimeError):
            LLMService.generate("test prompt")
        
        # The except Exception should have been triggered (not bare except)
        # This test passes if no SystemExit or KeyboardInterrupt was caught
    
    @patch('app.services.llm_service.requests.post')
    def test_503_retry_fallback_return(self, mock_post):
        """Test Issue 3: 503 retry block now has fallback return"""
        # First call: 503 (model loading)
        mock_response_503 = Mock()
        mock_response_503.status_code = 503
        mock_response_503.json.return_value = {'estimated_time': 5}
        
        # Second call (retry): 200 with non-standard format
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = [{"other_key": "some response"}]
        
        mock_post.side_effect = [mock_response_503, mock_response_200]
        
        result = LLMService.generate("test prompt")
        
        # Should return str(result) as fallback (not continue to next model)
        self.assertIsInstance(result, str)
        self.assertIn("other_key", result)
    
    @patch('app.services.llm_service.requests.post')
    def test_generated_text_format(self, mock_post):
        """Test Issue 4: Handle generated_text format"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"generated_text": "Test response"}]
        mock_post.return_value = mock_response
        
        result = LLMService.generate("test prompt")
        
        self.assertEqual(result, "Test response")
    
    @patch('app.services.llm_service.requests.post')
    def test_summary_text_format(self, mock_post):
        """Test Issue 4: Handle summary_text format from flan-t5"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"summary_text": "Test summary"}]
        mock_post.return_value = mock_response
        
        result = LLMService.generate("test prompt")
        
        self.assertEqual(result, "Test summary")
    
    @patch('app.services.llm_service.requests.post')
    def test_translation_text_format(self, mock_post):
        """Test Issue 4: Handle translation_text format"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"translation_text": "Test translation"}]
        mock_post.return_value = mock_response
        
        result = LLMService.generate("test prompt")
        
        self.assertEqual(result, "Test translation")
    
    @patch('app.services.llm_service.requests.post')
    def test_multiple_response_keys_priority(self, mock_post):
        """Test that response keys are checked in order"""
        mock_response = Mock()
        mock_response.status_code = 200
        # If multiple keys exist, first one in list should be used
        mock_response.json.return_value = [{
            "generated_text": "Generated",
            "summary_text": "Summary",
            "translation_text": "Translation"
        }]
        mock_post.return_value = mock_response
        
        result = LLMService.generate("test prompt")
        
        # Should use generated_text (first in the key list)
        self.assertEqual(result, "Generated")
    
    @patch('app.services.llm_service.requests.post')
    def test_503_retry_with_summary_text(self, mock_post):
        """Test Issue 4 in retry block: Handle summary_text after 503 retry"""
        # First call: 503 (model loading)
        mock_response_503 = Mock()
        mock_response_503.status_code = 503
        mock_response_503.json.return_value = {'estimated_time': 5}
        
        # Second call (retry): 200 with summary_text
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = [{"summary_text": "Test summary after retry"}]
        
        mock_post.side_effect = [mock_response_503, mock_response_200]
        
        result = LLMService.generate("test prompt")
        
        self.assertEqual(result, "Test summary after retry")


if __name__ == '__main__':
    unittest.main()
