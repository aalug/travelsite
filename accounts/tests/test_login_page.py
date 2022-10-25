import pytest

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


@pytest.mark.selenium
def test_user_login(live_server, create_test_user, chrome_browser_instance):
    """Test logging-in from a login page."""
    browser = chrome_browser_instance
    browser.get(('%s%s' % (live_server.url, '/login/')))

    email = browser.find_element(By.NAME, 'email')
    password = browser.find_element(By.NAME, 'password')
    submit = browser.find_element(By.XPATH, '//*[@id="form-submit"]')
    email.send_keys('test_user@example.com')
    password.send_keys('asdasd123123')
    submit.send_keys(Keys.RETURN)

    assert 'Edit your account details' in browser.page_source


@pytest.mark.selenium
def test_superuser_login(live_server, create_test_superuser, chrome_browser_instance):
    """Test logging-in from a login page into admin page."""
    browser = chrome_browser_instance
    browser.get(('%s%s' % (live_server.url, '/login/')))

    email = browser.find_element(By.NAME, 'email')
    password = browser.find_element(By.NAME, 'password')
    submit = browser.find_element(By.XPATH, '//*[@id="form-submit"]')
    email.send_keys('admin_user@example.com')
    password.send_keys('asdasd123123')
    submit.send_keys(Keys.RETURN)

    assert 'Site administration' in browser.page_source
