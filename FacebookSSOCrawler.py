from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchAttributeException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import UnexpectedAlertPresentException
import timeit

start = timeit.default_timer()
driver = webdriver.Firefox()
json_file = 'FirstOneHundred.txt' #list of just sites with Faceboook idp from study
data = [] #info for sites with fb idp from study

rank = 0
currentSite = ""
url_list = []
url_with_button = ""
method_that_found_button = ""
permissions_url = ""
permissions_list = ""


def set_permissions_list(setString):
    global permissions_list
    permissions_list = setString
def set_permissions_url(setString):
    global permissions_url
    permissions_url= setString
def get_permissions_list():
    return permissions_list
def get_permissions_url():
    return permissions_url


get_attribute_class = 'class'
get_attribute_id = 'id'

css_facebook_class_string = "[class*='facebook'"
css_facebook_id_string = "[id*='facebook'"
css_fb_class_string = "[class*='fb'"
css_fb_id_string = "[id*='fb'"
css_title_string = "[title*='Facebook'"

css_btn__class_string = "[class*='btn'"
css_button__class_string = "[class*='button"
css_btn__id_string = "[id*='btn'"
css_button__id_string = "[id*='button"
#todo: text in button = continue as

matchPatterns = []
matchPatterns.append(css_facebook_class_string)
matchPatterns.append(css_facebook_id_string)
matchPatterns.append(css_fb_class_string)
matchPatterns.append(css_fb_id_string)
matchPatterns.append(css_title_string)
#matchPatterns.append(css_btn__class_string)
#matchPatterns.append(css_button__class_string)
#matchPatterns.append(css_btn__id_string)
#matchPatterns.append(css_button__id_string)

def load_json():
    with open(json_file) as f:
        for line in f:
            data.append(json.loads(line))

def login_to_facebook():
    timeout = 3
    user = ""
    pwd = ""
    driver.get("http://www.facebook.com")
    assert "Facebook" in driver.title
    elem = driver.find_element_by_id("email")
    elem.send_keys(user)
    elem = driver.find_element_by_id("pass")
    elem.send_keys(pwd)
    elem.send_keys(Keys.RETURN)
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '.span._2md'))
        WebDriverWait(driver, timeout).until(element_present)
        element_clickable = EC.element_to_be_clickable((By.CSS_SELECTOR, '.span._2md'))
        WebDriverWait(driver,timeout).until(element_clickable)
    except TimeoutException:
        print("timed out waiting for page to load")

def is_new_url(oldURL, currentURL):
    if oldURL not in currentURL:
        return True
    return False

def is_wanted_url(curURL):
    if "scope" in curURL and "facebook" in curURL:
        return True
    return False

def check_for_success(origURL):
    #todo: check if URL is new, if so check if its the one we want
    try:
        WebDriverWait(driver, 1).until(EC.url_contains("scope"))
    except TimeoutException:
        print("timed out waiting for scope")
    success = False
    currentURL = driver.current_url
    if currentURL not in origURL:
        success = is_wanted_url(currentURL)
        if success:
            setURL = currentURL
            set_permissions_url(setURL)
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(@id,'permissions')]")))
                ele = driver.find_elements_by_xpath("//span[contains(@id,'permissions')]")
                if len(ele) > 0:
                    print(ele[0].get_attribute("innerText"))
                    permissions_list_set = ele[0].get_attribute("innerText")
                    set_permissions_list(permissions_list_set)
            except TimeoutException:
                print("timed out waiting for permisions list")
            return True
        #if not success, on some other page, return to original webpage to keep clicking around
        driver.execute_script("window.history.go(-1)")

    #if its not the one we want, check if there are two window handles. if so, switch to new window handle and check if it is facebook. if not, close that handle and return to the first page and return false.
    try:
        WebDriverWait(driver, 3).until(EC.number_of_windows_to_be(2))
    except TimeoutException:
        print("there's not two windows")
    handles = driver.window_handles
    origWindow = handles[0]
    index = 0
    if len(handles) > 1:
        for window in handles:
            if index > 0:
                #for each window, check if it is the one we want. if not, close it
                #todo: if it is window we want, still have to close all the others. get info. then close and return to original handle
                driver.switch_to.window(window)
                try:
                    WebDriverWait(driver, 3).until(EC.url_contains("scope"))
                except TimeoutException:
                    print("timed out waiting for scope")
                currentURL = driver.current_url
                if currentURL not in origURL:
                    success = is_wanted_url(currentURL)
                if success:
                    setURL = currentURL
                    set_permissions_url(setURL)
                    print("found it")
                    #record the url information, then close
                    try:
                        WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, "//*[contains(@id,'permissions')]")))
                        ele = driver.find_elements_by_xpath("//span[contains(@id,'permissions')]")
                        if len(ele) > 0:
                            print(ele[0].get_attribute("innerText"))
                            permissions_list_set = ele[0].get_attribute("innerText")
                            set_permissions_list(permissions_list_set)
                    except TimeoutException:
                        print("timed out waiting for permisions list")
                    driver.close()
                else:
                    driver.close()
            driver.switch_to.window(handles[0])
            index = index + 1
    return success

def try_locate_by_css(matchPattern):
    list = driver.find_elements_by_css_selector(matchPattern)
    found = False
    waitType = ""
    if "class" in matchPattern:
        waitType = 'class'
    else:
        waitType = 'id'
    if len(list) > 0:
        #try to click each css element that contains match pattern
        oldURL = driver.current_url
        for el in list:
            try:
                WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, str(el.get_attribute('css selector')))))
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, str(el.get_attribute('css selector')))))
                    #element_clickable = EC.element_to_be_clickable((By.CLASS_NAME, el.get_attribute('class')))
                    #WebDriverWait(driver, 5).until(element_clickable)
            except TimeoutException:
                print("time out")
            except NoSuchElementException:
                print("doesn't exist")
            except NoSuchAttributeException:
                print("attribute does not exist")
            except ElementNotInteractableException:
                print("not interactable")
            except StaleElementReferenceException:
                print("stale")
            try:
                el.click()#todo: handle click, figure out if success or not
                print("click success")#if make it to this line, we have a click! this is the only place that windows and urls need to be checked
                found = check_for_success(oldURL)
                if found is True:
                    break
                #todo: put another wait here and take it out so only have to wait if had to renavigate to original page
                #todo: maybe go off of index?
            except ElementNotInteractableException:
                print("not interactable")
            except ElementClickInterceptedException:
                print("click intercepted")
            except StaleElementReferenceException:
                print("stale")
            except NoSuchElementException:
                print("doesn't exist")
    return found

load_json()
login_to_facebook()
#driver.get('https://vk.com/login?&to=&s=0&m=1&email=')

def run_crawler():
    results = []
    #fh = open("tester.txt", "w")
    fh = open("retest_CSV.txt", "w")
    #fh1 = open("x1_temp_CSV.txt", "w")
    for domain in data:
        rank = domain['rank']
        for url in domain['url']:
            url_with_button = url
            foundForDomain = False
            if 'www.facebook.com' not in url and 'fbcdn.net' not in url:
                try:
                    try:
                        driver.get(url)
                    except Exception as e:
                        print(e)
                        pass
                    try:
                        WebDriverWait(driver,3).until(EC.alert_is_present())
                        obj = driver._switch_to.alert
                        obj.dismiss()
                    except TimeoutException:
                        print("no alert")
                    try:
                        WebDriverWait(driver,1).until(EC.title_contains('*'))
                    except TimeoutException:
                        print("title issue")

                    if "404" not in driver.title and "not found" not in driver.title:
                        for pattern in matchPatterns:
                            found = try_locate_by_css(pattern)
                            if found is True:
                                foundForDomain = True
                                permission_url = get_permissions_url()
                                permission_list = get_permissions_list()
                                perm_to_pass = permission_list.replace(" and", ",")
                                split_perm = perm_to_pass.split(',')
                                num_perms = len(split_perm)
                                stringToWrite = rank + "," + url_with_button + "," + permission_url + "," + str(num_perms) + "," + perm_to_pass + ", \n"
                                results.append(stringToWrite)
                                fh1 = open("retestCSV_temp.txt", "a")
                                fh1.write(stringToWrite)
                                fh1.close()
                                for item in results:
                                    print(item)
                                break
                        if foundForDomain is True:
                            break

                except Exception as e:
                    print(e)
                    pass
        if foundForDomain is False:
            stringWrite = rank + "," + url + "," + "NotFound" + "," + "NotFound" + ", \n"
            results.append(stringWrite)
            fh1 = open("retestCSV_temp.txt", "a")
            fh1.write(stringWrite)
            fh1.close()
            #fh1.write(stringWrite)
            #todo: string here for failed to find anything

    for item in results:
        fh.write(item)
    fh.close()


run_crawler()

stop = timeit.default_timer()
print('Runtime: ', stop - start)