import numpy
import time
from matplotlib import colors
try:
    import queue as Queue
except ImportError:
    import Queue as Queue


class MagicEcoLedPattern(object):

    def __init__(self, show=None, show_odd_pixel=None):
        self.color_data = numpy.array([0]*4*12)

        self.basis = numpy.array([0] * 4 * 12)
        self.basis[0 * 4 + 1] = 2
        self.basis[3 * 4 + 1] = 1
        self.basis[3 * 4 + 2] = 1
        self.basis[6 * 4 + 2] = 2
        self.basis[9 * 4 + 3] = 2

        self.pixels = self.basis * 24

        if not show or not callable(show):
            def dummy(data):
                pass
            show = dummy

        if not show_odd_pixel or not callable(show_odd_pixel):
            def dummy_odd_pixel(data):
                pass
            show_odd_pixel = dummy_odd_pixel
        """
        if not show_even_pixel or not callable(show_even_pixel):
            def dummy_even_pixel(data):
                pass
            show_even_pixel = dummy_even_pixel
        """

        self.show = show
        self.show_odd_pixel = show_odd_pixel
    
        self.stop = False

    def wakeup(self, direction=0):
        position = int((direction + 15) / 30) % 12

        basis = numpy.roll(self.basis, position * 4)
        for i in range(1, 25):
            pixels = basis * i
            self.show(pixels)
            time.sleep(0.005)

        pixels =  numpy.roll(pixels, 4)
        self.show(pixels)
        time.sleep(0.1)

        for i in range(2):
            new_pixels = numpy.roll(pixels, 4)
            self.show(new_pixels * 0.5 + pixels)
            pixels = new_pixels
            time.sleep(0.1)

        self.show(pixels)
        self.pixels = pixels

    def listen(self):
        pixels = self.pixels
        for i in range(1, 25):
            self.show(pixels * i / 24)
            time.sleep(0.01)

    def think(self):
        pixels = self.pixels

        while not self.stop:
            pixels = numpy.roll(pixels, 4)
            self.show(pixels)
            time.sleep(0.2)

        t = 0.1
        for i in range(0, 5):
            pixels = numpy.roll(pixels, 4)
            self.show(pixels * (4 - i) / 4)
            time.sleep(t)
            t /= 2

        self.pixels = pixels

    def speak(self):
        pixels = self.pixels
        step = 1
        brightness = 5
        while not self.stop:
            self.show(pixels * brightness / 24)
            time.sleep(0.02)

            if brightness <= 5:
                step = 1
                time.sleep(0.4)
            elif brightness >= 24:
                step = -1
                time.sleep(0.4)

            brightness += step

    def set_color(self, color_name):
        color_hex = colors.to_rgb(color_name)
        red = int(color_hex[0]*255)
        green = int(color_hex[1]*255)
        blue = int(color_hex[2]*255)
        for i in range(len(self.color_data)):
            if i%4 == 0:
                self.color_data[i] = 0
            elif i%4 == 1:
                self.color_data[i]=red
            elif i%4 == 2:
                self.color_data[i]=green
            else:
                self.color_data[i]=blue

        print("color value ",red,green,blue)


    def dont_understand(self, error_num=0):
        self.show_odd_pixel(0xFF,0,0)

    def action(self, color="white"):
        self.set_color(color)
        self.show(self.color_data)

    def off(self):
        self.show([0] * 4 * 12)