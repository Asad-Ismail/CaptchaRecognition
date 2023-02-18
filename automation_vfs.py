from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import cv2
import time
import os
from time import sleep
import smtplib
import ssl
from email.message import EmailMessage
import datetime
import re
from bs4 import BeautifulSoup

import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter

PATH="./chromedriver"
MAX_TRYS=10
# For saving captchas for training
links=["https://visa.vfsglobal.com/pak/en/nld/login"]

# Check after these many minures
checkafter=15
checkstatus=30
currtix=0
sleeptime=5

debug_dir="debug"
os.makedirs(debug_dir,exist_ok=True)


def send_message(subject='Nothing',body="Nothing to Update",subtype=None):
    # Define email sender and receiver
    email_sender = 'asadismaeel@gmail.com'
    email_password = 'mgfhptlydaoqhhog'
    email_receiver = ['asadismaeel@gmail.com','kiranriazart@gmail.com']
    #email_receiver ='asadismaeel@gmail.com'
    # Set the subject and body of the email
    #subject = 'Appointment Update'
    #body = """
    #I've just published a new video on YouTube: https://youtu.be/2cZzP9DLlkg
    #"""
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    if subtype:
        em.set_content(body,subtype=subtype)
    else:
        em.set_content(body)
    # Add SSL (layer of security)
    context = ssl.create_default_context()
    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
        

def find_text(content,txt):
    if txt in content:
        return True
    else:
        return False
    
def save_page(content,name="content.html",err=False):
    page = content.encode('utf-8')
    if err:
        file_ = open(os.path.join(f"{debug_dir}",'err.html'), 'wb')
        file_.write(page)
        file_.close()
    else:
        file_ = open(os.path.join(f"{debug_dir}",name), 'wb')
        file_.write(page)
        file_.close()
        

def checkLink(link):
    ## Intially no content in the webpage
    content=None
    try:
        op = webdriver.ChromeOptions()
        op.add_argument('--no-sandbox')
        op.add_argument('--disable-dev-shm-usage')
        op.add_argument("--headless")
        op.add_argument("--incognito")
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        op.add_argument(f'user-agent={user_agent}')

        driver = webdriver.Chrome(PATH,options=op)
        driver.delete_all_cookies()
        #wait = WebDriverWait(driver, 60)
        driver.get(link)
        sleep(sleeptime)
        ## In case the code raise exception write it
        content=driver.page_source

        # Dismiss cookie banner if it exists
        cookie_banner = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "onetrust-consent-sdk")))
        accept_button = cookie_banner.find_element(By.XPATH, '//button[@id="onetrust-accept-btn-handler"]')
        accept_button.click()
        print(f"Accepting Cookies!!")
        #save
        save_page(content)

        email= driver.find_element(By.XPATH,"//input[@formcontrolname='username']")
        email.send_keys("asadismaeel@gmail.com")
        print(f"Sending Email!!")
        sleep(sleeptime)
        passwd = driver.find_element(By.XPATH,'//form//div[text()="Password"]/following-sibling::mat-form-field//input[@formcontrolname="password"]')
        passwd.send_keys("Asad8634!")
        print(f"Sending Password!!")
        sleep(sleeptime)
        submit=driver.find_element(By.XPATH,'//button[normalize-space()="Sign In"]')
        submit.click()
        sleep(sleeptime)
        #save
        content=driver.page_source
        save_page(content,name="content2.html")

        button = driver.find_element(By.XPATH, "//button[contains(.,'Start New Booking')]")
        button.click()
        sleep(sleeptime)
        #save
        content=driver.page_source
        save_page(content,name="content3.html")

        select_element = driver.find_element(By.ID,"mat-select-0")
        select_element.click()
        sleep(sleeptime)
        option_xpath = '//mat-option[contains(.,"Netherlands Lahore")]'
        option_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
        option_element.click()
        sleep(sleeptime)
        #save
        content=driver.page_source
        save_page(content,name="content4.html")

        select_element = driver.find_element(By.ID,"mat-select-value-5")
        select_element.click()
        sleep(sleeptime)
        option_xpath = '//mat-option[contains(.,"Family And Friends Visit")]'
        option_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
        option_element.click()
        sleep(sleeptime)

        content=driver.page_source
        save_page(content,name="content5.html")

        notfound=find_text(content=content,txt="No appointment slots are currently available")
        # status 0 capthca read failes, 1 did not found an appointment, 2 found an appointment
        if notfound:
            # return is status,error
            return False,False
        else:
            return True,False
    except Exception as er:
        print(f"Error exception is {er}")
        if content:
            print(f"Saving Exception Content")
            save_page(content,err=True)
        else:
            print(f"Warning!!"*20)
            print("Content is None")
        return False,True
    


def appointment_call():
    global currtix
    global checkstatus
    foundappointment=False
    checked_links=0
    for link in links:
        for _ in range(MAX_TRYS):
            status,err=checkLink(link)
            if not err:
                foundappointment=status
                break
            else:
                continue
    currtix+=1
    ## Send Email
    #if foundappointment or currtix>=checkstatus:
    if foundappointment:
        e = datetime.datetime.now()
        dt=f"{e.day}/{e.month}/{e.year}"
        tm=f"{e.hour}:{e.minute}:{e.second}"
        subject=f"VFS Report from {dt}--{tm}, Result={foundappointment}"
        HtmlFile = open(f'{debug_dir}/content5.html', 'r', encoding='utf-8')
        body = HtmlFile.read() 
        HtmlFile.close()
        send_message(subject=subject,body=body,subtype='html')
    else:
        body=f"Checked {checked_links}"
        send_message(subject=subject,body=body)
        # reset currtix
        currtix=0
    
    
if __name__=="__main__":
    while True:
        appointment_call()
        sleep(checkafter*60)
