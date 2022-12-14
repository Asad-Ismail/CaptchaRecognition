# CaptchaRecognition Dataset and Model
 
The contribution of this is work is follows

1) We present custom Captcha Dataset with 5 characters per captcha
2) Trained the Deep learning model for Captcha recognition
3) Deploy the resulting model to read Captchas and automate the appointment system

## Dataset

You can download the 5 digit Captcha dataset from this link 
Few examples of the dataset are shown below
<p align="center">
  <img alt="Light" src="vis_imgs/6mn8n.png" width="25%">
&nbsp; &nbsp; &nbsp; &nbsp;
  <img alt="Dark" src="vis_imgs/8eggg.png" width="25%">
</p>
<p align="center">
  <img alt="Light" src="vis_imgs/be3bp.png" width="25%">
&nbsp; &nbsp; &nbsp; &nbsp;
  <img alt="Dark" src="vis_imgs/bw44w.png" width="25%">
</p>
<p align="center">
  <img alt="Light" src="vis_imgs/pgwnp.png" width="25%">
&nbsp; &nbsp; &nbsp; &nbsp;
  <img alt="Dark" src="vis_imgs/8n4n8.png" width="25%">
</p>


https://drive.google.com/drive/folders/1NS9CBTT-bu7Uegc6t2jn3Xg3m8iUtsZz?usp=sharing

## Model Training
Please see the train_captcha.ipynb notebook to train the captcha recognition model on the given dataset. The model is quite simple using 2 bidirectional LSTM and CTC loss to recgnize captchas. The model has quite low latency and was able to recognize captchas on online test very accuractely

## Automatic appointment system
The script automation.py uses the trained captcha recognition model and use it to recognize captchas on website and check if the appointment is available. If the appointment is availbale it sends the email to the receiver. The automation is done particularly for one type of website but can be used as blue print to automate appointmet/alret system for any other website/service.
