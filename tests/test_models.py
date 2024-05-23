import unittest
from app import create_app, db
from app.models.models import User, LoginHistory, Post, Reply,Notification
from config import TestingConfig
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

class BaseTestCase(unittest.TestCase):
    """Base test case for setting up the application context and database."""

    def setUp(self):
        """Set up test variables and initialize app context and database."""
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.create_test_user()

    def tearDown(self):
        """Remove session and drop all tables after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_test_user(self):
        """Create a test user."""
        user = User(username='testuser', email='test@example.com', password_hash=generate_password_hash('testpass'))
        db.session.add(user)
        db.session.commit()
    
    def create_notification(self, user):
        """Create a test notification."""
        notification = Notification(
            user_id=user.id,
            actor_id=user.id,
            message="This is a test notification",
            notification_type="mention",
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notification)
        db.session.commit()
        return notification

class ModelsTestCase(BaseTestCase):
    """Test cases for models."""

    def test_user_creation(self):
        """Test user creation and password hashing."""
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertTrue(check_password_hash(user.password_hash, 'testpass'))
        self.assertEqual(user.profile_image_url, "/static/uploads/default_user.jpg")

    def test_unique_username(self):
        """Test that the username is unique."""
        user = User(username='testuser', email='test2@example.com', password_hash=generate_password_hash('testpass'))
        db.session.add(user)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_login_history(self):
        """Test login and logout recording."""
        user = User.query.filter_by(username='testuser').first()
        login_history = LoginHistory(username='testuser', login_time=datetime.utcnow(), user_id=user.id)
        db.session.add(login_history)
        db.session.commit()
        self.assertEqual(login_history.user_id, user.id)
        self.assertIsNone(login_history.logout_time)

        # Simulate user logout
        login_history.logout_time = datetime.utcnow()
        db.session.commit()
        self.assertIsNotNone(login_history.logout_time)

    def test_post_creation(self):
        """Test post creation and relationship with user."""
        user = User.query.filter_by(username='testuser').first()
        post = Post(title='Test Post', content='This is a test post', user_id=user.id)
        db.session.add(post)
        db.session.commit()
        self.assertEqual(post.user_id, user.id)
        self.assertEqual(post.user.username, 'testuser')
        self.assertEqual(post.replies.count(), 0)

    def test_reply_creation(self):
        """Test reply creation and hierarchical relationship."""
        user = User.query.filter_by(username='testuser').first()
        post = Post(title='Test Post', content='This is a test post', user_id=user.id)
        db.session.add(post)
        db.session.commit()

        reply1 = Reply(content='This is a reply', post_id=post.id, user_id=user.id)
        db.session.add(reply1)
        db.session.commit()
        self.assertEqual(reply1.post_id, post.id)
        self.assertEqual(reply1.user_id, user.id)
        self.assertIsNone(reply1.parent_id)
        self.assertEqual(len(reply1.children), 0)

        reply2 = Reply(content='This is a child reply', post_id=post.id, user_id=user.id, parent_id=reply1.id)
        db.session.add(reply2)
        db.session.commit()
        self.assertEqual(reply2.parent_id, reply1.id)
        self.assertEqual(len(reply1.children), 1)
        self.assertEqual(reply1.children[0].id, reply2.id)


    def test_create_notification(self):
        """Test creating a notification."""
        user = User.query.filter_by(username='testuser').first()
        notification = self.create_notification(user)

        self.assertEqual(notification.user_id, user.id)
        self.assertEqual(notification.actor_id, user.id)
        self.assertEqual(notification.message, "This is a test notification")
        self.assertEqual(notification.notification_type, "mention")
        self.assertFalse(notification.is_read)
        self.assertIsInstance(notification.created_at, datetime)


if __name__ == '__main__':
    unittest.main()
