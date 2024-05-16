This readme is still on progress. 

# DIY-Emu-Black-Dash
Raspberry pi based digital dash working with Ecumaster Emu Black. 
More info coming, still on beta. 

### Hardware features
Raspberry Pi 4 handles the communicatin with all the hardware. Can bus communication with MCP2515, ADC (MCP3002) reads light sensor values and Raspberry Pi adjusts screen brightness based on ambient light. DS3231 RTC tp keep the clock in time. Neopixels for shiftlight. 12v to 5v DC-DC converter on board. Device needs switched 12V and continous 12v from battery to work correctly. Continous power is connected to a relay on PCB. Switched power wakes up the device and Raspberry pi starts booting and relay turns on. When Can Bus stream is lost Raspberry pi automatically starts shutdown process. After shutdown the relay turns off and cuts power from the device. The device doesn't consume any power after shutdown. Small button as a failsafe if Raspberry Pi crashes (pressing thins buttons turns relay off). 

### Software specs
- Raspberry Pi OS Lite 64bit (Bookworm)
  - Python code runs from command line without a windows manager
  - Gauge cluster software is based on Pygame graphics library
### Graphic software functions
- There is 6 sensors data (3 left and 3 right) that you can choose to display with touscreen
- bar on the bottom of the screen in normal situation is blue and shows Raspberry pi CPU temperature
- If there is some error detected by ECU or battery voltage is low. Error flags are shown on the bottom of the screen and the bar is red. 

### Can bus stream
- Most of the data needed is read from Ecumaster Emu Black can stream
- There is also DIY can bus device sending message id 0x400, which contains
  - Turn signals
  - High beam on
  - Fuel level
  - Ambient temperature

### Case
- Designed with FreeCAD
- Filament is PETG
- M3x6 machine screws 2 pcs
- M4 thread insert 1 pcs
- M4x8 machine screw 1pcs
- M4x20 machine screw 2pcs
- M4 nut 2pcs

### Part list for PCB:
#### From www.partco.fi
  - 3A diode 
  - 1A diode 2pcs
  - FTR-F3AA005V (small 5V relay)
  - BPW42 3mm phototransistor or similar
  - 2N3904 NPN transistor or similar
  - B3F-31XX Omron switch or SKH KKK 2 from partco.fi
  - MCP2515
  - 10K 0,6w resistor
  - 2K2 0,6w resistor
  - 1M 0,6w resistor 
  - 2x13 male pin header with long pins (20mm total length)
  - 2x13 female smd pin header (soldered to display pcb)
  - 1x40 male pin header
  - 0,22mm2 - 0,5mm2 wires (0,5mm2 recommended for power and ground)
#### From Berrybase.de
  - NeoPixel Stick mit 8 WS2812 5050 RGB LEDs (Copy of Adafruit's product. Dimensions won't match)
#### From www.adafruit.com
  - Adafruit DS3231 Precision RTC - STEMMA QT
#### From www.ebay.com
  - 5pin JST-SM connector pair
