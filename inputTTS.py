from Tango import *
import speech_recognition as sr
import _thread, threading
# Create motor controller
c = Tango()
TEXT_MODE = False
def on_begin():
    listening = True
    c.reset_positions()
    time.sleep(1)
    c.initialize_motors()
    while listening:
        with sr.Microphone() as source:
            r = sr.Recognizer()
            r.adjust_for_ambient_noise(source)
            r.dynamic_energythreshold = 3000
            try:
                if TEXT_MODE:
                    print("Waiting for text input")
                    word = input()
                else:
                    print("listening")
                    audio = r.listen(source)
                    print("Got audio")
                    word = r.recognize_google(audio).lower()
                print(word)
                x = process_word(word)
                if x == 1:
                    return
            except sr.UnknownValueError:
                print("I don't know that word")

def process_word(word):
    if word == "look left":
        print('look left')
        #move head left
        c.increment_joint('head_twist',reverse=False)
    elif word == "look right":
        print('look right')
        #move head right
        c.increment_joint('head_twist',reverse=True)
    elif word  == "look up":
        print('look up')
        #move head up
        c.increment_joint('head_tilt',reverse=False)
    elif word == "look down":
        print('look down')
        #move head down
        c.increment_joint('head_tilt',reverse=True)
    elif word == "body left":
        print('body left')
        #move waist left
        c.increment_joint('body_twist',reverse=False)
    elif word == "body right":
        print('body right')
        #move waist right
        c.increment_joint('body_twist',reverse=True)
    elif word == "move forward":
        print('move forward')
        #move forward
       # c.stop_thread_driving()
        c.start_thread_driving(reverse = False)
    elif word == "move back":
        print('move backwards')
       # c.stop_thread_driving()
        #move backwards
        c.start_thread_driving(reverse = True)
    elif word == "stop":
        print("STOPING")
        c.stop_drive()
        #c.stop_thread_driving()
    elif word == "turn left":
        print('rotate left')
        #c.increment_joint('motor_dir', reverse = False)
        c.turn(left = True)
        #rotate left
    elif word == "turn right":
        print('rotate right')
        c.turn(left = False)
        #c.increment_joint('right_motor', reverse = False)
        #rotate right
        #TODO add a call to c.____

    elif word == "reset":
        print('reset positions')
        #reset servo and motor positions
        c.reset_positions()
        try:
            _threading.start_new_thread(c.reset_positions(), ())
        except:
            print("Unable to start thread")
    elif word == "speed one" or word == "speed 1":
        print("Speed 1...")
        c.set_speed(1)
    elif word == "speed two" or word == "speed 2" or word == "speed to" or word == "speed too":
        print("Speed 2")
        c.set_speed(2)
    elif word == "speed three" or word == "speed 3":
        print("Speed 3")
        c.set_speed(3)
    elif word == "exit":
        c.kill_thread_driving()
        return 1
    else:
        print("Unknown Command")

on_begin()
