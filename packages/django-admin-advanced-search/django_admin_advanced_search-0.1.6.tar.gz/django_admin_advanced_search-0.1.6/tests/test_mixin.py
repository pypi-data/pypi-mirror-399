"""Tests for the AdvancedSearchMixin."""

from django.test import TestCase
from django.contrib.admin import ModelAdmin
from django_admin_advanced_search.mixins import AdvancedSearchMixin


class BookAdmin(AdvancedSearchMixin, ModelAdmin):
    """Mock admin class for testing."""
    search_fields = ['title', 'author__name']
    
    def __init__(self):
        # Mock model and admin site for testing
        from django.contrib.admin.sites import AdminSite
        from django.db import models
        
        class MockModel(models.Model):
            title = models.CharField(max_length=100)
            author = models.CharField(max_length=100)  # Simplified for testing
            
            class Meta:
                app_label = 'test_app'
        
        super().__init__(MockModel, AdminSite())


class AdvancedSearchMixinTest(TestCase):
    """Test cases for AdvancedSearchMixin."""
    
    def test_contains_search(self):
        """Test case-insensitive contains search."""
        admin = BookAdmin()
        # Test field:value (case-insensitive contains)
        result = admin._parse_advanced_search('title:python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'python'))
    
    def test_exact_search(self):
        """Test case-insensitive exact search."""
        admin = BookAdmin()
        # Test field:=value (case-insensitive exact)
        result = admin._parse_advanced_search('title:=python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('iexact', 'python'))
    
    def test_exact_case_search(self):
        """Test case-sensitive exact search."""
        admin = BookAdmin()
        # Test field:==value (case-sensitive exact)
        result = admin._parse_advanced_search('title:==Python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('exact', 'Python'))
    
    def test_contains_case_search(self):
        """Test case-sensitive contains search."""
        admin = BookAdmin()
        # Test field:!value (case-sensitive contains)
        result = admin._parse_advanced_search('title:!Python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('contains', 'Python'))
    
    def test_endswith_search(self):
        """Test case-insensitive endswith search."""
        admin = BookAdmin()
        # Test field:*suffix (case-insensitive endswith)
        result = admin._parse_advanced_search('title:*programming')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('iendswith', 'programming'))
    
    def test_endswith_case_search(self):
        """Test case-sensitive endswith search."""
        admin = BookAdmin()
        # Test field:!*suffix (case-sensitive endswith)
        result = admin._parse_advanced_search('title:!*Programming')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('endswith', 'Programming'))
    
    def test_startswith_search(self):
        """Test case-insensitive startswith search."""
        admin = BookAdmin()
        # Test field:prefix* (case-insensitive startswith)
        result = admin._parse_advanced_search('title:python*')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('istartswith', 'python'))
    
    def test_startswith_case_search(self):
        """Test case-sensitive startswith search."""
        admin = BookAdmin()
        # Test field:!prefix* (case-sensitive startswith)
        result = admin._parse_advanced_search('title:!Python*')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('startswith', 'Python'))
    
    def test_related_field_search(self):
        """Test search on related fields."""
        admin = BookAdmin()
        # Test author__name:john* (related field startswith)
        result = admin._parse_advanced_search('author__name:john*')
        self.assertTrue(result['has_advanced'])
        self.assertIn('author__name', result['filters'])
        self.assertEqual(result['filters']['author__name'], ('istartswith', 'john'))
    
    def test_quoted_values_search(self):
        """Test search with quoted values."""
        admin = BookAdmin()
        # Test quoted values
        result = admin._parse_advanced_search('title:"Python Programming"')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'Python Programming'))
    
    def test_multiple_conditions(self):
        """Test multiple conditions combination."""
        admin = BookAdmin()
        # Test multiple conditions
        result = admin._parse_advanced_search('title:python author__name:john')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertIn('author__name', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'python'))
        self.assertEqual(result['filters']['author__name'], ('icontains', 'john'))
    
    def test_combined_advanced_and_plain_text(self):
        """Test combination of advanced search and plain text."""
        admin = BookAdmin()
        # Test combination of advanced search and plain text
        result = admin._parse_advanced_search('title:=Python lisa')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('iexact', 'Python'))
        self.assertEqual(result['plain_text'], 'lisa')
    
    def test_combined_search_integration(self):
        """Test integration of advanced search with plain text search."""
        # This test verifies that the mixin can be instantiated without errors
        admin = BookAdmin()
        self.assertIsNotNone(admin)
    

    
