from selenium import webdriver
from selenium.webdriver.common.by import By
import cv2
import time
import os
from time import sleep

path="./chromedriver"


def find_text(content):
    texts=["Please enter here the text you see"]
    for txt in texts:
        if content.find(txt):
            print("*"*100) 
            print("Given is present in the webpage")


def getcaptha(link,outfile):
    driver=webdriver.Chrome(path)
    driver.get(link)
    with open(outfile, 'wb') as file:
        file.write(driver.find_element(By.XPATH,"//form[@id='appointment_captcha_month']/div/captcha/div").screenshot_as_png)
    ## Crop unneccassy part
    img=cv2.imread(outfile)
    print(img.shape)
    assert img is not None, "Input image is None"
    img=img[:,:300]
    cv2.imwrite(outfile,img)
    ##
    #sleep(5)
    #print(f"Finding content!!")
    #content=driver.page_source
    #find_text(content=content)
    #driver.close()
    
    #inp=input("Enter the Captcha now!!")
    #print(f"You entered {inp}")
    #print(f"Getting Text Box")
    #textbox=driver.find_element(By.ID,"appointment_captcha_month_captchaText")
    #textbox.send_keys(inp)
    #sleep(5)
    #print(f"Submitting answer!!")
    #submit = driver.find_element(By.ID,"appointment_captcha_month_appointment_showMonth")
    #submit.click()
    #sleep(5)
    #content=driver.page_source
    #sleep(5)
    
    ## if prev is successfull go to this line https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=amst&realmId=1113&categoryId=2324&dateStr=14.09.2022
    


dst_data="/media/asad/8800F79D00F79104/captcha_data"
links=["https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=amst&realmId=1113&categoryId=2324&dateStr=09.08.2022",
       "https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=amst&realmId=1113&categoryId=2324&dateStr=14.09.2022"]

for i in range(101,500):
    #for link in links:
    getcaptha(links[0],os.path.join(dst_data,str(i)+".png"))
    time.sleep(2)
    