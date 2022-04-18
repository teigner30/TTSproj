import serial
import sys
import time
import threading

class Tango:
    MAX_SERVO_POS = 7900  #Max servo position
    MIN_SERVO_POS = 4100  #Minimum servo position
    CENTER_SERVO_POS = (MAX_SERVO_POS + MIN_SERVO_POS) / 2.0
    COUNT = 0
    MAX_MOTOR_POS = 8000  # Max motor speed backwards
    MIN_MOTOR_POS = 4000  # Max motor speed forwards
    CENTER_MOTOR_POS = 6000 #Not in the middle, much to my chagrin
    REVERSE = False
    STOPPED = True
    # Joint Mapping
    joint_ids = {"motor_spd": 1, "motor_dir": 2,
                 "head_twist": 3, "head_tilt": 4,
                 "body_twist": 0}

    # Joint Resolutions
    joint_reses = {"motor_spd": 3,
                    "head_twist": 5,
                    "head_tilt": 5,
                    "body_twist": 3, "motor_dir": 1}

    # Joint States (at initial conditions)
    joint_states = {"motor_spd": 1, "motor_dir": CENTER_SERVO_POS,
                    "head_twist": CENTER_SERVO_POS,
                    "head_tilt": CENTER_SERVO_POS,
                    "body_twist": CENTER_SERVO_POS}

    def __init__(self):
        try:
            self.usb = serial.Serial('/dev/ttyACM0')
        except:
            try:
                self.usb = serial.Serial('/dev/ttyACM1')
            except:
                print("No servo serial ports found")
                sys.exit(0)
        print('set initial positions')
        #TODO: set initial positions here
        self.drive_thread = threading.Thread(target=self.thread_driving)
        self.drive_thread.do_run = False

    def move_joints_to_pos(self):
        for key, val in self.joint_states:
            self.move_joint(key, val)

    def initialize_motors(self):
        self.move_joint('motor_spd', self.CENTER_MOTOR_POS)
        time.sleep(.5)
        self.move_joint('motor_dir', self.CENTER_SERVO_POS)
        time.sleep(0.5)

    def move_joint(self, joint_name: str, position, update_state=True):
        joint_id = self.joint_ids[joint_name]
        position = int(position)
        self.COUNT += 100
        print("Pos: {} {}".format(position, self.COUNT))
        lsb = position & 0x7F
        msb = (position >> 7) & 0x7F
        cmd = chr(0xaa) + chr(0xC) + chr(0x04) + chr(joint_id) + chr(lsb) + chr(msb)
        self.usb.write(cmd.encode('utf-8'))
        if update_state:
             self.joint_states[joint_name] = position
             print("State: {}".format(self.joint_states[joint_name]))

    def drive_tank(self, left, right):
        # TODO: Scale for motors
        self.move_joint('left_motor', left)
        self.move_joint('right_motor', right)

    def start_thread_driving(self, reverse = False):
        self.REVERSE = reverse
        self.STOPPED = False
        self.drive_thread.do_run = True
        if not self.drive_thread.is_alive():
            self.drive_thread.start()
       # self.drive(reverse=reverse)

    def stop_thread_driving(self):
        self.STOPPED = True

    def kill_thread_driving(self):
        self.drive_thread.do_run = False

    def thread_driving(self):
        SLEEP_TIME = 0.5
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            self.drive(reverse=self.REVERSE)
            time.sleep(SLEEP_TIME)

    def drive_arcade(self, throttle, rot):
        self.drive_tank((throttle - rot) / 2.0, (throttle + rot) / 2.0)


    def twist_head(self, rot: int):
        pos = self.scale_servo_rot(rot, 5)
        self.move_joint('head_twist', pos)

    def twist_body(self, rot: int):
        pos = self.scale_servo_rot(rot, 3)
        self.move_joint('body_twist', pos)

    def tilt_head(self, rot: int):
        pos = self.scale_servo_rot(rot, 5)
        self.move_joint('head_tilt', pos)

    def increment_joint(self,joint_name, reverse=False):
        if (not reverse and not (self.joint_states[joint_name] == self.MAX_SERVO_POS)) or (reverse and not (self.joint_states[joint_name] == self.MIN_SERVO_POS)):
            inc_val = self.get_servo_scale_increment(self.joint_reses[joint_name]) * (-1 if reverse else 1)
            pos = int(self.joint_states[joint_name] + inc_val)
            self.move_joint(joint_name, pos)

    #TODO: add functionality to increment speed up to the max, right now it just goes to the max
            #further added functinality needs to check the joint state and not set the joint back
            #to center if the button is held and repeatedly calls this function
    def drive(self, reverse=False):
        #self.move_joint('motor_spd', 1000)
        #self.move_joint('motor_dir',self.CENTER_MOTOR_POS)
        if self.STOPPED:
            self.move_joint('motor_spd', self.CENTER_MOTOR_POS, update_state=False)
            return
        if not reverse:
            self.move_joint('motor_spd', (self.CENTER_MOTOR_POS - (self.CENTER_MOTOR_POS - self.MIN_MOTOR_POS)/self.joint_reses['motor_spd'] * self.joint_states['motor_spd']), update_state=False)
        else:
            self.move_joint('motor_spd', (self.CENTER_MOTOR_POS + (self.MAX_MOTOR_POS - self.CENTER_MOTOR_POS)/ self.joint_reses['motor_spd'] * self.joint_states['motor_spd']), update_state=False)
    #TODO: add functionality to decrement spd so it doesn't just stop all at once and tip
    def stop_drive(self):
        print("STOPPING DRIVE")
        self.move_joint('motor_spd',self.CENTER_MOTOR_POS, update_state=False)
        self.STOPPED = True

    def turn(self, left=True):
       self.move_joint('motor_dir', self.CENTER_MOTOR_POS)

       if not left:
           self.move_joint('motor_dir', self.MIN_SERVO_POS)
       else:
           self.move_joint('motor_dir',self.MAX_SERVO_POS)

    #TODO create a method that returns all motors and servos to center position
    def stop_turn(self):
        self.move_joint('motor_dir', self.CENTER_SERVO_POS)
        print("STOPPING TURN")
    def reset_positions(self):
        SLEEP_TIME = .2
        print("motor_dir")
        self.move_joint('motor_dir', self.CENTER_SERVO_POS)
        time.sleep(SLEEP_TIME)
        print("speed")
        self.move_joint('motor_spd', 1)
        time.sleep(SLEEP_TIME)
        print("head twist")
        self.move_joint('head_twist', self.CENTER_SERVO_POS)
        time.sleep(SLEEP_TIME)
        print("head tilt")
        self.move_joint('head_tilt', self.CENTER_SERVO_POS)
        time.sleep(SLEEP_TIME)
        print("body twist")
        self.move_joint('body_twist', self.CENTER_SERVO_POS)
        time.sleep(SLEEP_TIME)
        print("STOPPING MOTORS")
        self.stop_drive()

    def set_speed(self, speed):
        speed = min(max(1, speed), 3)
        self.joint_states['motor_spd'] = speed

    #It did not seem like we needed this, so I commented it out when debugging
   # @classmethod
   # def scale_motor_speeds(cls):

    #@classmethod
    def scale_servo_rot(cls, rot: int, res: int):
        servo_increments = cls.get_servo_scale_increment(res)
        return max(min(cls.CENTER_SERVO_POS + rot * servo_increments, cls.MAX_SERVO_POS), cls.MIN_SERVO_POS)

    #@classmethod
    def get_servo_scale_increment(cls, res: int):
        return (cls.MAX_SERVO_POS - cls.MIN_SERVO_POS) / (float(res)-1)

