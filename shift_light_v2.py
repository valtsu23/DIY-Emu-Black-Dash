import board
import neopixel
import time

# Neopixel setup (pin, number of leds)
pixels = neopixel.NeoPixel(board.D21, 8)

# Turn off all the leds
def leds_off():
    pixels.fill((0, 0, 0))

# Blink frequency and timer
BLINK = .1
t1 = time.monotonic()

# Needed variables
shift_changed = 10

def action(rpm, STEP, END, br):
    global shift_changed
    global t1
    shift = (END - rpm) // STEP + 1
    # Blinker
    if rpm > END + STEP:
        if t1 + BLINK < time.monotonic():
            pixels.fill((0, br, br))
        if t1 + BLINK * 2 < time.monotonic():
            pixels.fill((0, 0, 0))
            t1 = time.monotonic()
    # If shift light step is exceeded
    elif shift_changed != shift:
        # LED steps control
        # print("Shift:", shift)
        # print("Shift_changed:", shift_changed)
        if shift <= 3:
            pixels[0] = (0, br, 0)
            pixels[7] = (0, br, 0)
        else:
            pixels[0] = (0, 0, 0)
            pixels[7] = (0, 0, 0)

        if shift <= 2:
            pixels[1] = (0, br, 0)
            pixels[6] = (0, br, 0)
        else:
            pixels[1] = (0, 0, 0)
            pixels[6] = (0, 0, 0)

        if shift <= 1:
            pixels[2] = (br, br, 0)
            pixels[5] = (br, br, 0)
        else:
            pixels[2] = (0, 0, 0)
            pixels[5] = (0, 0, 0)

        if shift <= 0:
            pixels[3] = (br, 0, 0)
            pixels[4] = (br, 0, 0)
        else:
            pixels[3] = (0, 0, 0)
            pixels[4] = (0, 0, 0)

    # Save the new state
    shift_changed = shift
