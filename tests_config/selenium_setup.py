import pytest

from selenium import webdriver


@pytest.fixture(scope='module')
def chrome_browser_instance(request):
    """Provide a selenium webdriver instance."""

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=chrome_options)

    yield browser
    browser.close()
