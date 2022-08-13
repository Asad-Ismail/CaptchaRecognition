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
    email_sender = 'asadismaeel@gmail.com'
    email_password = '.NETALICE12'
    email_receiver = 'asadismaeel@gmail.com'

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

def find_text(content,txt="Please enter here the text you see"):
    if content.find(txt):
        return True
        #print("*"*100) 
        #print("Given is present in the webpage")
    else:
        False

def getcaptha(link,outfile):
    driver=webdriver.Chrome(PATH)
    driver.get(link)
    with open(outfile, 'wb') as file:
        file.write(driver.find_element(By.XPATH,"//form[@id='appointment_captcha_month']/div/captcha/div").screenshot_as_png)
    ## Crop unneccassy part
    img=cv2.imread(outfile)
    print(img.shape)
    assert img is not None, "Input image is None"
    img=img[:,:300]
    sleep(1)
    content=driver.page_source
    status=find_text(content=content,txt="Please enter here the text you see")
    assert status==Trues
    
    ## Run the model and get prediction as string in outstr
    #driver.close()
    #inp=input("Enter the Captcha now!!")
    #print(f"You entered {inp}")
    #print(f"Getting Text Box")
    
    textbox=driver.find_element(By.ID,"appointment_captcha_month_captchaText")
    textbox.send_keys(outstr)
    sleep(1)
    print(f"Sending predicted Captchas!!")
    submit = driver.find_element(By.ID,"appointment_captcha_month_appointment_showMonth")
    submit.click()
    sleep(1)
    content=driver.page_source
    status=find_text(content=content,txt="Please enter here the text you see")
    foundappoint=find_text(content=content,txt="Unfortunately, there are no appointments")
    # status 0 capthca read failes, 1 did not found an appointment, 2 found an appointment
    if status:
        return 0
    if !status and foundappoint:
        return 1
    if !status and !foundappoint:
        return 2
    


#for i in range(101,500):
foundappointment=False
checked_links=0
for link in links:
    for _ in range(MAX_TRYS):
        status=getcaptha(link,os.path.join(dst_data,str(i)+".png"))
        if status==1:
            checked_links+=1
            break
        if status==2:
            checked_links+=1
            foundappointemnt=True
            break
    time.sleep(2)
    


e = datetime.datetime.now()
dt=f"{e.day}, {e.month}, {e.year}"
tm=f"{e.hour}, {e.minute}, {e.second}"
subject=f"Login Report from {dt}, {tm}, {foundappointment}"
body=f"Checked Links {checked_links}"
send_message(subject=subject,body=body)


