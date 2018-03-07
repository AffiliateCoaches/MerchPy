import webbrowser, sys, csv, re, selenium, os, time, shutil
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

def write_leftovers(head, shirts, newfile = False):
    file_name = 'merchpy.csv'
    if newfile == True:
        file_name = 'shirts_backup'+str(time.time())+'.csv'
    with open(file_name, 'w') as f:
                    writer=csv.writer(f, lineterminator='\n')
                    for x in head:
                        writer.writerow(x)

                    for x in shirts:
                        writer.writerow(x)

daily_limit = 200

with open('merchpy.csv', 'r') as f:
    reader = csv.reader(f)
    shirts = list(reader)

finished_shirts = list()

creds = shirts[0]
userEmail = creds[1]
userPass = creds[3]
header = shirts[:2]
#strip the header and credentials
shirts = shirts[2:]

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
browser = webdriver.Chrome(chrome_options=options)

i = 0
try:
    for shirt in list(shirts):
        i += 1
        if i > daily_limit:
            break

        if len(shirt) < 10:
            print("Not enough values in CSV row - " + ",".join(str(x) for x in shirt))
            break

        s = {}
        s['type'] = shirt[0]
        s['brand'] = shirt[1]
        s['title'] = shirt[2]
        s['feat1'] = shirt[3]
        s['feat2'] = shirt[4]
        s['color'] = shirt[5].upper()
        s['fit'] = shirt[6].upper()
        s['price'] = shirt[7]
        s['file'] = shirt[8]
        s['desc'] = shirt[9]

        if not bool(s['type'].strip()):
            print("Shirt type cannot be empty.")
            break
        elif not bool(s['brand'].strip()):
            print("Shirt brand cannot be empty.")
            break
        elif not bool(s['title'].strip()):
            print("Shirt title cannot be empty.")
            break
        elif not bool(s['color'].strip()):
            print("Shirt colors cannot be empty.")
            break
        elif not bool(s['fit'].strip()):
            print("Shirt fit cannot be empty.")
            break
        elif not bool(s['price'].strip()):
            print("Shirt price cannot be empty.")
            break
        elif not bool(s['file'].strip()):
            print("Shirt file name cannot be empty.")
            break
        
        if len(s['desc']) > 0 and len(s['desc']) < 75 or len(s['desc']) > 2000:
            print("Description must be either empty or between 75 and 2000 characters. Error for file - " + s['file'])
            break

        if not s['file'].endswith(".png"):
            print("Must provide a file name ending with '.png'. Filename given - " + s['file'])
            break
        
        if not os.path.exists(s['file']):
            print("This file does not exist in the merchpy directory - " + s['file'])
            break

        try:
            integral, fractional = s['price'].split('.')
            n = float(s['price'])
            if len(fractional) == 2:
                pass
            else:
                raise ValueError
        except ValueError:
            print('Error with your price, please enter it as 4 digits, for example 19.99. You entered - ' + s['price'])
            break

        browser.get('http://merch.amazon.com/merch-tshirt/title-setup/new/upload_art')

        #log in if credentials are supplied in the CSV
        if bool(userEmail.strip()) and bool(userPass.strip()):
            try:
                emailElem = browser.find_element_by_id('ap_email')
                emailElem.send_keys(userEmail)
                passwordElem = browser.find_element_by_id('ap_password')
                passwordElem.send_keys(userPass)
                passwordElem.submit()
            except:
                pass
        
        #wait to get past login screen, either by automatic login or by user logging in
        WebDriverWait(
                    browser, 90
            ).until(EC.presence_of_element_located((By.ID, 'data-draft-tshirt-assets-front-image-asset-cas-shirt-art-image-file-upload-AjaxInput')))

        #select shirt type
        typeSelect = Select(browser.find_element_by_id("data-draft-shirt-type-native"))
        if s['type'].upper() == "STANDARD":
            typeSelect.select_by_value("HOUSE_BRAND")
        elif s['type'].upper() == "PREMIUM":
            typeSelect.select_by_value("PREMIUM_BRAND")
        elif s['type'].upper() == "LONGSLEEVE":
            typeSelect.select_by_value("STANDARD_LONG_SLEEVE")
        elif s['type'].upper() == "SWEATSHIRT":
            typeSelect.select_by_value("STANDARD_SWEATSHIRT")
        elif s['type'].upper() == "HOODIE":
            typeSelect.select_by_value("STANDARD_PULLOVER_HOODIE")
        else:
            typeSelect.select_by_value("HOUSE_BRAND")

        #upload file
        #HOODIE has different selectors so if statement is necessary and handled first
        if s['type'].upper() == "HOODIE":
            browser.find_element_by_id("data-draft-tshirt-assets-front-image-asset-cas-hoodie-art-image-file-upload-AjaxInput").send_keys(os.getcwd()+"\\"+s['file'])

            try:
                print("waiting for processing message to appear")
                WebDriverWait(
                        browser, 180
                ).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, '#data-draft-tshirt-assets-front-image-asset-cas-hoodie-art-image-file-upload-uploading-message.a-hidden')))

                print("waiting for processing message to disappear")
                WebDriverWait(
                        browser, 180
                ).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#data-draft-tshirt-assets-front-image-asset-cas-hoodie-art-image-file-upload-uploading-message.a-hidden')))

                time.sleep(4)

                print(s['title'] + " - file upload complete (file = " + s['file'] + ")")
            

            #click continue after upload
                browser.find_element_by_id("save-and-continue-upload-art-announce").click()
            except:
                print("timed out looking")

        #upload file (still)
        #Handle the rest of merch types after hoodie
        else:
            browser.find_element_by_id("data-draft-tshirt-assets-front-image-asset-cas-shirt-art-image-file-upload-AjaxInput").send_keys(os.getcwd()+"\\"+s['file'])

            try:
                print("waiting for processing message to appear")
                WebDriverWait(
                        browser, 180
                ).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, '#data-draft-tshirt-assets-front-image-asset-cas-shirt-art-image-file-upload-uploading-message.a-hidden')))

                print("waiting for processing message to disappear")
                WebDriverWait(
                        browser, 180
                ).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#data-draft-tshirt-assets-front-image-asset-cas-shirt-art-image-file-upload-uploading-message.a-hidden')))

                time.sleep(4)

                print(s['title'] + " - file upload complete (file = " + s['file'] + ")")
            

            #click continue after upload
                browser.find_element_by_id("save-and-continue-upload-art-announce").click()
            except:
                print("timed out looking")

        WebDriverWait(
                    browser, 20
            ).until(EC.visibility_of_element_located((By.ID, 'data-draft-list-prices-marketplace-1-amount')))
        #new we must set price, shirt type, fit type, and colors
        #set Price
        priceElem = browser.find_element_by_id("data-draft-list-prices-marketplace-1-amount")
        priceElem.clear()
        priceElem.send_keys(s['price'])

        #fit type
        fits = s['fit'].split(",")
        fits = [x.strip(' ') for x in fits]

        if s['type'].upper() == "LONGSLEEVE" or s['type'].upper() == "SWEATSHIRT" or s['type'].upper() == "HOODIE":
            pass
        else:
            WebDriverWait(
                        browser, 20
                ).until(EC.visibility_of_element_located((By.ID, 'data-shirt-configurations-fit-type-men')))
            #men and women selected by default, do opposite
            if not any(f in fits for f in ["MEN","MENS"]):
                browser.find_element_by_id("data-shirt-configurations-fit-type-men").send_keys(selenium.webdriver.common.keys.Keys.SPACE)
            if not any(f in fits for f in ["WOMEN","WOMENS"]):
                browser.find_element_by_id("data-shirt-configurations-fit-type-women").send_keys(selenium.webdriver.common.keys.Keys.SPACE)
            if any(f in fits for f in ["YOUTH","YOUTHS","KID","KIDS"]):
                browser.find_element_by_id("data-shirt-configurations-fit-type-youth").send_keys(selenium.webdriver.common.keys.Keys.SPACE)

        #do colors
        colors = s['color'].split(",")
        colors = [x.strip().replace(" ","_").replace("-","_").lower() for x in colors]

        for c in colors:
            browser.find_element_by_id("gear-tshirt-image").click()
            time.sleep(.25)
            if c == "royal_blue": #color called royal blue in the tooltip but is identified by 'royal'
                n = "royal"
            else:
                n = c.lower()

            browser.find_element_by_id("gear-checkbox-"+n).click()

        print(s['title'] + " - colors and fit type complete (file = " + s['file'] + ")")

        #continue
        browser.find_element_by_id("save-and-continue-choose-variations-announce").click()

        WebDriverWait(
                    browser, 20
            ).until(EC.visibility_of_element_located((By.ID, 'data-draft-brand-name')))

        #text details
        browser.find_element_by_id('data-draft-brand-name').send_keys(s['brand'])
        browser.find_element_by_id('data-draft-name-en-us').send_keys(s['title'])
        browser.find_element_by_id('data-draft-bullet-points-bullet1-en-us').send_keys(s['feat1'])
        browser.find_element_by_id('data-draft-bullet-points-bullet2-en-us').send_keys(s['feat2'])
        browser.find_element_by_id('data-draft-description-en-us').send_keys(s['desc'])
        browser.find_element_by_id("save-and-continue-announce").click()

        print(s['title'] + " - brand, title, desc complete (file = " + s['file'] + ")")

        WebDriverWait(
                    browser, 20
            ).until(EC.presence_of_element_located((By.ID, 'publish-announce')))

        #review and submit
        browser.find_element_by_xpath("//*[contains(text(), 'Sell - Public on Amazon')]").click()
        time.sleep(4)
        browser.find_element_by_id("publish-announce").click()
        time.sleep(4)
        browser.execute_script("document.getElementById('publish-confirm-button-announce').click();")

        print(s['title'] + " reviewed and submitted (file = " + s['file'] + ")")
        
        WebDriverWait(
                    browser, 60
            ).until(EC.presence_of_element_located((By.ID, 'landing-page')))

        finished_shirts.append(shirt)
        shirts.remove(shirt) #remove shirt from the list, which we will use to rebuild 

finally:
    browser.close()
    
    with open('completed/completed.csv','a') as f:
        writer=csv.writer(f, lineterminator='\n')
        for x in finished_shirts:
            writer.writerow(x)
            shutil.move(x[8], "completed/")
    
    if len(finished_shirts) > 0:
        #check if user has file open
        try:
            write_leftovers(header, shirts)
        except:
            while True:
                print("Access to the merchpy.csv file is blocked. Please close the file if you have it open, then type 'Y' and press enter to continue.")
                print("If the file is still not writable (or is deleted), the remaining shirt records will be written to a different file in the directory.")
                i = input()
                if i == 'Y':
                    write_leftovers(header, shirts, True)
                    break
