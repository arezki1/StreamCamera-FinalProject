# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
import threading
import io
import picamera
import logging
from time import sleep
#import SocketServer
import socketserver
from threading import Condition
from http import server
from firebase import firebase
from firebase.firebase import FirebaseApplication
from subprocess import call
from math import isnan
import pyrebase

# handle the page on the HTML frame
PAGE="""\
<html>
<head>
</head>
<body>
<center><img src="stream.mjpg" width="410" height="250"></center>
</body>
</html>
"""
#setting up the configuration of the firebase account
config = {
  "apiKey": "AIzaSyABWZ3dYZZaew1ZzYyZ6e-IZKaA4yCRv5s",
  "authDomain": "final-235115.firebaseapp.com",
  "databaseURL": "https://final-235115.firebaseio.com",
  "projectId": "final-235115",
  "storageBucket": "gs://final-235115.appspot.com"
  
};

#initialise the firebase instance
firebase2 = pyrebase.initialize_app(config)

#get the database instance
db = firebase2.database()
#get an instance of the firebase api
try:
    firebase1 = firebase.FirebaseApplication('https://final-235115.firebaseio.com/', None)
except Exception as e:
    print('Something went wrong:', e)

# define the frame 
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    #this function gets triggered from the button that is on the mobile app
    def cameraOn():
        
         #from here we are seting up the condition to set up the light 
        def stream_text(message):                
            #call the cameraOn method and pass it the value from frebase
            cameraOn(message["data"])
            print(message["data"])
            
        db.child("camera").stream(stream_text)

       
        
        def cameraOn(value):
            
            if(value=="on"):
                
                
                print("the value is ",value)

                try:
                    #take picture and store it in the same directory
                    camera.start_preview()
                    sleep(2)
                    camera.capture('/home/pi/cameraStream/CameraStream/image.jpg')
                    camera.stop_preview()
                except:

                    #stop the camera is there is any error
                    camera.stop_preview()
                    camera.close()

                print("Other image camptured")
               
                #from here we are importing the mail file class to send an email
                import mail as m
                m.mailto()
               
                
                #setting the camera value to off on firebase
                firebase1.post("camera","off")
                

    #start the thread that runs the camera method
    thread1 = threading.Thread(target=cameraOn)
    thread1.start()   

    #start recording the video stream
    camera.start_recording(output, format='mjpeg')
    try:
        #start the server on port 8000 to receive the stream
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    
    except (IOError, TypeError) as e:               
               
                #at last, print the error
                print(" Exited ",str(e))
    except KeyboardInterrupt as e:
              
                 #at last, print the error
                 print(" Exited ",str(e))
    finally:
            #stop recording
            camera.stop_recording()
