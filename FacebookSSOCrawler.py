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
import sys

#FacebookSSOFinalCrawler.py
#Created By: Megan Corbett
#crawls sites contained in provided json text document to identify and click login with Facebook buttons
#and record the number of permissions requested per site.

#todo: user defines sites file and Facebook login here
json_file = "FILE_NAME_HERE" #list of just sites with Faceboook idp from study
user = "EMAIL_HERE" #email for facebook account login. MUST be entered before program is run
pwd = "PASSWORD_HERE" #facebook account password

start = timeit.default_timer()
driver = webdriver.Firefox()
timeout = 3
data = [] #info for sites with fb idp from study

#variables for creating line to write to csv
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

def reset_browser(url):
    global driver
    driver = webdriver.Firefox()
    login_to_facebook()
    driver.get(url)

# get_attribute_class = 'class'
# get_attribute_id = 'id'

#string patterns that may be contained in Facebook Login button css selector.
css_facebook_class_string = "[class*='facebook'"
css_facebook_id_string = "[id*='facebook'"
css_fb_class_string = "[class*='fb'"
css_fb_id_string = "[id*='fb'"
css_title_string = "[title*='Facebook'"

# css_btn__class_string = "[class*='btn'"
# css_button__class_string = "[class*='button"
# css_btn__id_string = "[id*='btn'"
# css_button__id_string = "[id*='button"

matchPatterns = [] #store in array so can be looped through
matchPatterns.append(css_facebook_class_string)
matchPatterns.append(css_facebook_id_string)
matchPatterns.append(css_fb_class_string)
matchPatterns.append(css_fb_id_string)
matchPatterns.append(css_title_string)
#matchPatterns.append(css_btn__class_string)
#matchPatterns.append(css_button__class_string)
#matchPatterns.append(css_btn__id_string)
#matchPatterns.append(css_button__id_string)

#load the json data (original json was converted to txt due to formatting issues (had to strip return character)
def load_json():
    with open(json_file) as f:
        for line in f:
            data.append(json.loads(line))

#login to dummy facebook account.
def login_to_facebook():
    timeout = 3
    driver.get("http://www.facebook.com")
    assert "Facebook" in driver.title
    elem = driver.find_element_by_id("email")
    elem.send_keys(user)
    elem = driver.find_element_by_id("pass")
    elem.send_keys(pwd)
    elem.send_keys(Keys.RETURN)
    try:
        #make sure it completes login
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, '.span._2md'))
        WebDriverWait(driver, timeout).until(element_present)
        element_clickable = EC.element_to_be_clickable((By.CSS_SELECTOR, '.span._2md'))
        WebDriverWait(driver,timeout).until(element_clickable)
    except TimeoutException:
        print("timed out waiting for page to load")

#check if the url has changed i.e. on a new webpage
def is_new_url(oldURL, currentURL):
    if oldURL not in currentURL:
        return True
    return False

#check if the current url contains Facebook and scope
#if these are contained then it is the URL we want.
def is_wanted_url(curURL):
    if "scope" in curURL and "facebook" in curURL:
        return True
    return False

#check for success method does window handling. first it checks if the current window has the facebook url.
#if not it checks for a pop-up window
def check_for_success(origURL):
    #check if URL is new, if so check if its the one we want
    try:
        WebDriverWait(driver, 1).until(EC.url_contains("scope"))
    except TimeoutException:
        print("timed out waiting for scope")
    success = False
    currentURL = driver.current_url
    if currentURL not in origURL:
        success = is_wanted_url(currentURL) #check if this is a permissions request page.
        if success:
            setURL = currentURL
            set_permissions_url(setURL) #switch to current url
            #url was found, now need to get the permissions list.
            try:
                WebDriverWait(driver, timeout).until(
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

    #if its not the one we want, check if there are two window handles. if so, switch to new window handle and check if it is facebook.
    # if not, close that handle(close the popup) and return to the first page and return false.
    try:
        WebDriverWait(driver, timeout).until(EC.number_of_windows_to_be(2))
    except TimeoutException:
        print("there's not two windows")

    handles = driver.window_handles
    origWindow = handles[0]
    index = 0
    if len(handles) > 1:
        for window in handles:
            if index > 0:
                #for each window, check if it is the one we want. if not, close it
                #if it is window we want, still have to close all the others. get info. then close and return to original handle
                driver.switch_to.window(window)
                try:
                    WebDriverWait(driver, timeout).until(EC.url_contains("scope"))
                except TimeoutException:
                    print("timed out waiting for scope")
                currentURL = driver.current_url
                if currentURL not in origURL:
                    success = is_wanted_url(currentURL) #check if this is a request permissions page
                if success:
                    setURL = currentURL
                    set_permissions_url(setURL)
                    print("found it")
                    #record the url information, then close
                    try:
                        WebDriverWait(driver, timeout).until(
                            EC.presence_of_element_located((By.XPATH, "//*[contains(@id,'permissions')]")))
                        ele = driver.find_elements_by_xpath("//span[contains(@id,'permissions')]")
                        if len(ele) > 0:
                            print(ele[0].get_attribute("innerText"))
                            permissions_list_set = ele[0].get_attribute("innerText")
                            set_permissions_list(permissions_list_set)
                    except TimeoutException:
                        print("timed out waiting for permissions list")
                    driver.close()
                else:
                    driver.close()
            driver.switch_to.window(handles[0])
            index = index + 1
    return success

#method to attempt to locate Facebook Login buttons by css selectors using a match pattern string.
def try_locate_by_css(matchPattern):
    list = driver.find_elements_by_css_selector(matchPattern) #find all css selectors on the page containing the string
    found = False

    if len(list) > 0:
        #if the list is not empty, then matching css selectors were located
        #try to click each css element that contains match pattern
        oldURL = driver.current_url #save this url for comparison

        #for each matching selector, wait for it to load fully, then try to click it.
        for el in list:
            try:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, str(el.get_attribute('css selector')))))
                WebDriverWait(driver, timeout).until(
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

            #try clicking
            try:
                el.click()#here is the click
                print("click success")#if make it to this line, we have a click! this is the only place that windows and urls need to be checked
                found = check_for_success(oldURL)
                if found is True:
                    break
            except ElementNotInteractableException:
                print("not interactable")
            except ElementClickInterceptedException:
                print("click intercepted")
            except StaleElementReferenceException:
                print("stale")
            except NoSuchElementException:
                print("doesn't exist")
    return found #return if the button was found

#this crawls the original dataset, getting each url to
def run_crawler():
    results = []  # store results here to be written to final csv at end of run
    # for each top ranked site
    for domain in data:
        rank = domain['rank']
        #for each url listed as potentially having a Facebook SSO registration button. attempt to load the url.
        #do not try to load if it has a 404 error of if it is a direct link to facebook (results in (seemingly) endless click times)
        for url in domain['url']:
            url_with_button = url
            foundForDomain = False
            if 'www.facebook.com' not in url and 'fbcdn.net' not in url:
                try:
                    try:
                        driver.get(url)
                    except Exception as e:
                        print(e)
                        if "discarded" in str(e) or "without establishing a connection" in str(e):
                            reset_browser(url) #if browser crashes need to reconnect and relogin to facebook
                        pass
                    try:
                        WebDriverWait(driver,timeout).until(EC.alert_is_present())
                        obj = driver._switch_to.alert #need to handle alert if one pops up. unfortunately also need
                        obj.dismiss()                  #to try to wait for this to render all the way (if it is even going
                                                    # to be present before can move on, otherwise it breaks with an alert with no response
                    except TimeoutException:
                        print("no alert")
                    try:
                        WebDriverWait(driver,1).until(EC.title_contains('*'))
                    except TimeoutException:
                        print("timed out")

                    # if everything checks out, call the method to check for button and construct a write string based on its return.
                    if "404" not in driver.title and "not found" not in driver.title:
                        for pattern in matchPatterns:
                            found = try_locate_by_css(pattern) #try to locate button!!
                            if found is True:
                                foundForDomain = True
                                permission_url = get_permissions_url()
                                permission_list = get_permissions_list()
                                perm_to_pass = permission_list.replace(" and", ",")
                                split_perm = perm_to_pass.split(',')
                                num_perms = len(split_perm)
                                stringToWrite = rank + "," + url_with_button + ",\"" + permission_url + "\"," + str(num_perms) + "," + perm_to_pass + ", \n"
                                results.append(stringToWrite)
                                for item in results:
                                    print(item)
                                fh1 = open("crawlResultsCSV_temp.txt", "a")  # write to temporary file in case of crash.
                                fh1.write(stringToWrite)  # store in temp file
                                fh1.close()
                                break
                        if foundForDomain is True:
                            break

                except Exception as e:
                    print(e)
                    if "discarded" in str(e) or "without establishing a connection" in str(e):
                        reset_browser(url)
                    pass
        if foundForDomain is False:
            stringWrite = rank + "," + url + "," + "NotFound" + "," + "NotFound" + ", \n"
            results.append(stringWrite)
            fh1 = open("crawlResultsCSV_temp.txt", "a")  # write to temporary file in case of crash.
            fh1.write(stringWrite)  # store in temp file
            fh1.close()
    # once everything is done being crawled, write the final dataset and include runtime
    fh = open("crawlResults_CSV.txt", "w")  # file to be written to
    for item in results:
        fh.write(item)
    fh.close()

#on run time, load json doc, login to Facebook, then start crawling. close browser and print runtime on completion
load_json()
login_to_facebook()
run_crawler()
driver.close()

stop = timeit.default_timer()
runtime = stop - start
print('Runtime: ', stop - start)
fh = open("crawlResults_CSV.txt", "a")
fh.write("Runtime: " + str(runtime))
fh.close()