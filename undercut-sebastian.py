import time
from threading import Thread

import cv2
import mss
import numpy
import pytesseract
from pynput import keyboard
from pynput.keyboard import Controller

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


def main():
    print("Script started")
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()


def on_press(key):
    # print(key)
    if str(key) == "'ó'":
        thread = Thread(target=(tests if debug else begin))
        thread.start()
    if str(key) == "'ü'":
        print("stopped")
        quit()


my_item_number_coords = {"x": 795, "y": 524, "w": 66, "h": 21}
my_price_coords = {"x": 584, "y": 411, "w": 70, "h": 18}
enemy_price_coords = {"x": 560, "y": 486, "w": 64, "h": 19}
cb = Controller()
undercut_threshold = 0.35
wait_time = 0.2
debug = False


def tests():
    print("Tests started")
    number = get_number(my_item_number_coords, "my_item_number")
    # number = get_number(my_price_coords, "my_price")
    # number = get_number(enemy_price_coords, "enemy_price")
    print(number)
    # adjust_price(1234789)
    print("Tests ended")


def begin():
    print("Running..")
    # Select retainer
    down()
    # Enter retainer
    enter()
    time.sleep(1.4)
    # Skip dialog
    enter()
    time.sleep(0.5)
    # Select and enter sell items from inventory to market
    down()
    down()
    enter()
    time.sleep(0.6)
    my_item_number = get_number(my_item_number_coords, "my_item_number")
    print(str(my_item_number) + " items detected")
    for i in range(my_item_number):
        enter()
        enter()
        time.sleep(0.1)
        my_price = get_number(my_price_coords, "my_price")
        print("My price: " + str(my_price))
        up()
        enter()
        time.sleep(0.8)
        enemy_price = get_number(enemy_price_coords, "enemy_price")
        print("Enemy price: " + str(enemy_price))
        escape()
        down()
        # currently hovering over my price
        if 500 < enemy_price < my_price and (enemy_price / my_price) > undercut_threshold:
            adjust_price(enemy_price - 1)
        else:
            escape()
        down()
    escape()
    time.sleep(0.5)
    escape()
    enter()
    time.sleep(1.4)


def adjust_price(desired_price):
    print("Adjusting price to: " + str(desired_price))
    enter()
    cb.press(keyboard.Key.enter)
    cb.release(keyboard.Key.enter)
    time.sleep(wait_time)
    escape()
    cb.type(str(desired_price))
    time.sleep(wait_time)
    cb.press(keyboard.Key.enter)
    cb.release(keyboard.Key.enter)
    time.sleep(wait_time)
    down()
    down()
    enter()


def up():
    cb.press(keyboard.KeyCode(104))
    cb.release(keyboard.KeyCode(104))
    time.sleep(wait_time)


def down():
    cb.press(keyboard.KeyCode(98))
    cb.release(keyboard.KeyCode(98))
    time.sleep(wait_time)


def right():
    cb.press(keyboard.KeyCode(102))
    cb.release(keyboard.KeyCode(102))
    time.sleep(wait_time)


def left():
    cb.press(keyboard.KeyCode(100))
    cb.release(keyboard.KeyCode(100))
    time.sleep(wait_time)


def enter():
    cb.press(keyboard.KeyCode(96))
    cb.release(keyboard.KeyCode(96))
    time.sleep(wait_time)


def escape():
    cb.press(keyboard.Key.esc)
    cb.release(keyboard.Key.esc)
    time.sleep(wait_time)


def get_number(coords, item_format):
    mon = {'left': coords["x"], 'top': coords["y"], 'width': coords["w"], 'height': coords["h"]}
    with mss.mss() as sct:
        im = numpy.asarray(sct.grab(mon))
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)  # grayscale to setup for threshold and improve accuracy
        # im = cv2.adaptiveThreshold(im, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        if item_format == "my_item_number":
            th, im = cv2.threshold(im, 180, 255, cv2.THRESH_BINARY)  # threshold to improve accuracy
        else:
            th, im = cv2.threshold(im, 120, 255, cv2.THRESH_BINARY)
        im = ~im  # reversing image (so it'll be black text on white background)
        return detect_number(im, coords["w"], coords["h"], item_format)


def detect_number(im, width, height, item_format, inter_type=cv2.INTER_CUBIC):
    for i in range(2, 5):
        res = cv2.resize(im, dsize=(width * i, height * i), interpolation=inter_type)
        if debug:
            cv2.imshow('Image', res)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        text = pytesseract.image_to_string(res, lang='eng',
                                           config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789,/')
        if text != "":
            if item_format == "my_price":
                try:
                    number = int(text)
                    return number
                except:
                    print("Error detecting my_price, trying to upscale: " + str(i))
            elif item_format == "my_item_number":
                try:
                    number = int(text[:-3])
                    return number
                except:
                    print("Error detecting my_items, trying to upscale: " + str(i))
            elif item_format == "enemy_price":
                try:
                    number = int(text.replace(",", ""))
                    return number
                except:
                    print("Error detecting enemy_price, trying to upscale: " + str(i))
        else:
            print("No text detected")
            return -1
    if inter_type != cv2.INTER_AREA:
        print("Trying a different upscaling method")
        return detect_number(im, width, height, item_format, cv2.INTER_AREA)
    return -1


def text_detection_test():
    print("Text recognition started")
    x = 326
    y = 77
    width = 1025
    height = 583
    mon = {'left': x, 'top': y, 'width': width, 'height': height}

    with mss.mss() as sct:
        im = numpy.asarray(sct.grab(mon))
        res = cv2.resize(im, dsize=(width * 4, height * 4), interpolation=cv2.INTER_CUBIC)
        try:
            text = pytesseract.image_to_string(res)
            print(text)
        except:
            print("error")
        cv2.imshow('Image', res)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def number_detection_test():
    print("Number recognition started")
    x = 560
    y = 486
    width = 64
    height = 19
    mon = {'left': x, 'top': y, 'width': width, 'height': height}
    with mss.mss() as sct:
        im = numpy.asarray(sct.grab(mon))
        res = cv2.resize(im, dsize=(width * 2, height * 2), interpolation=cv2.INTER_CUBIC)

        try:
            text = pytesseract.image_to_string(res)
            print(text)
            number = int(text.replace(",", ""))
            print(number)
        except:
            print("error")
        cv2.imshow('Image', res)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def control_test():
    controlboard = Controller()
    controlboard.press(keyboard.KeyCode(98))
    controlboard.release(keyboard.KeyCode(98))


if __name__ == "__main__":
    main()
