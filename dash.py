import pygame
import time
import struct

# PC test mode
TEST_MODE = False

# Screen size
size = width, height = (800, 480)
pygame.display.init()
pygame.font.init()

if TEST_MODE is False:
    import os
    import can
    import mcp3002
    import shift_light_v2
    from rpi_hardware_pwm import HardwarePWM
    screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    PATH = "/home/your_user_name/Dash/"
    # Can bus
    os.system('ip link set can0 type can bitrate 500000')
    os.system('ifconfig can0 up')
    can_bus_filter = [{"can_id": 0x607, "can_mask": 0x5F8 , "extended": False}]
    can_bus = can.Bus(channel="can0", interface="socketcan", can_filters=can_bus_filter)
    # Pwm
    backlight = HardwarePWM(pwm_channel=0, hz=500, chip=0)
    backlight.start(70)
else:
    screen = pygame.display.set_mode(size)
    PATH = "P:/Raspberry_pi/EMU_display_mcp/"

# Read needed files
units_memory = open(PATH + "units_memory.txt", "r")
units = units_memory.read().splitlines()
units_memory.close()
odometer_memory = open(PATH + "odometer_memory.txt", "r")
odometer = float(odometer_memory.readline())
odometer_memory.close()

# Variables
start_up = True
timeout_counter = 0
rpm = 0
speed = 0
gear = 0
out_temp = 0
fuel_level = None
fuel_used = None
raw_fuel_level = 0
refuel = False
batt_v = 0
left_blinker = False
right_blinker = False
high_beam = False
errors = 0
speed_sum = 0
speed_sum_counter = 0
old_rpm = None
old_gear = None
old_speed = None
old_out_temp = None
old_odometer = odometer
old_clock = None
old_error_list = None
old_refuel = None
old_right_blinker = None
old_left_blinker = None
old_high_beam = None
values = {x : 0 for x in units}
old_values = {x : None for x in units}
clear = True
loop = True
touch = False
start = True
filter_counter = 0
filter_sum = 0
countdown = 10
unit_change = None
units_ok = True
draw_menu = False
old_cpu_temp = None
shift_changed = 10
shift_light_off = False
cpu_timer = time.monotonic()
blink_timer = time.monotonic()
dimmer_timer = time.monotonic()
distance_timer = time.monotonic()

# CONSTANTS
ECU_CAN_ID = 0x600
FUEL_MAX = 197
FUEL_MIN = 37
FUEL_DIVIDER = (FUEL_MAX - FUEL_MIN) / 100
CENTER_X, CENTER_Y = (width / 2, height / 2)
RIGHT_SIDE = width - 180
RED = (155, 0, 0)
WHITE = (255, 255, 255)
DARK_BLUE = (0, 64, 128)
LIGHT_BLUE = (0, 128, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
# Shift light
END = 8600
STEP = 300

# Close io devices
def close_io():
    mcp3002.close()
    can_bus.shutdown()
    os.system('ifconfig can0 down')
    backlight.stop()

# Touchscreen coordinate return
def touch_xy(x, y):
    return (int(x * width), int(y * height))

# Odometer calculations and file save
def odometer_save(speed_sum, speed_sum_counter, distance_timer, odometer, PATH):
    if speed_sum == 0:
        return odometer
    average_speed = (speed_sum / speed_sum_counter) * 0.27777778
    timer = time.monotonic() - distance_timer
    distance = (average_speed * timer) / 1000
    odometer = odometer + distance
    # Saving to memory
    odometer_memory = open(PATH + "odometer_memory.txt", "w")
    odometer_memory.write(str(odometer))
    odometer_memory.close()
    return odometer

def menu(pos):
    if pygame.Rect.collidepoint(rpm_button, pos):
        return "rpm"
    elif pygame.Rect.collidepoint(tps_button, pos):
        return "tps"
    elif pygame.Rect.collidepoint(iat_button, pos):
        return "iat"
    elif pygame.Rect.collidepoint(map_button, pos):
        return "map"
    elif pygame.Rect.collidepoint(inj_pw_button, pos):
        return "inj_pw"
    elif pygame.Rect.collidepoint(oil_t_button, pos):
        return "oil_t"
    elif pygame.Rect.collidepoint(oil_p_button, pos):
        return "oil_p"
    elif pygame.Rect.collidepoint(fuel_p_button, pos):
        return "fuel_p"
    elif pygame.Rect.collidepoint(clt_t_button, pos):
        return "clt_t"
    elif pygame.Rect.collidepoint(ign_ang_button, pos):
        return "ign_ang"
    elif pygame.Rect.collidepoint(dwell_button, pos):
        return "dwell"
    elif pygame.Rect.collidepoint(lambda_button, pos):
        return "lambda"
    elif pygame.Rect.collidepoint(lambda_corr_button, pos):
        return "lambda_corr"
    elif pygame.Rect.collidepoint(egt_1_button, pos):
        return "egt_1"
    elif pygame.Rect.collidepoint(egt_2_button, pos):
        return "egt_2"
    elif pygame.Rect.collidepoint(ethanol_cont_button, pos):
        return "ethanol_cont"
    elif pygame.Rect.collidepoint(batt_v_button, pos):
        return "batt_v"
    elif pygame.Rect.collidepoint(dbw_pos_button, pos):
        return "dbw_pos"
    elif pygame.Rect.collidepoint(boost_t_button, pos):
        return "boost_t"
    elif pygame.Rect.collidepoint(dsg_mode_button, pos):
        return "dsg_mode"
    elif pygame.Rect.collidepoint(lambda_t_button, pos):
        return "lambda_t"
    elif pygame.Rect.collidepoint(fuel_used_button, pos):
        return "fuel_used"
    elif pygame.Rect.collidepoint(fuel_level_button, pos):
        return "fuel_level"
    elif pygame.Rect.collidepoint(fuel_consumption_button, pos):
        return "fuel_consum"

# Read light sensor value
def is_dark():
    a_val = mcp3002.read_adc(0)
    # print(a_val)
    if a_val < 300:
        return True
    else:
        return False

# Dimmer
def dimmer(value):
    global led_br
    # Dark
    if value is True:
        backlight.change_duty_cycle(70)
        led_br = 10
    # Bright
    else:
        backlight.change_duty_cycle(0)
        led_br = 80

if TEST_MODE is False:
    old_dark = is_dark()
    dimmer(old_dark)

# Return CPU temperature and CPU clock as a character string
def getCPUtemperature():
    temp = os.popen('vcgencmd measure_temp').readline()
    temp = temp.replace("temp=", "")
    return temp.replace("'C\n", "°C")

def getCPUclock():
    clock = os.popen('vcgencmd measure_clock arm').readline()
    clock = clock.replace("frequency(48)=", "")
    clock = int(clock)/1000000
    return str(int(clock))

def error_flags(number):
    # Convert to bit list
    bit_list = [True if x == "1" else False for x in "{:016b}".format(number)]
    # Get the errors that are on
    errors_on = []
    for x in range(len(bit_list)):
        if bit_list[x] is True:
            errors_on.append(ERRORFLAGS[x])
    return errors_on

# Reading 3 bit bitfield from Can extension board (message 0x610)
def bitfield_3_return(number):
    # Convert to bit list
    bit_list = [True if x == "1" else False for x in "{:03b}".format(number)]
    return bit_list

# Emu Black error flags
ERRORFLAGS = ("", "OILP", "EWG", "DSG", "DIFFCTRL", "FPR", "DBW", "FF_SENSOR",
              "KNOCKING", "EGT_ALARM", "EGT2", "EGT1", "WBO", "MAP", "IAT", "CLT")

title_text_units = {"rpm": "RPM", "tps": "TPS                 %",
                    "iat": "IAT                 °C", "map": "MAP              kPa",
                    "inj_pw": "Inj pw.           ms", "oil_t": "Oil temp.       °C",
                    "oil_p": "Oil press.      bar", "fuel_p": "Fuel press.    bar",
                    "clt_t": "Clt temp.       °C", "ign_ang": "Ign angle  °btdc",
                    "dwell": "Dwell time    ms", "lambda": "Lambda",
                    "lambda_corr": "Lambda corr.  %", "egt_1": "EGT 1             °C",
                    "egt_2": "EGT 2             °C", "batt_v": "Battery  voltage",
                    "ethanol_cont": "Ethanol           %", "dbw_pos": "Dbw position  %",
                    "boost_t": "Boost target  kPa", "dsg_mode": "DSG mode",
                    "lambda_t": "Lambda target", "fuel_used": "Fuel used         L",
                    "fuel_level": "Fuel level        %", "fuel_consum": "Fuel c.  L/100km"}

dsg_mode_return = {0: "0", 2: "P", 3: "R", 4: "N", 5: "D", 6: "S", 7: "M", 15: "Fault"}

font_20 = pygame.font.SysFont("dejavusans", 20)
font_30 = pygame.font.SysFont("dejavusans", 30)
font_60 = pygame.font.SysFont("dejavusans", 60)
font_80 = pygame.font.SysFont("dejavusans", 80)

# Text box sizes
digits_30 = [font_30.size("0"), font_30.size("00"), font_30.size("000")]
kmh_30 = font_30.size("km/h")
one_digit_60 = font_60.size("0")
three_digit_60 = font_60.size("000")
one_letter_60 = font_60.size("N")
digits_80 = [font_80.size("0"), font_80.size("00"), font_80.size("000")]

# Renders
CELSIUS_20 = font_20.render("°C", True, WHITE, BLACK)
KMH_TEXT = font_30.render("km/h", True, WHITE, BLACK)
NO_CAN_BUS_R = font_20.render("No Can Bus communication", True, WHITE, BLACK)
# RPM bar numbers
rpm_list = [font_60.render(str(x), True, WHITE) for x in range(1, 10)]

image0 = pygame.image.load(PATH + "High_beam_blue.png")
image1 = pygame.image.load(PATH + "High_beam_black.png")
image2 = pygame.image.load(PATH + "Fuel_pump_yellow.png")
image3 = pygame.image.load(PATH + "Fuel_pump_black.png")

HIGH_BEAM_BLUE = pygame.Surface.convert(image0)
HIGH_BEAM_BLACK = pygame.Surface.convert(image1)
FUEL_PUMP_YELLOW = pygame.Surface.convert(image2)
FUEL_PUMP_BLACK = pygame.Surface.convert(image3)

unit_buttons = [pygame.Rect(0, 95, 180, 100), pygame.Rect(0, 210, 180, 100),
                pygame.Rect(0, 325, 180, 100), pygame.Rect(RIGHT_SIDE, 95, 180, 100),
                pygame.Rect(RIGHT_SIDE, 210, 180, 100), pygame.Rect(RIGHT_SIDE, 325, 180, 100)]

# Creating title texts
units_r = []
for x in range(6):
    units_r.append(font_20.render(title_text_units[units[x]], True, WHITE, BLACK))

while loop:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            loop = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            touch = True
            pos = event.pos
        elif event.type == pygame.FINGERUP:
            touch = True
            pos = touch_xy(event.x, event.y)

    if TEST_MODE is False:
        # Read can bus message
        message = can_bus.recv(timeout=1)
        # Shutdown if there is no Can Bus communication
        if message is None:
            clear = True
            countdown -= 1
            pygame.draw.rect(screen, BLACK, [CENTER_X - 150, 180, 300, 150], border_radius=10)
            screen.blit(NO_CAN_BUS_R, (CENTER_X - 140, CENTER_Y - 10))
            shutdown = font_20.render("Shutting down in: " + str(countdown) + " s", True, WHITE, BLACK)
            screen.blit(shutdown, (CENTER_X - 140, CENTER_Y + 15))
            pygame.display.flip()
            if countdown == 0:
                # Save odometer
                odometer = odometer_save(speed_sum, speed_sum_counter, distance_timer, odometer, PATH)
                close_io()
                print("Shutdown")
                os.system("shutdown -h now")
            if loop is True:
                continue
        else:
            data = message.data
            message_id = message.arbitration_id
    if TEST_MODE is True or message is None:
        data = None
        message_id = None
    # Reset countdown
    countdown = 10

    # List of what to update on the screen
    display_update = []
    # Clearing screen
    if clear:
        screen.fill((60, 60, 60))
        values = {x : 0 for x in units}
        old_values = {x : None for x in units}
        pygame.display.flip()

    if message_id == 0x400:
        message = struct.unpack("<BBb", data)
        bit_list_3 = bitfield_3_return(message[0])
        # High beam input is inverted
        high_beam = not bit_list_3[0]
        right_blinker = bit_list_3[1]
        left_blinker = bit_list_3[2]
        raw_fuel_level = message[1]
        out_temp = message[2]
        # Fuel level averaging
        if raw_fuel_level > FUEL_MAX:
            raw_fuel_level = FUEL_MAX
        elif raw_fuel_level < FUEL_MIN:
            raw_fuel_level = FUEL_MIN
        if filter_counter < 199:
            filter_sum += raw_fuel_level
            filter_counter += 1
            filter_ready = False
        else:
            fuel_level = int(filter_sum / filter_counter)
            filter_sum = 0
            filter_counter = 0
            filter_ready = True
        # Scaling and reading stabilation
        if filter_ready is True or start_up is True:
            # If filtering not ready
            if start_up is True:
                fuel_level = raw_fuel_level
            fuel_level = int((fuel_level - FUEL_MIN) / FUEL_DIVIDER - 100)
            if fuel_level != 0:
                fuel_level = fuel_level * -1
            if start_up is False and fuel_level > old_fuel_level:
                fuel_level = old_fuel_level + 1
            elif start_up is False and fuel_level < old_fuel_level:
                fuel_level = old_fuel_level - 1
            old_fuel_level = fuel_level
            start_up = False
        if "fuel_level" in units:
            values["fuel_level"] = fuel_level

    if message_id == ECU_CAN_ID:
        # Unpack message
        message = struct.unpack("<HBbHH", data)
        rpm = message[0]
        if "rpm" in units:
            values["rpm"] = rpm
        if "tps" in units:
            values["tps"] = int(message[1] * 0.5)
        if "iat" in units:
            values["iat"] = message[2]
        if "map" in units:
            values["map"] = message[3]
        if "inj_pw" in units:
            values["inj_pw"] = round(message[4] * 0.016129, 1)

    elif message_id == ECU_CAN_ID + 2:
        message = struct.unpack("<HBBBBh", data)
        speed = message[0]
        # Odometer
        speed_sum += speed
        speed_sum_counter += 1
        if speed_sum_counter >= 100:
            # Calculating travelled distance and save it
            odometer = odometer_save(speed_sum, speed_sum_counter, distance_timer, odometer, PATH)
            distance_timer = time.monotonic()
            speed_sum = 0
            speed_sum_counter = 0
        if "oil_t" in units:
            values["oil_t"] = message[2]
        if "oil_p" in units:
            values["oil_p"] = round(message[3] * 0.0625, 1)
        if "fuel_p" in units:
            values["fuel_p"] = round(message[4] * 0.0625, 1)
        if "clt_t" in units:
            values["clt_t"] = message[5]

    elif message_id == ECU_CAN_ID + 3:
        message = struct.unpack("<bBBBHH", data)
        if "ign_ang" in units:
            values["ign_ang"] = message[0] * 0.5
        if "dwell" in units:
            values["dwell"] = round(message[1] * 0.05, 1)
        if "lambda" in units:
            values["lambda"] = round(message[2] * 0.0078125, 2)
        if "lambda_corr" in units:
            values["lambda_corr"] = int(message[3] * 0.5)
        if "egt_1" in units:
            values["egt_1"] = message[4]
        if "egt_2" in units:
            values["egt_2"] = message[5]

    elif message_id == ECU_CAN_ID + 4:
        message = struct.unpack("<BbHHBB", data)
        gear = message[0]
        batt_v = round(message[2] * 0.027, 1)
        if "batt_v" in units:
            values["batt_v"] = batt_v
        # Error flags
        errors = message[3]
        if "ethanol_cont" in units:
            values["ethanol_cont"] = message[5]

    elif message_id == ECU_CAN_ID + 5:
        message = struct.unpack("<BBhHBB", data)
        if "dbw_pos" in units:
            values[units.index("dbw_pos")] = int(message[0] * 0.5)

    elif message_id == ECU_CAN_ID + 7:
        message = struct.unpack("<HBBBBH", data)
        if "boost_t" in units:
            values["boost_t"] = message[0]
        if "dsg_mode" in units:
            values["dsg_mode"] = dsg_mode_return[message[2]]
        if "lambda_t" in units:
            values"lambda_t"] = round(message[3] * 0.01, 2)
        fuel_used = message[5] * 0.01
        if "fuel_used" in units:
            values["fuel_used"] = round(fuel_used, 1)
    if int(odometer) != int(old_odometer) and fuel_used is not None:
        fuel_consum = round(fuel_used / ((odometer - old_odometer) / 100), 1)
        if "fuel_consum" in units:
            values["fuel_consum"] = fuel_consum

    # Shift light
    if TEST_MODE is False:
        # Shift light
        if rpm > END - STEP * 5:
            shift_light_v2.action(rpm, STEP, END, led_br)
            shift_light_off = False
            # Make sure all leds are off
        else:
            if shift_light_off is False:
                shift_light_v2.leds_off()
                shift_light_off = True

        # Dimmer
        dark = is_dark()
        # If ambient light hasn't changed: reset timer
        if dark is old_dark:
            t1 = time.monotonic()
        # If timer hasn't been reseted in 4 seconds: change brightness
        if time.monotonic() > t1 + 4:
            dimmer(dark)
            old_dark = dark

    # To make sure a unit button is pressed in menu
    if units_ok is True:
        # Update values, when needed
        # Top left value update
        if values[units[0]] != old_values[units[0]] or clear is True:
            pygame.draw.rect(screen, BLACK, [0, 95, 180, 100], border_radius=10)
            value_0_r = font_60.render(str(values[units[0]]), True, WHITE, BLACK)
            screen.blit(value_0_r, (10, 125))
            screen.blit(units_r[0], (10, 100))
            display_update.append((0, 95, 180, 100))
        # Center left value update
        if values[units[1]] != old_values[units[1]] or clear is True:
            pygame.draw.rect(screen, BLACK, [0, 210, 180, 100], border_radius=10)
            value_1_r = font_60.render(str(values[units[1]]), True, WHITE, BLACK)
            screen.blit(value_1_r, (10, 240))
            screen.blit(units_r[1], (10, 215))
            display_update.append((0, 210, 180, 100))
        # Bottom left value update
        if values[units[2]] != old_values[units[2]] or clear is True:
            pygame.draw.rect(screen, BLACK, [0, 325, 180, 100], border_radius=10)
            value_2_r = font_60.render(str(values[units[2]]), True, WHITE, BLACK)
            screen.blit(value_2_r, (10, 355))
            screen.blit(units_r[2], (10, 330))
            display_update.append((0, 325, 180, 100))
        # Top right value update
        if values[units[3]] != old_values[units[3]] or clear is True:
            pygame.draw.rect(screen, BLACK, [RIGHT_SIDE, 95, 180, 100], border_radius=10)
            value_3_r = font_60.render(str(values[units[3]]), True, WHITE, BLACK)
            screen.blit(value_3_r, (RIGHT_SIDE + 10, 125))
            screen.blit(units_r[3], (RIGHT_SIDE + 10, 100))
            display_update.append((RIGHT_SIDE, 95, 180, 100))
        # Center right value update
        if values[units[4]] != old_values[units[4]] or clear is True:
            pygame.draw.rect(screen, BLACK, [RIGHT_SIDE, 210, 180, 100], border_radius=10)
            value_4_r = font_60.render(str(values[units[4]]), True, WHITE, BLACK)
            screen.blit(value_4_r, (RIGHT_SIDE + 10, 240))
            screen.blit(units_r[4], (RIGHT_SIDE + 10, 215))
            display_update.append((RIGHT_SIDE, 210, 180, 100))
        # Bottom right value update
        if values[units[5]] != old_values[units[5]] or clear is True:
            pygame.draw.rect(screen, BLACK, [RIGHT_SIDE, 325, 180, 100], border_radius=10)
            value_5_r = font_60.render(str(values[units[5]]), True, WHITE, BLACK)
            screen.blit(value_5_r, (RIGHT_SIDE + 10, 355))
            screen.blit(units_r[5], (RIGHT_SIDE + 10, 330))
            display_update.append((RIGHT_SIDE, 325, 180, 100))
        # Save old values
        for x in range(6):
            if values[units[x]] != old_values[units[x]] or clear is True:
                old_values[units[x]] = values[units[x]]

    # Gear update
    if gear != old_gear or clear is True:
        pygame.draw.rect(screen, BLACK, [CENTER_X - 40, 90, 80, 80], border_radius=10)
        old_gear = gear
        if gear == 0:
            gear = "N"
        gear_r = font_60.render(str(gear), True, WHITE, BLACK)
        if gear == "N":
            screen.blit(gear_r, (CENTER_X - one_letter_60[0] / 2, 95))
        else:
            screen.blit(gear_r, (CENTER_X - one_digit_60[0] / 2, 95))
        display_update.append((CENTER_X - 40, 90, 80, 80))
    # Speed update
    if speed != old_speed or clear is True:
        old_speed = speed
        pygame.draw.rect(screen, BLACK, [CENTER_X - 110, 180, 220, 150], border_radius=10)
        speed_r = font_80.render(str(speed), True, WHITE, BLACK)
        screen.blit(speed_r, (CENTER_X - digits_80[len(str(speed)) - 1][0] / 2, CENTER_Y - digits_80[0][1] / 2))
        screen.blit(KMH_TEXT, (CENTER_X - kmh_30[0] / 2, 285))
        display_update.append((CENTER_X - 110, 180, 220, 150))

    clock = time.strftime("%H:%M")
    if clock != old_clock or out_temp != old_out_temp or int(odometer) != int(old_odometer) or clear is True:
        pygame.draw.rect(screen, BLACK, [CENTER_X - 110, 340, 220, 80], border_radius=10)
        screen.blit(CELSIUS_20, (CENTER_X + 75, 350))
        # Clock update
        old_clock = clock
        clock_r = font_30.render(clock, True, WHITE, BLACK)
        screen.blit(clock_r, (CENTER_X - 100, 343))
        # Out temp update
        old_out_temp = out_temp
        out_temp_r = font_30.render(str(out_temp), True, WHITE, BLACK)
        out_temp_location = CENTER_X + 72 - digits_30[len(str(out_temp)) - 1][0], 343
        if out_temp < 0:
            out_temp_location = out_temp_location[0] + 7,  343
        screen.blit(out_temp_r, out_temp_location)
        # Odometer update
        old_odometer = odometer
        odometer_r = font_30.render(str(int(odometer)) + " km", True, WHITE, BLACK)
        screen.blit(odometer_r, (CENTER_X - 100, 383))
        display_update.append((CENTER_X - 110, 340, 220, 80))

    # RPM Bar
    if rpm != old_rpm or clear is True:
        rpm_bar = int(rpm * 0.08)
        pygame.draw.rect(screen, BLACK, (0, 0, 800, 80))
        pygame.draw.rect(screen, LIGHT_BLUE, (0, 0, rpm_bar, 80))
        for x in range(len(rpm_list)):
            screen.blit(rpm_list[x], (width / 10 * (x + 1) - one_digit_60[0] / 2, 40 - one_digit_60[1] / 2))
        old_rpm = rpm
        display_update.append((0, 0, 800, 80))

    if old_left_blinker != left_blinker or clear is True:
        if left_blinker is True:
            blinker_colour = GREEN
        else:
            blinker_colour = BLACK
        bl = [210, 150]
        pygame.draw.polygon(screen, blinker_colour, [[bl[0], bl[1]], [bl[0] + 16, bl[1] - 16], [bl[0] + 16, bl[1] + 16]])
        pygame.draw.rect(screen, blinker_colour, (bl[0] + 16, bl[1] - 8, 16, 16))
        old_left_blinker = left_blinker
        display_update.append((bl[0] - 1, bl[1] - 17, 34, 34))

    if old_right_blinker != right_blinker or clear is True:
        if right_blinker is True:
            blinker_colour = GREEN
        else:
            blinker_colour = BLACK
        br = [590, 150]
        pygame.draw.polygon(screen, blinker_colour, [[br[0], br[1]], [br[0] - 16, br[1] - 16], [br[0] - 16, br[1] + 16]])
        pygame.draw.rect(screen, blinker_colour, (br[0] - 32, br[1] - 8, 16, 16))
        old_right_blinker = right_blinker
        display_update.append((br[0] - 33, bl[1] - 17, 34, 34))

    if old_high_beam != high_beam or clear is True:
        if high_beam is True:
            screen.blit(HIGH_BEAM_BLUE, (205, 350))
        else:
            screen.blit(HIGH_BEAM_BLACK, (205, 350))
        old_high_beam = high_beam
        display_update.append((205, 350, 50, 50))

    # Fuel level warning
    if fuel_level is not None and fuel_level < 6:
        refuel = True
    elif fuel_level is not None and fuel_level > 10:
        refuel = False

    if refuel != old_refuel or clear is True:
        if refuel is False:
            screen.blit(FUEL_PUMP_BLACK, (545, 350))
        else:
            screen.blit(FUEL_PUMP_YELLOW, (545, 350))
        old_refuel = refuel
        display_update.append((545, 350, 50, 50))

    # Errors
    error_list = []
    if errors != 0:
        error_list = error_flags(errors)

    # Battery voltage low warning
    if batt_v < 11.3 or batt_v < 13 and rpm > 0:
        error_list.append("Battery " + str(batt_v) + "V")

    if error_list != old_error_list or cpu_timer < time.monotonic() or clear is True:
        cpu_timer = time.monotonic() + 1
        if len(error_list) == 0:
            pygame.draw.rect(screen, LIGHT_BLUE, (0, 440, 800, 40))
            cpu_temp = getCPUtemperature()
            cpu_clock = getCPUclock()
            cpu_stats_text = font_30.render("Cpu: " + cpu_temp + ", " + cpu_clock + " MHz",
                                            True, WHITE, LIGHT_BLUE)
            screen.blit(cpu_stats_text, (0, 443))
        else:
            errors_text = font_30.render("Errors " + str(len(error_list)) + ": ", True, WHITE, RED)
            errors_r = font_30.render(", ".join(error_list), True, WHITE, RED)
            pygame.draw.rect(screen, RED, (0, 440, 800, 40))
            screen.blit(errors_text, (0, 443))
            screen.blit(errors_r, (135, 443))
        old_error_list = error_list
        clear = False
        display_update.append((0, 440, 800, 40))

    if touch:
        # Pick a new unit from menu
        for x in range(6):
            if unit_change == x:
                units[x] = menu(pos)
                if units[x] is not None:
                    units_r[x] = font_20.render(title_text_units[units[x]], True, WHITE, BLACK)
                    unit_change = None
                    clear = True
                    units_ok = True
                else:
                    units_ok = False
        # Enable menu draw
        for x in range(6):
            if clear is False and pygame.Rect.collidepoint(unit_buttons[x], pos):
                draw_menu = True
                unit_change = x
        touch = False

        # Saving to memory
        if clear:
            units_memory = open(PATH + "units_memory.txt", "w")
            for x in range(len(units)):
                units_memory.write(str(units[x]) + "\n")
            units_memory.close()

    if draw_menu is True:
        screen.fill((60, 60, 60))

        def create_rect(x, y, text):
            pygame.draw.rect(screen, BLACK, [x, y, 190, 70], border_radius=10)
            name = font_20.render(text, True, WHITE)
            screen.blit(name, (x + 15, y + 20))
            return pygame.Rect(x, y, 190, 70)

        # Coordinates
        coordinates_x = []
        coordinates_y = []
        coordinate_y = 5
        coordinate_x = 5
        for x in range(6):
            coordinates_y.append(coordinate_y)
            coordinate_y += 80
        for x in range(4):
            coordinates_x.append(coordinate_x)
            coordinate_x += 200

        # Buttons
        rpm_button = create_rect(coordinates_x[0], coordinates_y[0], "RPM")
        tps_button = create_rect(coordinates_x[1], coordinates_y[0], "TPS")
        iat_button = create_rect(coordinates_x[2], coordinates_y[0], "IAT")
        map_button = create_rect(coordinates_x[3], coordinates_y[0], "MAP")
        inj_pw_button = create_rect(coordinates_x[0], coordinates_y[1], "Inj pw.")
        oil_t_button = create_rect(coordinates_x[1], coordinates_y[1], "Oil temp.")
        oil_p_button = create_rect(coordinates_x[2], coordinates_y[1], "Oil pressure")
        fuel_p_button = create_rect(coordinates_x[3], coordinates_y[1], "Fuel pressure")
        clt_t_button = create_rect(coordinates_x[0], coordinates_y[2], "Coolant temp.")
        ign_ang_button = create_rect(coordinates_x[1], coordinates_y[2], "Ignition angle")
        dwell_button = create_rect(coordinates_x[2], coordinates_y[2], "Dwell time")
        lambda_button = create_rect(coordinates_x[3], coordinates_y[2], "Lambda")
        lambda_corr_button = create_rect(coordinates_x[0], coordinates_y[3], "Lambda corr.")
        egt_1_button = create_rect(coordinates_x[1], coordinates_y[3], "EGT 1")
        egt_2_button = create_rect(coordinates_x[2], coordinates_y[3], "EGT 2")
        batt_v_button = create_rect(coordinates_x[3], coordinates_y[3], "Battery voltage")
        ethanol_cont_button = create_rect(coordinates_x[0], coordinates_y[4], "Ethanol content")
        dbw_pos_button = create_rect(coordinates_x[1], coordinates_y[4], "Dbw position")
        boost_t_button = create_rect(coordinates_x[2], coordinates_y[4], "Boost target")
        dsg_mode_button = create_rect(coordinates_x[3], coordinates_y[4], "DSG Mode")
        lambda_t_button = create_rect(coordinates_x[0], coordinates_y[5], "Lambda target")
        fuel_used_button = create_rect(coordinates_x[1], coordinates_y[5], "Fuel used")
        fuel_level_button = create_rect(coordinates_x[2], coordinates_y[5], "Fuel level")
        fuel_consumption_button = create_rect(coordinates_x[3], coordinates_y[5], "Fuel consum.")

        pygame.display.flip()
        draw_menu = False

    # Update screen
    if unit_change is None:
        pygame.display.update(display_update)

    # Close the program in case of interrupt
    if loop is False:
        odometer = odometer_save(speed_sum, speed_sum_counter, distance_timer, odometer, PATH)
        pygame.quit()
        if TEST_MODE is False:
            close_io()
