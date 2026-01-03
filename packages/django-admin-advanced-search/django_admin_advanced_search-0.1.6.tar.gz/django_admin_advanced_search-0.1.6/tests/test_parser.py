"""Tests for the advanced search parser."""

from django.test import TestCase
from django_admin_advanced_search.parser import parse_advanced_search


class AdvancedSearchParserTest(TestCase):
    """Test cases for the advanced search parser."""
    
    def setUp(self):
        self.allowed_fields = ['title', 'author__name']
    
    def test_contains_search(self):
        """Test case-insensitive contains search."""
        # Test field:value (case-insensitive contains)
        result = parse_advanced_search('title:python', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'python'))
    
    def test_exact_search(self):
        """Test case-insensitive exact search."""
        # Test field:=value (case-insensitive exact)
        result = parse_advanced_search('title:=python', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('iexact', 'python'))
    
    def test_exact_case_search(self):
        """Test case-sensitive exact search."""
        # Test field:==value (case-sensitive exact)
        result = parse_advanced_search('title:==Python', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('exact', 'Python'))
    
    def test_contains_case_search(self):
        """Test case-sensitive contains search."""
        # Test field:!value (case-sensitive contains)
        result = parse_advanced_search('title:!Python', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('contains', 'Python'))
    
    def test_endswith_search(self):
        """Test case-insensitive endswith search."""
        # Test field:*suffix (case-insensitive endswith)
        result = parse_advanced_search('title:*programming', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('iendswith', 'programming'))
    
    def test_endswith_case_search(self):
        """Test case-sensitive endswith search."""
        # Test field:!*suffix (case-sensitive endswith)
        result = parse_advanced_search('title:!*Programming', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('endswith', 'Programming'))
    
    def test_startswith_search(self):
        """Test case-insensitive startswith search."""
        # Test field:prefix* (case-insensitive startswith)
        result = parse_advanced_search('title:python*', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('istartswith', 'python'))
    
    def test_startswith_case_search(self):
        """Test case-sensitive startswith search."""
        # Test field:!prefix* (case-sensitive startswith)
        result = parse_advanced_search('title:!Python*', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('startswith', 'Python'))
    
    def test_related_field_search(self):
        """Test search on related fields."""
        # Test author__name:john* (related field startswith)
        result = parse_advanced_search('author__name:john*', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        self.assertIn('author__name', result['filters'])
        self.assertEqual(result['filters']['author__name'], ('istartswith', 'john'))
    
    def test_quoted_values_search(self):
        """Test search with quoted values."""
        # Test quoted values
        result = parse_advanced_search('title:"Python Programming"', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'Python Programming'))
    
    def test_multiple_conditions(self):
        """Test multiple conditions combination."""
        # Test multiple conditions
        result = parse_advanced_search('title:python author__name:john', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertIn('author__name', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'python'))
        self.assertEqual(result['filters']['author__name'], ('icontains', 'john'))
    
    def test_field_whitelist_security(self):
        """Test that only whitelisted fields can be searched."""
        # Test that disallowed fields are treated as plain text
        result = parse_advanced_search('description:secret author__name:john', self.allowed_fields)
        self.assertTrue(result['has_advanced'])
        # Only author__name should be in filters, description should be in plain_text
        self.assertIn('author__name', result['filters'])
        self.assertNotIn('description', result['filters'])
        self.assertIn('description:secret', result['plain_text'])