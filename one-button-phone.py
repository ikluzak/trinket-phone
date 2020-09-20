#
# Ivan's super awesome one button phone...
#
import board
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogOut, AnalogIn
import busio
import touchio
#from adafruit_hid.keyboard import Keyboard
#from adafruit_hid.keycode import Keycode
import adafruit_dotstar as dotstar
import time
#import neopixel

print("Good morning!\n")

# Serial connection to the FONA
# The example I saw used board.TX and board.RX but I couldn't get that to work...
uart = busio.UART(board.D4, board.D3, baudrate=115200)
uart.write("AT\r\n")
time.sleep(0.5)
uart.write("AT\r\n")
time.sleep(0.5)
uart.write("ATI\r\n")
time.sleep(0.5)
uart.write("AT+CVHU=0\r\n")
time.sleep(0.5)
print("UART is open...")

# One pixel connected internally!
#dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.005)
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.005)

# Built in red LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Analog input on D0
analog1in = AnalogIn(board.D0)

# Analog output on D1
#aout = AnalogOut(board.D1)

# Digital input with pullup on D2
button = DigitalInOut(board.D2)
button.direction = Direction.INPUT
button.pull = Pull.UP

# we are not in a call
on_a_call = 0
# the phone is not ringing
ringing = 0

# Used if we do HID output, see below
#kbd = Keyboard()

######################### HELPERS ##############################

# Helper to convert analog input to voltage
def getVoltage(pin):
    return (pin.value * 3.3) / 65536

# Helper to give us a nice color swirl
#def wheel(pos):
#    # Input a value 0 to 255 to get a color value.
#    # The colours are a transition r - g - b - back to r.
#    if (pos < 0):
#        return (0, 0, 0)
#    if (pos > 255):
#        return (0, 0, 0)
#    if (pos < 85):
#        return (int(pos * 3), int(255 - (pos*3)), 0)
#    elif (pos < 170):
#        pos -= 85
#        return (int(255 - pos*3), 0, int(pos*3))
#    else:
#        pos -= 170
#        return (0, int(pos*3), int(255 - pos*3))

######################### MAIN LOOP ##############################

# Default to red, not in a call
dot[0] = (255,0,0)

i = 0
while True:

    # This reads a byte array...
    data = uart.read(64)
    #print(data)

    # convert to string
    if data is not None:
        data_string = ''.join([chr(b) for b in data])
        print(data_string, end="")
        print("\n")
    
  # spin internal LED around! autoshow is on
  # So this is basically R, G, B I guess...
  #dot[0] = (255, 0, 0)
  #dot[0] = (0,0,0)
#  dot[0] = wheel(i & 255)

  # also make the neopixels swirl around
#  for p in range(NUMPIXELS):
#      idx = int ((p * 256 / NUMPIXELS) + i)
#      neopixels[p] = wheel(idx & 255)
#  neopixels.show()

  # set analog output to 0-3.3V (0-65535 in increments)
#  aout.value = i * 256

  # Read analog voltage on D0
  #print("D0: %0.2f" % getVoltage(analog1in))
  #print("testing...")
    
    if "VOICE CALL: END:" in data_string:
        # hang up the call, set the LED to red again... 
        print("Call ended")
        on_a_call = 0
        # set display to red
        dot[0] = (255,0,0)
        data_string = ""
        
    if "RING" in data_string:
        print("Phone is ringing")
        ringing = 1
        data_string = ""
        
    if "VOICE CALL: BEGIN" in data_string:
        print("Voice call begin")
        on_a_call = 1
        ringing = 0
        dot[0] = (0,255,0)
        data_string = ""
        
    if not button.value:
        led.value = 255
        print("Button pressed")
        print("On a call status: ", on_a_call)
        #print("Button on D2 pressed!")
        #led.value = 255
        if not on_a_call:
            #
            # We want to make a phone call OR if the phone is ringing we want to answer it...
            if ringing:
                print("Answering the call")
                uart.write("ATA\r\n")
                #on_a_call = 1
                #dot[0] = (0,255,0)
                #data_string = ""
            else:
                # for now assume we are making a call only...
                print("We are making a call...")
                # here we could dial the phone number
                # "ATD5551234567;"
                uart.write("ATD5551235555;\r\n")
                #uart.write("ATI\n")
          
                # look for the +OK
                #on_a_call = 1
                # set display to GREEN
                dot[0] = (255,255, 0)
                #
        else:
            # we want to end the call
            print("Hanging up...")
            # "ATH"
            uart.write("ATH\r\n")
            # look for the +OK
            on_a_call = 0
            # set display to red
            dot[0] = (255,0,0)

        # optional! uncomment below & save to have it sent a keypress
        #kbd.press(Keycode.A)
        #kbd.release_all()
    else:
        led.value = 0

    i = (i+1)
    if i > 10: 
        i = 0
        print("Hi there... 10 loops\n")
#  i = (i+1) % 256  # run from 0 to 255
  #time.sleep(0.75) # make bigger to slow down
  #time.sleep(1)
  #time.sleep(0.01)

