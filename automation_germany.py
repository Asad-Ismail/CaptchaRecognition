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
import re
from bs4 import BeautifulSoup

## Tensorflow stuff
import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import time

img_width = 300
img_height = 50
max_length=  6
characters = ['2', '3', '4', '5', '6', '7', '8', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
char_to_num = layers.StringLookup(vocabulary=list(characters), mask_token=None)

# Mapping integers back to original characters
num_to_char = layers.StringLookup(vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True)

model = keras.models.load_model('newcaptcha_model.tf')
prediction_model = keras.models.Model( model.get_layer(name="image").input, model.get_layer(name="dense2").output)
prediction_model.summary()

PATH="./chromedriver"
MAX_TRYS=10
# For saving captchas for training
dst_data="./"
## amsterdam
#links=["https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=amst&realmId=1113&categoryId=2324",
#       "https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=amst&realmId=1113&categoryId=2324&dateStr=03.05.2023"]
# Ismbd
links=["https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=isla&realmId=108&categoryId=203",
      "https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=isla&realmId=108&categoryId=203&dateStr=03.03.2023",
      "https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=isla&realmId=108&categoryId=203&dateStr=03.05.2023"]

checkstatus=100
currtix=0


def encode_image(img_path):
    # 1. Read image
    img = tf.io.read_file(img_path)
    # 2. Decode and convert to grayscale
    img = tf.io.decode_png(img, channels=1)
    # 3. Convert to float32 in [0, 1] range
    img = tf.image.convert_image_dtype(img, tf.float32)
    # 4. Resize to the desired size
    img = tf.image.resize(img, [img_height, img_width])
    # 5. Transpose the image because we want the time
    # dimension to correspond to the width of the image.
    img = tf.transpose(img, perm=[1, 0, 2])
    img=tf.expand_dims(img, axis=0)
    # 6. Map the characters in label to numbers
    # 7. Return a dict as our model is expecting two inputs
    return img

def decode_batch_predictions(pred):
    input_len = np.ones(pred.shape[0]) * pred.shape[1]
    # Use greedy search. For complex tasks, you can use beam search
    results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][:, :max_length]
    # Iterate over the results and get back the text
    output_text = []
    for res in results:
        res = tf.strings.reduce_join(num_to_char(res)).numpy().decode("utf-8")
        output_text.append(res)
    return output_text


def send_message(receipents,subject='Nothing',body="Nothing to Update",subtype=None):
    # Define email sender and receiver
    email_sender = 'asadismaeel@gmail.com'
    email_password = 'mgfhptlydaoqhhog'
    email_receiver = receipents
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
        file_ = open('err.html','wb')
        file_.write(page)
        file_.close()
    else:
        file_ = open(name,'wb')
        file_.write(page)
        file_.close()
        

def getcaptha(link,outfile):
    ## Intially no content in the webpage
    content=None
    try:
        # To run wothout opening the chrome
        op = webdriver.ChromeOptions()
        #op.add_argument('--no-sandbox')
        #op.add_argument('--disable-dev-shm-usage')
        op.add_argument("--headless")
        op.add_argument("--incognito")
        #user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
        #op.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome(PATH,options=op)
        #driver.delete_all_cookies()
        #op = webdriver.ChromeOptions()
        #op.add_argument('headless')
        driver = webdriver.Chrome(PATH,options=op)
        #driver=webdriver.Chrome(PATH)
        driver.get(link)
        ## In case the code raise exception write it
        content=driver.page_source
        with open(outfile, 'wb') as file:
            file.write(driver.find_element(By.XPATH,"//form[@id='appointment_captcha_month']/div/captcha/div").screenshot_as_png)
        ## Crop unneccassy part
        img=cv2.imread(outfile)
        #print(img.shape)
        assert img is not None, "Input image is None"
        img=img[:,:300]
        cv2.imwrite(outfile,img)
        sleep(1)
        content=driver.page_source
        status=find_text(content=content,txt="Please enter here the text you see")
        assert status==True, "WebPage Could Not be Found!!"
        ## Run the model and get prediction as string in outstr
        #driver.close()
        #outstr=input("Enter the Captcha now!!")
        tf_img=encode_image(outfile)
        preds = prediction_model.predict(tf_img)
        outstr = decode_batch_predictions(preds)[0]
        textbox=driver.find_element(By.ID,"appointment_captcha_month_captchaText")
        textbox.send_keys(outstr)
        sleep(1)
        print(f"Sending predicted Captchas!!")
        submit = driver.find_element(By.ID,"appointment_captcha_month_appointment_showMonth")
        submit.click()
        sleep(1)
        content=driver.page_source
        status=find_text(content=content,txt="Please enter here the text you see")
        foundappoint=find_text(content=content,txt="Appointments are available")
        save_page(content)
        # status 0 capthca read failes, 1 did not found an appointment, 2 found an appointment
        if status:
            return 0,"None"
        if not status and not foundappoint:
            return 1,"None"
        if not status and foundappoint:
            save_page(content,"found.html")
            #print(f"All dates are {all_dates}")
            return 2,'Some'
    except Exception as er:
        print(f"Error exception is {er}")
        if content:
            print(f"Saving Exception Content")
            save_page(content,err=True)
        else:
            print(f"Warning!!"*20)
            print("Content is None")
        return 0,"None"
    
def appointment_call():
    global currtix
    global checkstatus
    foundappointment=False
    checked_links=0
    dates=[]
    for link in links:
        for _ in range(MAX_TRYS):
            status,currdate=getcaptha(link,os.path.join(dst_data,"test"+".png"))
            print(f"Returned status is {status}")
            if currdate!="None":
                dates.append(currdate)
            #print(status)
            if status==1:
                checked_links+=1
                break
            if status==2:
                checked_links+=1
                foundappointment=True
                break
    currtix+=1
    print(f"Current Index is {currtix}")
    ## Send Email
    if foundappointment or currtix>=checkstatus:
        print(f"Sending Email!!")
        e = datetime.datetime.now()
        dt=f"{e.day}/{e.month}/{e.year}"
        tm=f"{e.hour}:{e.minute}:{e.second}"
        subject=f"Login Report from {dt}---{tm}, Result={foundappointment} Dates are {' '.join(dates)}"
        if foundappointment:
            print(f"Sending Alert!!")
            HtmlFile = open('found.html', 'r', encoding='utf-8')
            body = HtmlFile.read() 
            HtmlFile.close()
            #email_receiver = ['asadismaeel@gmail.com']
            email_receiver = ['Kiran_riaz_88@hotmail.com','kiranriazart@gmail.com','Omar.rana87@outlook.com',"bismairfanmalik13@gmail.com"]
            send_message(email_receiver,subject=subject,body=body,subtype='html')
        else:
            body=f"Checked {checked_links} Months for appointment"
            email_receiver = ['asadismaeel@gmail.com']
            send_message(email_receiver,subject=subject,body=body,subtype=None)
        # reset currtix
        currtix=0
    
    
if __name__=="__main__":
    while True:
        start=time.monotonic()
        appointment_call()
        end=time.monotonic()
        print(f"Time to check all links is {(end-start)/60} minutes")
        #sleep(6)
