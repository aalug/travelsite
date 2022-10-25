"""
Test fpr models.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from accounts import models


class ModelTest(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful"""
        email = 'test@example.com'
        password = 'testpass123'
        username = 'TestUsername'
        user = get_user_model().objects.create_user(
            email=email,
            username=username,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            username = email[:5]
            user = get_user_model().objects.create_user(email, username, 'password123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raise_error(self):
        """Test that creating a user without an email raises a ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'SomeUsername', 'password123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            email='test@example.com',
            username='userNAME',
            password='admin123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_user_profile_after_user(self):
        """Test creating a user profile automatically after creating a user."""
        user = get_user_model().objects.create_user(
            email='test2@example.com',
            username='TestUsername',
            password='testpass123'
        )
        self.assertTrue(user.user_profile)

