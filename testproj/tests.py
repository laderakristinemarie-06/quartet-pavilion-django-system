from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest

class HomepageHeadingTest(unittest.TestCase):

    def setUp(self):
        """
        SECTION 1: SETUP
        This initializes the Chrome browser and sets an implicit wait.
        """
        self.driver = webdriver.Chrome()
        
        # This tells Selenium to wait up to 10 seconds for elements 
        # to appear before throwing an error.
        self.driver.implicitly_wait(10) 

    def test_verify_main_heading(self):
        """
        Navigates to the site, finds the heading by ID, and checks the text.
        """
        driver = self.driver

        # Step A: Navigate to the local Django server
        driver.get("http://127.0.0.1:8000/")

        # Step B: Locate the element using the unique 'main-heading' ID
        heading_element = driver.find_element(By.ID, "main-heading")

        # Step C: Assert that the text content matches our expectation
        actual_text = heading_element.text
        expected_text = "Welcome to My Site!"
        
        self.assertEqual(actual_text, expected_text, 
                         f"Error: Expected '{expected_text}', but found '{actual_text}'")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()