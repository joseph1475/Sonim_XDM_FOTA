from logging import getLogger

import pytest
import openpyxl
import pandas as pd
from selenium import webdriver  # Importing web driver
from selenium.webdriver.support.select import Select
import time

driver = None


# Code for selecting user input at run time :
def pytest_addoption(parser):
    parser.addoption("--browser_name", action="store", default="Firefox")
    parser.addoption("--model_name", action="store", default="XP5800")
    parser.addoption("--login_name", action="store", help="input useranme")
    parser.addoption("--login_password", action="store", help="input password")
    parser.addoption("--excel_path", action="store", help="input FOTA_Setup_Readme path")
    parser.addoption("--driver_path", action="store", help="input driver path")

@pytest.fixture(scope="class")
def setup(request):
    global driver  # defined driver as global so screenshot capture can use it
    browser_name = request.config.getoption("browser_name")  # browser code for selecting different browser at run time
    driver_path = request.config.getoption("driver_path")
    if browser_name == "Firefox":
        driver = webdriver.Firefox(executable_path=driver_path)
    elif browser_name == "InternetExplorer":
        driver = webdriver.Ie(executable_path=driver_path)
    elif browser_name == "Chrome":
        driver = webdriver.Chrome(driver_path)
    driver.maximize_window()
    driver.get("https://xdme.wireless.att.com/jsp/login/login.jsp")  # open the web page provided
    driver.implicitly_wait(30)  # implicitly wait will wait for the events to occur
    print(driver.title)  # title of web page
    print(driver.current_url)  # url loaded to be printed
    # to run from pycharm enable this
    # excel = pd.read_excel(r"D:\Python_XDM\FOTA_Setup_Readme.xlsx", sheet_name=1)  # using pandas for calling excel
    # username = excel.iloc[0, 2]  # used to locate values
    # password = excel.iloc[1, 2]
    username = request.config.getoption("login_name")  # getting login details from user input
    password = request.config.getoption("login_password")
    driver.find_element_by_name("LOGIN").send_keys(username)
    print("Username entered")
    time.sleep(1)
    driver.find_element_by_css_selector("input[name='PASSWORD']").send_keys(
        password)  # enter password using css selector method
    print("Password entered")
    time.sleep(1)
    driver.find_element_by_xpath("//input[@type='submit']").click()  # to select the sumit button using xpath method
    if driver.current_url == "https://xdme.wireless.att.com/jsp/main/main.jsp":
        print("Login success")
    else:
        print("Invalid Login Please Try Again")
        print("Login failed - !!!XDM account will be blocked on three incorrect password.!!!")
        driver.quit()

    #senting excel_path to BaseClass using request.cls
    excel_path = request.config.getoption("excel_path")
    request.cls.excel_path = excel_path
    print(excel_path)
    # senting model_name to BaseClass using request.cls
    model_name = request.config.getoption("model_name")
    request.cls.model_name = model_name
    print(model_name)
    request.cls.driver = driver
    yield
    driver.close()


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item):
    """
        Extends the PyTest Plugin to take and embed screenshot in html report, whenever test fails.
        :param item:
        """
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    if report.when == 'call' or report.when == "setup":
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            file_name = report.nodeid.replace("::", "_") + ".png"
            _capture_screenshot(file_name)
            if file_name:
                html = '<div><img src="%s" alt="screenshot" style="width:304px;height:228px;" ' \
                       'onclick="window.open(this.src)" align="right"/></div>' % file_name
                extra.append(pytest_html.extras.html(html))
        report.extra = extra


def _capture_screenshot(name):
    driver.get_screenshot_as_file(name)
