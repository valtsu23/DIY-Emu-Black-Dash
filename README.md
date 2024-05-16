This readme is still on progress. 

# DIY-Emu-Black-Dash
Raspberry pi based digital dash working with Ecumaster Emu Black. 
More info coming, still on beta. 

### Hardware features
Raspberry Pi 4 handles the communicatin with all the hardware. Can bus communication with MCP2515, ADC (MCP3002) reads light sensor values and Raspberry Pi adjusts screen brightness based on ambient light. 
Device needs switched 12V and continous 12v from battery to work correctly. Continous power is connected to a relay on PCB. Switched power wakes up the device and Raspberry pi starts booting and relay turns on. When Can Bus stream is lost Raspberry pi automatically starts shutdown process. After the relay turns off and cuts power from the device. The device doesn't consume any power after shutdown. 

...
