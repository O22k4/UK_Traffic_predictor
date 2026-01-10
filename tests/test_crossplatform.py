import unittest
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


APP_URL = "http://localhost:8501"


class TestCrossPlatform(unittest.TestCase):

    def run_streamlit_test(self, driver, browser_name):
        print(f"\nRunning test on: {browser_name}")
        driver.get(APP_URL)

        # Ensure Streamlit loaded
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        print("⏳ Waiting 60 seconds for manual dataset/model upload...")
        time.sleep(60)

        # Scroll to bottom to force Streamlit render
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        try:
            # 🔁 Re-locate button RIGHT BEFORE click (prevents stale element)
            for _ in range(3):  # retry loop
                try:
                    buttons = WebDriverWait(driver, 60).until(
                        EC.presence_of_all_elements_located((By.TAG_NAME, "button"))
                    )
                    driver.execute_script("arguments[0].click();", buttons[-1])
                    break
                except StaleElementReferenceException:
                    time.sleep(1)
        except TimeoutException:
            driver.quit()
            self.fail(f"❌ Predict button not found in {browser_name}")

        # Wait for ANY Streamlit output
        try:
            WebDriverWait(driver, 180).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "[data-testid='stMarkdownContainer']")
                )
            )
        except TimeoutException:
            driver.quit()
            self.fail(f"❌ No prediction output in {browser_name}")

        print(f"✅ {browser_name} test PASSED")
        driver.quit()

    # ---------------- CHROME ----------------
    def test_chrome(self):
        chrome_options = ChromeOptions()
        chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        chrome_options.add_argument("--start-maximized")

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )

        self.run_streamlit_test(driver, "Chrome")

    # ---------------- FIREFOX ----------------
    def test_firefox(self):
        firefox_options = FirefoxOptions()
        firefox_options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

        driver = webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=firefox_options
        )

        self.run_streamlit_test(driver, "Firefox")

    # ---------------- EDGE ----------------
    def test_edge(self):
        self.skipTest("Edge skipped due to driver download restrictions")


if __name__ == "__main__":
    unittest.main()
