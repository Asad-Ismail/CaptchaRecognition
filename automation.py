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
links=["https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=amst&realmId=1113&categoryId=2324&dateStr=09.08.2022",
       "https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=amst&realmId=1113&categoryId=2324&dateStr=14.09.2022"]




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
    results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][
        :, :max_length
    ]
    # Iterate over the results and get back the text
    output_text = []
    for res in results:
        res = tf.strings.reduce_join(num_to_char(res)).numpy().decode("utf-8")
        output_text.append(res)
    return output_text


def send_message(subject='Nothing',body="Nothing to Update"):
    # Define email sender and receiver
    email_sender = ''
    email_password = ''
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
        

def find_text(content,txt):
    if txt in content:
        return True
    else:
        return False

def getcaptha(link,outfile):
    # To run wothout opening the chrome
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(PATH,options=op)
    #driver=webdriver.Chrome(PATH)
    driver.get(link)
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
    #print(pred_texts)
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
    #print(content)
    #print(f"Intital status are {status}, {foundappoint}")
    if status:
        return 0,"None"
    if not status and foundappoint:
        return 1,"None"
    if not status and not foundappoint:
        #print(content)
        soup=BeautifulSoup(content,"html.parser")
        heading_tags = ["h4"]
        all_dates=[]
        for tags in soup.find_all(heading_tags):
            #print(tags.name + ' -> ' + tags.text.strip())
            all_dates.append(tags.text.strip())
        #print(f"All dates are {all_dates}")
        return 2,' '.join(all_dates)
    


#for i in range(101,500):

def appointment_call():
    foundappointment=False
    checked_links=0
    dates=[]
    for link in links:
        for _ in range(MAX_TRYS):
            status,currdate=getcaptha(link,os.path.join(dst_data,"test"+".png"))
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
        time.sleep(1)
    ## Send Email to yourself
    e = datetime.datetime.now()
    dt=f"{e.day}/{e.month}/{e.year}"
    tm=f"{e.hour}:{e.minute}:{e.second}"
    subject=f"Login Report from {dt}---{tm}, Result={foundappointment} Dates are {' '.join(dates)}"
    body=f"Checked Links {checked_links}"
    send_message(subject=subject,body=body)
    
    
if __name__=="__main__":
    while True:
        appointment_call()
        sleep(600)
