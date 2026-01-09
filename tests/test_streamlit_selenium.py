import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

class TestStreamlitApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        # chrome_options.add_argument("--headless")  # optional

        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        cls.driver.get("http://localhost:8501")  # Streamlit app URL

    def test_prediction_workflow(self):
        driver = self.driver

        # Wait for manual upload
        print("Please upload the dataset and model manually in the next 60 seconds...")
        time.sleep(60)  # give you time to upload files

        # Wait for the Predict button to appear
        predict_button = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Predict')]"))
        )

        # Scroll button into view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", predict_button)
        time.sleep(1)  # short pause to stabilize view

        # Click using JavaScript to avoid interception issues
        driver.execute_script("arguments[0].click();", predict_button)

        # Wait for any output in Streamlit
        output_texts = WebDriverWait(driver, 180).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, '//div[@data-testid="stMarkdownContainer"]//div')
            )
        )

        self.assertTrue(len(output_texts) > 0, "Prediction output not found!")
        print("Prediction output detected successfully!")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
