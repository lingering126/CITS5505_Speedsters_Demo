import unittest
from flask import url_for
from app import create_app, db
from app.models.models import User, LoginHistory,Post, Reply,Notification
from config import TestingConfig
from werkzeug.security import generate_password_hash
import os
import openai
from unittest.mock import patch
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

    def login_test_user(self):
        """Log in the test user."""
        return self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'testpass'
        })
    
    def create_notification(self, user):
        """Create a test notification."""
        post = Post(title='Test Post', content='This is a test post', user_id=user.id)
        db.session.add(post)
        db.session.commit()
        assert post.id is not None, "Test post creation failed"

        notification = Notification(
            user_id=user.id,
            actor_id=user.id,
            message="This is a test notification",
            notification_type="mention",
            is_read=False,
            created_at=datetime.utcnow(),
            post_id=post.id  # Ensure the post ID is assigned
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    def create_test_post(self, title, content):
        """Create a test post."""
        user = User.query.filter_by(username='testuser').first()
        post = Post(title=title, content=content, user_id=user.id)
        db.session.add(post)
        db.session.commit()
        return post


class AuthRoutesTestCase(BaseTestCase):
    """Test cases for authentication routes."""


    def test_register_success(self):
        """Test successful registration."""
        response = self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 302)
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)

    def test_duplicate_username(self):
        """Test registration with a duplicate username."""
        # Register the first user
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })

        # Attempt to register the same username again
        response = self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test2@example.com'
        }, follow_redirects=True)
        
        self.assertIn(b'Username already exists.', response.data)

    def test_invalid_email(self):
        """Test registration with an invalid email format."""
        response = self.client.post(url_for('auth.register'), data={
            'username': 'testuser2',
            'password': 'testpass',
            'email': 'invalidemail'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email format', response.data)

    def test_successful_login(self):
        """Test successful login."""
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        response = self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(url_for("pr.view_post", _external=False), response.headers['Location'])  # Check for relative path

    def test_incorrect_password(self):
        """Test login with incorrect password."""
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        response = self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'wrongpass'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username or password.', response.data)

    def test_nonexistent_user(self):
        """Test login with a nonexistent user."""
        response = self.client.post(url_for('auth.login'), data={
            'username': 'nonuser',
            'password': 'testpass'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username or password.', response.data)

    def test_successful_logout(self):
        """Test successful logout."""
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'testpass'
        })
        response = self.client.get(url_for('auth.logout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/', response.headers['Location'])

    def test_login_recorded(self):
        """Test if login time and username are recorded."""
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'testpass'
        })
        login_history = LoginHistory.query.filter_by(username='testuser').first()
        self.assertIsNotNone(login_history)
        self.assertIsNone(login_history.logout_time)

    def test_logout_recorded(self):
        """Test if logout time is recorded."""
        self.client.post(url_for('auth.register'), data={
            'username': 'testuser',
            'password': 'testpass',
            'email': 'test@example.com'
        })
        self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'testpass'
        })
        self.client.get(url_for('auth.logout'))
        login_history = LoginHistory.query.filter_by(username='testuser').first()
        self.assertIsNotNone(login_history.logout_time)

class UserRoutesTestCase(BaseTestCase):
    """Test cases for user-related routes."""

    def test_user_profile_view(self):
        """Test viewing user profile."""
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()
        response = self.client.get(url_for('user.user_profile', user_id=user.id))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'testuser', response.data)

    def test_user_settings_view(self):
        """Test viewing user settings."""
        self.login_test_user()
        response = self.client.get(url_for('user.user_settings'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Profile Picture', response.data)
        self.assertIn(b'Change Password', response.data)

    def test_update_profile_picture(self):
        """Test updating profile picture."""
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()

        # Ensure the initial profile image is the default one
        self.assertEqual(user.profile_image_url, "/static/uploads/default_user.jpg")

        # Construct the full path to the sample picture file
        file_path = os.path.join(os.path.dirname(__file__), 'sample_picture.jpeg')
        with open(file_path, 'rb') as img:
            data = {
                'picture': (img, 'sample_picture.jpeg'),
                'submit_picture': True
            }
            response = self.client.post(url_for('user.user_settings'), data=data, content_type='multipart/form-data', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        

    def test_change_password(self):
        """Test changing password."""
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()

        data = {
            'current_password': 'testpass',
            'password': 'newpassword',
            'confirm_password': 'newpassword',
            'submit_password': True
        }
        response = self.client.post(url_for('user.user_settings'), data=data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Verify that the password has been updated
        self.client.get(url_for('auth.logout'))
        response = self.client.post(url_for('auth.login'), data={
            'username': 'testuser',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 302)

    def test_change_password_incorrect_current_password(self):
        """Test changing password with incorrect current password."""
        self.login_test_user()

        data = {
            'current_password': 'wrongpassword',
            'password': 'newpassword',
            'confirm_password': 'newpassword',
            'submit_password': True
        }
        response = self.client.post(url_for('user.user_settings'), data=data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)


    def test_change_password_mismatched_passwords(self):
        """Test changing password with mismatched new passwords."""
        self.login_test_user()

        data = {
            'current_password': 'testpass',
            'password': 'newpassword1',
            'confirm_password': 'newpassword2',
            'submit_password': True
        }
        response = self.client.post(url_for('user.user_settings'), data=data, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Passwords must match', response.data)

    def test_post_history_view(self):
        """Test viewing post history."""
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()

        # Create a post by the test user
        post = Post(title='Test Post', content='This is a test post', user_id=user.id, category='general')
        db.session.add(post)
        db.session.commit()

        response = self.client.get(url_for('user.user_profile', user_id=user.id, tab='posts'))
        self.assertEqual(response.status_code, 200)
        
        # Check for the post title in the response
        self.assertIn(b'Test Post', response.data)
        
        # Check for the start text and username in the response
        self.assertIn(b'Started by', response.data)
        self.assertIn(user.username.encode('utf-8'), response.data)

    def test_reply_history_view(self):
        """Test viewing reply history."""
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()

        # Create a post by another user
        another_user = User(username='anotheruser', email='another@example.com', password_hash=generate_password_hash('anotherpass'))
        db.session.add(another_user)
        db.session.commit()
        post = Post(title='Another Post', content='This is another post', user_id=another_user.id, category='general')
        db.session.add(post)
        db.session.commit()

        # Create a reply by the test user
        reply = Reply(content='This is a reply', post_id=post.id, user_id=user.id)
        db.session.add(reply)
        db.session.commit()

        response = self.client.get(url_for('user.user_profile', user_id=user.id, tab='replies'))
        self.assertEqual(response.status_code, 200)

class ChatbotTestCase(BaseTestCase):
    """Test case for chatbot route."""

    @patch('openai.ChatCompletion.create')
    def test_chatbot_response(self, mock_openai_create):
        """Test the chatbot response."""
        self.login_test_user()

        # Simulate sending a question to the chatbot
        response = self.client.post(url_for('pr.chat'), data={
            'question': 'What is the capital of France?'
        }, follow_redirects=True)

        # Ensure the session chat history is initialized
        with self.client.session_transaction() as sess:
            sess['chat_history'] = []

        # Ensure the response is successful
        self.assertEqual(response.status_code, 200)

class NotificationRoutesTestCase(BaseTestCase):
    """Test cases for notification routes."""
    def test_mark_notification_as_read(self):
        """Test marking a notification as read."""
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()
        notification = self.create_notification(user)

        response = self.client.get(url_for('notifications.mark_as_read', notification_id=notification.id))
        self.assertEqual(response.status_code, 302)  # Redirect

        # Check if the notification is marked as read
        notification = Notification.query.get(notification.id)
        self.assertTrue(notification.is_read)

    def test_delete_notification(self):
        """Test deleting a notification."""
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()
        notification = self.create_notification(user)

        response = self.client.get(url_for('notifications.delete_notification', notification_id=notification.id))
        self.assertEqual(response.status_code, 302)  # Redirect

        # Check if the notification is deleted
        notification = Notification.query.get(notification.id)
        self.assertIsNone(notification)

    def test_latest_notifications(self):
        """Test retrieving the latest notifications."""
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()
        self.create_notification(user)

        response = self.client.get(url_for('notifications.latest_notifications'))
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['message'], "This is a test notification")

class SearchPostTestCase(BaseTestCase):
    """Test cases for search functionality."""

    def test_search_by_title(self):
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()
        self.create_test_post('First Post', 'This is the first post')
        self.create_test_post('Second Post', 'This is the second post with some unique content')
        response = self.client.get(url_for('pr.search'), query_string={'q': 'First', 'search_type': 'Titles'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'First Post', response.data)
        self.assertNotIn(b'Second Post', response.data)

    def test_search_by_content(self):
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()
        self.create_test_post('First Post', 'This is the first post')
        self.create_test_post('Second Post', 'This is the second post with some unique content')
        response = self.client.get(url_for('pr.search'), query_string={'q': 'second', 'search_type': 'Descriptions'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Second Post', response.data)
        self.assertNotIn(b'First Post', response.data)

    def test_search_by_title_and_content(self):
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()
        self.create_test_post('First Post', 'This is the first post')
        self.create_test_post('Second Post', 'This is the second post with some unique content')
        response = self.client.get(url_for('pr.search'), query_string={'q': 'post', 'search_type': 'Both'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'First Post', response.data)
        self.assertIn(b'Second Post', response.data)

    def test_search_no_query(self):
        self.login_test_user()
        user = User.query.filter_by(username='testuser').first()
        self.create_test_post('First Post', 'This is the first post')
        self.create_test_post('Second Post', 'This is the second post with some unique content')
        response = self.client.get(url_for('pr.search'), query_string={'q': '', 'search_type': 'Both'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'First Post', response.data)
        self.assertNotIn(b'Second Post', response.data)


if __name__ == '__main__':
    unittest.main()
