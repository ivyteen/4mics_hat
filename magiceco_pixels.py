
import speech_recognition as sr
from matplotlib import colors
import apa102
import time
import threading
from gpiozero import LED
try:
    import queue as Queue
except ImportError:
    import Queue as Queue

#from alexa_led_pattern import AlexaLedPattern
from magiceco_led_pattern import MagicEcoLedPattern

class Pixels:
    PIXELS_N = 12

    def __init__(self, pattern=MagicEcoLedPattern):
        self.pattern = pattern(show=self.show, show_odd_pixel=self.show_odd_pixel)

        self.dev = apa102.APA102(num_led=self.PIXELS_N)
        
        self.power = LED(5)
        self.power.on()

        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

        self.last_direction = None

    def wakeup(self, direction=0):
        self.last_direction = direction
        def f():
            self.pattern.wakeup(direction)

        self.put(f)

    def listen(self):
        if self.last_direction:
            def f():
                self.pattern.wakeup(self.last_direction)
            self.put(f)
        else:
            self.put(self.pattern.listen)

    def think(self):
        self.put(self.pattern.think)

    def speak(self):
        self.put(self.pattern.speak)

    def error_indicator(self, error_num=0):
        def f():
            self.pattern.error_indicator(error_num)

        self.put(f)
        

    def action(self, color="white"):
        def f():
            self.pattern.action(color)

        self.put(f)  

    def off(self):
        self.put(self.pattern.off)

    def put(self, func):
        self.pattern.stop = True
        self.queue.put(func)

    def _run(self):
        while True:
            func = self.queue.get()
            self.pattern.stop = False
            func()

    def show(self, data):
        for i in range(self.PIXELS_N):
            #print(i)
            self.dev.set_pixel(i, int(data[4*i + 1]), int(data[4*i + 2]), int(data[4*i + 3]), 5)
            self.dev.show()
            time.sleep(0.001)
        #self.dev.show()
    
    def show_odd_pixel(self, red, green, blue):
        for i in range(self.PIXELS_N):
            if i%2 != 0:
                self.dev.set_pixel(i, red, green, blue, 5)
        
        self.dev.show()



def main():

    pixels = Pixels()
    sr_instance = sr.Recognizer() 

    pixels.wakeup()
    time.sleep(5)

    while True:

        with sr.Microphone() as source:
            print("Say Something!")
            pixels.speak()
            audio = sr_instance.listen(source)
            
        try:
            color_name = sr_instance.recognize_google(audio)
            
            #To check the name is available
            colors.to_rgb(color_name)

            pixels.action(color_name)
            time.sleep(10)
            
            #pixels.off()
            #time.sleep(1)

        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            pixels.off()
            pixels.error_indicator()
            time.sleep(3)
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))        
        except ValueError:
            print("Color name unavailable")
            pixels.off()
            pixels.error_indicator()
            time.sleep(3)
        except KeyboardInterrupt:
            break


    pixels.off()
    time.sleep(1)


if __name__ == '__main__':
    main()
