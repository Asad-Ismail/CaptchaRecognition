from selenium import webdriver
from selenium.webdriver.common.by import By
import cv2
import time
import os
from time import sleep
import smtplib
import ssl
from email.message import EmailMessage
import datetime

PATH="./chromedriver"
MAX_TRYS=10
# For saving captchas for training
dst_data="/media/asad/8800F79D00F79104/captcha_data"
links=["https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=amst&realmId=1113&categoryId=2324&dateStr=09.08.2022",
       "https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=amst&realmId=1113&categoryId=2324&dateStr=14.09.2022"]

def send_message(subject='Nothing',body="Nothing to Update"):
    # Define email sender and receiver
    email_sender = 'sender email'
    email_password = 'password for your email'
    email_receiver = 'receiver email'
    # Set the subject and body of the email
    #subject = 'Appointment Update'
    #body = """
    #I've just published a new video on YouTube: https://youtu.be/2cZzP9DLlkg
    #"""
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
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

def getcaptha(link,outfile):
    # To run wothout opening the chrome
    #op = webdriver.ChromeOptions()
    #op.add_argument('headless')
    #driver = webdriver.Chrome(PATH,options=op)
    driver=webdriver.Chrome(PATH)
    driver.get(link)
    with open(outfile, 'wb') as file:
        file.write(driver.find_element(By.XPATH,"//form[@id='appointment_captcha_month']/div/captcha/div").screenshot_as_png)
    ## Crop unneccassy part
    img=cv2.imread(outfile)
    #print(img.shape)
    assert img is not None, "Input image is None"
    img=img[:,:300]
    sleep(1)
    content=driver.page_source
    status=find_text(content=content,txt="Please enter here the text you see")
    assert status==True, "WebPage Could Not be Found!!"
    
    ## Run the model and get prediction as string in outstr
    #driver.close()
    outstr=input("Enter the Captcha now!!")
    #print(f"You entered {inp}")
    #print(f"Getting Text Box")
    
    textbox=driver.find_element(By.ID,"appointment_captcha_month_captchaText")
    textbox.send_keys(outstr)
    sleep(3)
    print(f"Sending predicted Captchas!!")
    submit = driver.find_element(By.ID,"appointment_captcha_month_appointment_showMonth")
    submit.click()
    sleep(5)
    #content=""
    content=driver.page_source
    #print(content)
    status=find_text(content=content,txt="Please enter here the text you see")
    foundappoint=find_text(content=content,txt="Unfortunately, there are no appointments")
    sleep(5)
    # status 0 capthca read failes, 1 did not found an appointment, 2 found an appointment
    #print(f"Intital status are {status}, {foundappoint}")
    if status:
        return 0
    if not status and foundappoint:
        return 1
    if not status and not foundappoint:
        return 2
    


#for i in range(101,500):
foundappointment=False
checked_links=0
for link in links:
    for _ in range(MAX_TRYS):
        status=getcaptha(link,os.path.join(dst_data,"test"+".png"))
        #print(status)
        if status==1:
            checked_links+=1
            break
        if status==2:
            checked_links+=1
            foundappointemnt=True
            break
    time.sleep(1)
    

## Send Email to yourself
e = datetime.datetime.now()
dt=f"{e.day}/{e.month}/{e.year}"
tm=f"{e.hour}:{e.minute}:{e.second}"
subject=f"Login Report from {dt}---{tm}, Result={foundappointment}"
body=f"Checked Links {checked_links}"
send_message(subject=subject,body=body)


