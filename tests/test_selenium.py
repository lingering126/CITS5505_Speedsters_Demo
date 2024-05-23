import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class SeleniumTestCase(unittest.TestCase):
    """Selenium tests for the application."""

    @classmethod
    def setUpClass(cls):
        """Set up the test driver and application URL once for all tests."""
        cls.driver = webdriver.Chrome()
        cls.base_url = "http://127.0.0.1:5000"
        cls.register_user()

    @classmethod
    def tearDownClass(cls):
        """Quit the driver after all tests."""
        cls.driver.quit()

    @classmethod
    def register_user(cls):
        """Register a user to use for login tests."""
        driver = cls.driver
        driver.get(cls.base_url + "/register")

        try:
            # Use explicit wait to ensure elements are present
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "username")))
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "password")))
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "email")))
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))

            # Find the registration form elements
            username = driver.find_element(By.NAME, "username")
            password = driver.find_element(By.NAME, "password")
            email = driver.find_element(By.NAME, "email")
            submit = driver.find_element(By.XPATH, "//button[@type='submit']")

            # Fill in the form
            username.send_keys("seleniumuser")
            password.send_keys("testpass")
            email.send_keys("selenium@example.com")
            submit.click()

            # Wait for redirect and check if registration was successful
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'alert-success') and contains(text(), 'Registration successful')]"))
            )
            assert "Registration successful" in driver.page_source
        except Exception as e:
            print(driver.page_source)  # Print the page source for debugging
            raise e

    def setUp(self):
        """Set up for each test."""
        self.driver = self.__class__.driver
        self.base_url = self.__class__.base_url

    def test_login(self):
        """Test user login."""
        driver = self.driver
        driver.get(self.base_url + "/login")

        try:
            # Use explicit wait to ensure elements are present
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "username")))
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "password")))
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))

            # Find the login form elements
            username = driver.find_element(By.NAME, "username")
            password = driver.find_element(By.NAME, "password")
            submit = driver.find_element(By.XPATH, "//button[@type='submit']")

            # Fill in the form
            username.send_keys("seleniumuser")
            password.send_keys("testpass")
            submit.click()

            # Wait for the page to load and the user dropdown to be clickable
            WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "navbarDropdownMenuLink")))

            # Click on the user profile dropdown
            user_dropdown = driver.find_element(By.ID, "navbarDropdownMenuLink")
            user_dropdown.click()

            # Wait for the "Logout" link to be visible
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.LINK_TEXT, "Logout")))

            # Check if the "Logout" link is present
            self.assertIn("Logout", driver.page_source)
        except Exception as e:
            print(driver.page_source)  # Print the page source for debugging
            raise e

    def test_post_creation(self):
        """Test post creation."""
        driver = self.driver
        self.test_login()  # Log in first

        driver.get(self.base_url + "/view_posts")

        # Use explicit wait to ensure elements are present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Create Post")))

        # Click on Create Post button
        create_post_button = driver.find_element(By.LINK_TEXT, "Create Post")
        create_post_button.click()

        # Use explicit wait to ensure elements are present on the Create Post page
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "title")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "category")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "content")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "submit")))

        # Find the new post form elements
        title = driver.find_element(By.NAME, "title")
        category = driver.find_element(By.NAME, "category")
        content = driver.find_element(By.NAME, "content")
        submit = driver.find_element(By.NAME, "submit")

        # Fill in the form
        title.send_keys("Selenium Test Post")
        category.send_keys("discussion")

        # Set content using JavaScript to handle CKEditor
        driver.execute_script("CKEDITOR.instances['content'].setData('This is a test post created by Selenium.');")
        
        submit.click()

        # Wait for redirect and check if post was created
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "Selenium Test Post"))
        )
        self.assertIn("Selenium Test Post", driver.page_source)

    def test_reply_creation(self):
        """Test reply creation."""
        driver = self.driver
        self.test_login()  # Log in first

        # Navigate to the post details page
        driver.get(self.base_url + "/view_posts")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "Selenium Test Post")))
        post_link = driver.find_element(By.LINK_TEXT, "Selenium Test Post")
        post_link.click()

        # Use explicit wait to ensure elements are present on the post details page
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "reply_content")))

        # Find the reply form elements
        reply_content = driver.find_element(By.NAME, "reply_content")
        reply_submit = driver.find_element(By.XPATH, "//button[@type='submit' and contains(text(), 'Reply')]")

        # Set reply content using JavaScript to handle CKEditor
        driver.execute_script("CKEDITOR.instances['replyContent'].setData('This is a test reply created by Selenium.');")

        # Submit the reply form
        reply_submit.click()

        # Wait for the reply to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'This is a test reply created by Selenium.')]"))
        )

        # Check if reply was created
        self.assertIn("This is a test reply created by Selenium.", driver.page_source)

if __name__ == '__main__':
    unittest.main()
