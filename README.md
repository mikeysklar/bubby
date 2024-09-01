
Pocket Chording Left Hand Keyboard

A compact pocket keyboard for taking notes that can also be used as a USB keyboard. This a simple sturdy design every day carry design. Some frill, mostly function.

![Screenshot](pics/hands-on.jpeg)

Features:
===

* Slim Form Factor (mm)
    * thinner than a deck of cards in all dimensions
* 240x135 color LCD
    * view typed characters 
* Take notes
    * save to flash
    * view as USB drive
* Built-in Timer
    * chord speed practice
* ESP32-S3 based
    * future BLE wireless keyboard option
* CircuitPython 
    * based on [akmnos22 one handed chording keyboad](https://www.instructables.com/One-Handed-Chording-Keyboard/)
* Adafruit Feather Compatible
    * also works with Feather RP2040 (minus display code)
* USB-C 
    * optional computer/tablet/phone/pi HID interface
    * 350mAh battery w/charger


![Screenshot](pics/freecad.jpeg)

* Enclosure
    * Designed in FreeCAD 0.21.2
    * Printed on Bambu Lab P1P

![Screenshot](pics/kicad-pcb.jpeg)

* Dimensions:
    * 80 x 46 x 12 

* Tested with Circuitpython 9.x
    * PCB files are KiCAD
    * Enclosure is FreeCAD

![Screenshot](pics/open.jpeg)

Bill of Materials
===

| Item       | Source     | Part Number        |
|:----------:|:----------:|:------------------:|
| Controller | Adafruit   | [Feather ESP32-S3](https://www.adafruit.com/product/5483) |
| Bat 350mAh | Adafruit   | [LiPo 3.7v ADA# 2750](https://www.adafruit.com/product/2750) |
| Buttons    | Digi-Key   | [450-1657-ND](450-1657-ND) |
| Pwr Switch | AliExpress | MSKT-12G03 |
| Screws     | Adafruit   | [M2.5 Machine Screws / Stand-off](https://www.adafruit.com/product/3299) |

![Screenshot](pics/bottom.jpeg)

* Slim power switch on bottom.
* Keychain hole

![Screenshot](pics/chords.jpeg)

* G indicates center thumb (green)
    * B - blue (inner thumb)
    * Y - yellow (outer thumb)

* Chording ascii table. Digits, punctuation, symbols and mofiiers are also supported with the thumb modifiers. Firmware includes 4 custom modifiers.
    * save 124
    * timer 134
    * clear screen G-124
    * usb mode G-134

![Screenshot](pics/milled-pcb.jpeg)

* Milled single sided on a Bantam Othermill.
    * traces PCB engraving bit 0.005 (mm)
    * drill holes 0.9 (mm)

![Screenshot](pics/sch.jpeg)

![Screenshot](pics/front.jpeg)
