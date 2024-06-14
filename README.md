![Working Dash](https://filedn.com/lKOo3aQn9ubHtKC7DXLEkHh/DIY-Emu-Black-Dash/IMG_20240612_141538698.jpg)

# DIY-Emu-Black-Dash
Raspberry pi based digital dash working with Ecumaster Emu Black. 
Based on https://github.com/valtsu23/Raspberry_Pi_gauge_cluster .
Biggest difference to previously mentioned is PCB. Now there isn't an additional microcontroller. Also parts of the program had to be rewritten to support new hardware. 

### Additional data
  - [Video](https://youtu.be/x8BvJFvcHbc) 
  - [Raspberry Pi setup guide](https://filedn.com/lKOo3aQn9ubHtKC7DXLEkHh/DIY-Emu-Black-Dash/Raspberry%20Pi%20setup%20guide.pdf)
  - [Case and pcb files](https://filedn.com/lKOo3aQn9ubHtKC7DXLEkHh/DIY-Emu-Black-Dash/Case%20and%20Pcb%20files.zip) (Used software: FreeCAD and Fusion 360)
  - [Pcb schematic in pdf](https://filedn.com/lKOo3aQn9ubHtKC7DXLEkHh/DIY-Emu-Black-Dash/PCB_schematic.pdf)

### To do
  - More testing
  - Raspberry Pi 5 version is also coming at some point

### Technical specs:
- Raspberry Pi 4 Model B 4GB
- SanDisk Extreme Pro UHS-I U3 64GB microSD
- 5" sunlight readable display with touchscreen from Makerplane:
  - https://store.makerplane.org/5-sunlight-readable-touchscreen-hdmi-display-for-raspberry-pi/
- DIY PCB inside the enclosure

### Hardware features
Raspberry Pi 4 handles the communicatin with all the hardware via SPI and I2C. Can bus communication with MCP2515, ADC (MCP3002) reads light sensor values and Raspberry Pi adjusts screen brightness based on ambient light. DS3231 RTC to keep the clock in time. Neopixels for shiftlight. 12v to 5v DC-DC converter on board. Device needs switched 12V and continous 12v from battery to work correctly. Continous power is connected to a relay on PCB. Switched power wakes up the device and Raspberry pi starts booting and relay turns on. When Can Bus stream is lost Raspberry pi automatically starts shutdown process. After shutdown the relay turns off and cuts power from the device. The device doesn't consume any power after shutdown. Small button as a failsafe if Raspberry Pi crashes (pressing thins buttons turns relay off). 

### Software specs
- Raspberry Pi OS Lite 64bit (Bookworm)
  - Python code runs from command line without a windows manager
  - Gauge cluster software is based on Pygame graphics library
### Performance
  - Boot time with overclock is about 18s
  - I have made a lot of work to make the program light as possible
  - Only part of the screen is updated when needed, not the whole screen (this helps for cpu load)
  - I'm not using any kind of extra cooling
  - I haven't experienced any heat or performance issues
### Graphic software functions
- There is 6 sensors data (3 left and 3 right) that you can choose to display with touscreen
- bar on the bottom of the screen in normal situation is blue and shows Raspberry pi CPU temperature and CPU clock
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
  - MCP3002-I/P
  - 3A diode 
  - 1A diode 2pcs
  - P6KE18A transient diode (for overvoltage protection)
  - 15pF Ceramic capacitor 2pcs
  - 16Mhz crystal
  - BPW42 3mm phototransistor or similar
  - 2N3904 NPN transistor or similar
  - B3F-31XX Omron switch or SKH KKK 2 from partco.fi
  - 120 0,6w resistor
  - 10K 0,6w resistor
  - 2K2 0,6w resistor
  - 1M 0,6w resistor 
  - 2x13 male pin header with long pins (20mm total length)
  - 2x13 female smd pin header (soldered to display pcb)
  - 1x40 male pin header
  - 0,22mm2 - 0,5mm2 wires (0,5mm2 recommended for power and ground)
  - MCP2515-I/P
  - MCP2562-E/P
  - IC SOCKET 18-PINS (optional)
  - IC SOCKET 8-PINS 2pcs (optional)
  - FTR-F3AA005V
#### From www.Berrybase.de
  - NeoPixel Stick mit 8 WS2812 5050 RGB LEDs (Copy of Adafruit's product. Dimensions won't match)
#### From www.botland.store/
  - Adafruit DS3231 Precision RTC - STEMMA QT
  - Pololu Step-Down Voltage Converter D24V22F5 - 5V 2,5A 2858
#### From www.ebay.com
  - 5pin JST-SM connector pair


![Alt PCB](https://filedn.com/lKOo3aQn9ubHtKC7DXLEkHh/DIY-Emu-Black-Dash/IMG_20240528_233423409.jpg)

![Alt Inside](https://filedn.com/lKOo3aQn9ubHtKC7DXLEkHh/DIY-Emu-Black-Dash/IMG_20240528_234437181.jpg)

![Alt Case1](https://filedn.com/lKOo3aQn9ubHtKC7DXLEkHh/DIY-Emu-Black-Dash/IMG_20240528_234606426.jpg)

![Alt Case2](https://filedn.com/lKOo3aQn9ubHtKC7DXLEkHh/DIY-Emu-Black-Dash/IMG_20240528_234642311.jpg)

![Alt Case3](https://filedn.com/lKOo3aQn9ubHtKC7DXLEkHh/DIY-Emu-Black-Dash/IMG_20240528_234623667.jpg)
