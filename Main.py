from picamera2 import Picamera2, Preview
from roboflow import Roboflow
from gpiozero import LED
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from PIL import Image, ImageEnhance
from imutils.video import VideoStream
import time
import os
import smtplib
import glob
import datetime
import cv2
import random
import datetime
from suntime import Sun, SunTimeException
import pytz


####################################################################
def play_random_sounds(count, repeat):

file_list = glob.glob("sounds/*wav")
random.shuffle(file_list)

for i in range(0,count) :
for j in range(0,repeat):
cmd = f"cvlc --alsa-audio-device jack --play-and-exit {file_list[i]}"
os.system(cmd)
time.sleep(1)


####################################################################
def log_msg(msg_type,msg) :

now = datetime.datetime.now().strftime("%H:%M:%S")
print (f"{now} [{msg_type}] {msg}")


####################################################################
def get_USB_camera_img(image_file):


# v4l2-ctl -d 2 --list-ctrls
# v4l2-ctl -d 2 --list-formats-ext

#cam = cv2.VideoCapture(usb_cam_id)  # top USB 2.0 port
#cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#cam.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
#ret, image = cam.read()
#cv2.imwrite(image_file, image)
#cam.release()

# Cannot get good resolution with cv2

if os.path.exists(image_file) : os.remove(image_file)

cmd = f"fswebcam -r 1280x720 --no-banner {image_file} -d /dev/video{usb_cam_id}"
os.system(cmd)

if os.path.exists(image_file) :
return image_file

return False

####################################################################
def get_IPcam1 (image_file) :

try :
rtsp_url = "rtsp://Goosecam1:Busted@192.168.7.32/live"
vs = VideoStream(rtsp_url).start()    # Open the RTSP stream

frame = vs.read()
cv2.imwrite(image_file,frame)

vs.stop()
return image_file
except :
log_msg ('ERROR', 'Could not capture image from IP camera 1')
return False


####################################################################
def get_IPcam2 (image_file) :

try :
rtsp_url = "rtsp://Goosecam2:Busted@192.168.7.31/live"
vs = VideoStream(rtsp_url).start()    # Open the RTSP stream

frame = vs.read()
cv2.imwrite(image_file,frame)

vs.stop()

except:
log_msg ('ERROR', 'Could not capture image from IP camera 2')
return False


####################################################################
def get_picam_img(image_file):

try:
picam2.capture_file(image_file)

except :
log_msg ('ERROR', 'Could not capture image from Pi camera')
return False

return image_file

####################################################################
def get_nest_img(image_file):

#cmd = f"/home/enzo/.local/share/go/bin/nest2img -token bbU028ioHg -password Nest2Rasberry! -width 1024 -out {image_file}"  # Front
cmd = f"/home/enzo/.local/share/go/bin/nest2img -token cT9Tt8J8Ss -password Nest2Rasberry! -width 1024 -out {image_file}" # living room

try:
os.system(cmd)

except :
log_msg ('ERROR', 'Could not download image from Nest')
return False

return image_file

######################################################################
def crop_enhance(image_file , x , y, width, height , cropOnly = False ):

image = Image.open(image_file)
image = image.crop((x,y,x+width,y+height))

if cropOnly :
image.save(image_file) # overwrite
else:
enhancer = ImageEnhance.Brightness(image)
new_image_bright = enhancer.enhance(1.5)
enhancer = ImageEnhance.Sharpness(new_image_bright)
new_image_both = enhancer.enhance(1.4)
new_image_both.save(image_file) # overwrite

######################################################################
def resize_picture(filename):

if os.path.exists(filename):
img=cv2.imread(filename)
ratio = 640 / img.shape[1]
small_img = cv2.resize(img,None,fx = ratio,fy = ratio)
cv2.imwrite(filename, small_img)

######################################################################
def activate_airdancer(nb_secs) :

relay1.off()
time.sleep (nb_secs)
relay1.on()

######################################################################
def sendmail(recipient, subject, content,filename = False):

try:

msg = MIMEMultipart('mixed')
msg.attach( MIMEText(content))

if filename and os.path.exists(filename) :
fil = open(filename,'rb')
part = MIMEApplication(fil.read(),Name=os.path.basename(filename))
part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filename)}"'
msg.attach(part)


msg['Subject'] = subject
msg['To'] = recipient
msg['From'] = GMAIL_USERNAME

log_msg('INFO',f"Sending email {subject} to {recipient}")

#Connect to Gmail Server
session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
session.ehlo()
session.starttls()
session.ehlo()

#Login to Gmail
session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

#Send Email & Exit
session.sendmail(GMAIL_USERNAME, recipient, msg.as_string())
session.quit

except :
log_msg('ERROR','Could not send email')

######################################################################
def draw_rectangle( image_file , predictions ):

try:
image = cv2.imread(image_file)

for bounding_box in predictions :
x0 = int( bounding_box['x'] - bounding_box['width'] / 2 )
x1 = int ( bounding_box['x'] + bounding_box['width'] / 2 )
y0 = int (bounding_box['y'] - bounding_box['height'] / 2 )
y1 = int (bounding_box['y'] + bounding_box['height'] / 2 )
print ('Bounding box', bounding_box , x0, x1 , y0, y1 )

start_point = (int(x0), int(y0))
end_point = (int(x1), int(y1))
cv2.rectangle(image, start_point , end_point, color=(255,0,0) , thickness =2 )
print (x0,x1,y0,y1)
cv2.putText(image,f"{bounding_box['confidence']*100:.0f}%",(x0+10,y1-5),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,0,0),1,1)  

new_filename = image_file.replace('.jpeg','.box.jpg')
cv2.imwrite(new_filename, image)
return new_filename
except :
print ('ISSUE WITH BOX')
return image_file

def GetSunRiseTime () :
latitude = 41.466068
longitude = -73.485611

sun = Sun(latitude, longitude)

# Get today's sunrise and sunset in UTC
today_sr = sun.get_sunrise_time()
today_ss = sun.get_sunset_time()
est = pytz.timezone('US/Eastern')
today_sr_est = today_sr.astimezone(est).strftime('%H:%M')
today_ss_est = today_ss.astimezone(est).strftime('%H:%M')

log_msg( "INFO" , f"Today the sun raised at {today_sr_est} and get down at {today_ss_est} EST")


return (today_sr_est , today_ss_est)

#def GetRandomTimes (Start_Time, Stop_Time, Interval , Nb_events ) :

 
##########################################################################
###                 MAIN
##########################################################################

log_msg ('INFO',"Init Relay 1")
relay1 = LED(26)
relay1.on()


if __name__ == '__main__' :

# Set log level for PiCamera
# "0" - DEBUG, "1" - INFO, "2" - WARN, "3" - ERROR, "4" - FATAL
os.environ["LIBCAMERA_LOG_LEVELS"] = "3"

#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME = 'goosebuster45@gmail.com' #change this to match your gmail account
GMAIL_PASSWORD = 'zfvh impa eepz xthc'  #change this to match your gmail app-password

# Config
LOOP_DELAY = 20
MAX_COUNT = 3
SNOOZE_MAX_COUNT = 600
START_TIME,STOP_TIME = GetSunRiseTime ()
LOW_LIGHT_START_TIME = '08:00'
LOW_LIGHT_STOP_TIME = "19:00"
LOW_LIGHT_CORRECTION = 5
MAX_FILES = 2000
RANDOM_EVENTS = 5 # 0 to disable

SOURCES = {
'PiCam' : ('get_picam_img',65 ,0,1500,3280,850) ,
'Webcam': ( 'get_USB_camera_img', 60 ,0,390,1280,330) ,
'IPCam1': ( 'get_IPcam1', 65 ,0,300,1920,780) ,
'IPCam2': ( 'get_IPcam2', 60 ,0,180,1920,900) ,

#'Nest' : ( 'get_nest_img', 60, 0 ,200,1024,376) ,
}



log_msg('INFO', "Starting Pi camera")
Picamera2.set_logging(Picamera2.ERROR)
picam2 = Picamera2()
capture_config = picam2.create_still_configuration()
picam2.configure(capture_config)
picam2.start()

log_msg('INFO', "Scanning USB camera")
for usb_cam_id in range(0,5) :
if get_USB_camera_img('test.jpg') :
log_msg('INFO', f"Found USB camera on /dev/video{usb_cam_id}")
break
else:
log_msg('WARNING', "No USB Cam found")
del SOURCES['Webcam']



log_msg ('INFO',"Starting roboflow, connecting to inference server")
rf = Roboflow(api_key="###")
project = rf.workspace().project("goosebuster")
model = project.version(4, local="http://localhost:9001/").model

total_loops = ( datetime.datetime.strptime(STOP_TIME,"%H:%M") - datetime.datetime.strptime(START_TIME,"%H:%M") ).seconds / LOOP_DELAY


events_today = {}
random_events_today = []

log_msg('INFO',f"Capturing images between {START_TIME} and {STOP_TIME} evening {LOOP_DELAY} seconds ({total_loops} loops)")

evening_cleanup = False
snooze_active = SNOOZE_MAX_COUNT


while True:

for source in SOURCES :
capture_function , min_confidence ,crop_x ,crop_y, crop_width, crop_height = SOURCES[source]

now = datetime.datetime.now().strftime("%H:%M:%S")
today = datetime.datetime.now().strftime("%Y%m%d")
start_time = time.time()

if now > START_TIME and now < STOP_TIME :

if now < LOW_LIGHT_START_TIME: min_confidence += LOW_LIGHT_CORRECTION
if now > LOW_LIGHT_STOP_TIME: min_confidence += LOW_LIGHT_CORRECTION

evening_cleanup = False

# Random alerts
if random.randint(1,total_loops) <= RANDOM_EVENTS :

if len(random_events_today) < RANDOM_EVENTS :
random_events_today.append(now[:5])
log_msg('ALERT',f"Triggering random alert {len(random_events_today)}")
if random.randint(0,1) == 0 :
play_random_sounds(2,4)
else:
activate_airdancer(60)


log_msg('INFO',f'Capturing image from {source}')

capture_file = globals()[capture_function](f"images/{today}_{now}_{source}.jpeg")

if capture_file and os.path.exists(capture_file) :

if source.startswith('IPCam') :
crop_enhance(capture_file,crop_x ,crop_y, crop_width, crop_height , cropOnly = True )  # IP Cam do better in low light
else:
crop_enhance(capture_file,crop_x ,crop_y, crop_width, crop_height)

try:
prediction = model.predict(capture_file).json()
except :
print ('ERROR', 'Cannot get prediction')
prediction = {}

log_msg('INFO','Roboflow model predicitions: ' + str(prediction) )

if "predictions" in prediction and prediction["predictions"] != [] :

goose_count = len( prediction["predictions"] )
best_confidence = 0
for pred in prediction['predictions'] :
if pred['class'] == 'Baby Canada Goose' : continue  # Not reliable
if pred['width'] / pred['height'] > 1.75 : continue # to skip large rectangles
if pred['width'] < 75 and pred['height'] < 75 : continue  # Skip small objects
best_confidence = max(best_confidence,pred['confidence'])

new_file = draw_rectangle(capture_file,prediction['predictions'])

if best_confidence > min_confidence :
events_today[now[:5]] = int(best_confidence)
events = len(events_today)
alert_msg = f"Goosebuster Event {events} Detected {goose_count} goose from {source}"
log_msg('ALERT', alert_msg)
sendmail('guillaume.bouvet@gmail.com', alert_msg, f'Predicition: {str(prediction)}', new_file)
play_random_sounds(5,3)
activate_airdancer(120)

if events > MAX_COUNT :
log_msg('WARNING','Max event count reached, Slowing down')
time.sleep(snooze_active)
snooze_active *= 2
else:
log_msg('INFO',f"Prediction confidence {best_confidence:.1f} too low compare to threshold {min_confidence:d}")

#else:
# resize_picture(capture_file)

# Clean up file
for n,filename in enumerate( sorted(os.listdir('images'), reverse=True) ) :
if n > MAX_FILES :
os.remove('images/' + filename)


else:
log_msg('INFO','Outside capture time window, Zzzzzzz...')

if evening_cleanup == False :
evening_cleanup = True

summary = f"Number of random events triggered :{len(random_events_today)}\n"
summary += f"Times of random events :{','.join(random_events_today)}\n"
summary += f"Number of events detected : {len(events_today)}\n"
summary += f"Detail of events : {str(events_today)}\n"
sendmail('guillaume.bouvet@gmail.com', f'Goosebuster {today} EOD Summary', summary)
events_today = {}
random_events_today = []
snooze_active = SNOOZE_MAX_COUNT
START_TIME,STOP_TIME = GetSunRiseTime ()


exec_time = time.time()-start_time
if exec_time > 0.1 : print ('INFO', f"Loop took {exec_time:.1f} seconds")
time.sleep( max(0,LOOP_DELAY-exec_time) )






picam2.stop_preview()
picam2.close()
