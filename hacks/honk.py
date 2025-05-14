import display_driver_framework
import time
import machine
import lcd_bus
from micropython import const
from collections import deque

from i2c import I2C
i2c_bus = I2C.Bus(0, scl=10, sda=11, freq=100_000)
io_exp_i2c = I2C.Device(i2c_bus, 0x20)
# import io_expander_framework
# import tca9554
# tca9554._INPUT_PORT_REG = const(0x00)
# tca9554._OUTPUT_PORT_REG = const(0x01)
# tca9554._POLARITY_INVERSION_REG = const(0x02)
# tca9554._CONFIGURATION_REG = const(0x03)

# io_expander_framework.Pin.set_device(io_exp_i2c)
# ex2 = tca9554.Pin(tca9554.EXIO2, mode=io_expander_framework.Pin.OUT, pull=io_expander_framework.Pin.PULL_DOWN, value=1)
# ex2.value(0)
# time.sleep_ms(10)
# ex2.value(1)
# time.sleep_ms(50)

# LCD parameters
_WIDTH = const(360)
_HEIGHT = const(360)
_DEPTH = const(16)

# LCD SPI Bus
# Using 
_HOST = const(1)
_FREQ = const(50 * 1000 * 1000)
_SCK = const(40)
_CS = const(21)
_DC = const(0)
_SDA0 = const(46)
_SDA1 = const(45)
_SDA2 = const(42)
_SDA3 = const(41)

# LCD GPIO Pins
_BACKLIGHT = const(5)
_RESET = const(0)
_TEAR = const(24)

lcd_spi_bus = machine.SPI.Bus(
    host=_HOST,
    mosi=_SDA0,
    miso=_SDA1,
    sck=_SCK,
    quad_pins=(_SDA2, _SDA3), # type: ignore
)

display_bus = lcd_bus.SPIBus(
    spi_bus=lcd_spi_bus,
    freq=_FREQ,
    cs=_CS,
    dc=_DC,
    quad=True,
)

# lcd_spi_bus = SPI.Bus(
#     host=_HOST,
#     mosi=_SDA0,
#     miso=_SDA1,
#     sck=_SCK
# )
# 
# display_bus = lcd_bus.SPIBus(
#     spi_bus=lcd_spi_bus,
#     freq=_FREQ,
#     cs=_CS,
#     dc=_DC,
#     quad=False,
# )

# fb1 = display_bus.allocate_framebuffer(16 * 1024, lcd_bus.MEMORY_INTERNAL | lcd_bus.MEMORY_DMA)
# fb2 = display_bus.allocate_framebuffer(16 * 1024, lcd_bus.MEMORY_INTERNAL | lcd_bus.MEMORY_DMA)

import st77916
import lvgl as lv

display = st77916.ST77916(
    data_bus=display_bus,
    display_width=_WIDTH,
    display_height=_HEIGHT,
    backlight_pin=_BACKLIGHT,
    reset_pin=_RESET,
    color_space=lv.COLOR_FORMAT.RGB565,
    color_byte_order=st77916.BYTE_ORDER_BGR,
    rgb565_byte_swap=True,
)

display.set_power(False)
display.init()
display.set_backlight(100)

import fs_driver

fs_drv = lv.fs_drv_t()
fs_driver.fs_register(fs_drv, 'S')

import task_handler
th = task_handler.TaskHandler()

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex3(0x000), 0)

val = 0

big_font = lv.binfont_create(("S:/NotoSansDisplay-Regular-96.bin"))

big_label = lv.label(scrn)
big_label.set_style_text_font(big_font, 0)
big_label.set_style_text_color(lv.color_hex3(0xFFF), 0)
big_label.set_text(str(val))
big_label.align(lv.ALIGN.CENTER, 0, -90)


gauge = lv.arc(scrn)
gauge.set_size(_WIDTH - 5, _HEIGHT - 5)
gap_angle = 120
gauge.set_rotation(90 + int(gap_angle / 2))
gauge.set_bg_angles(0, 360 - gap_angle)
gauge.remove_style(None, lv.PART.KNOB)
# gauge.set_style_arc_color(lv.color_hex(0x900020), lv.PART.INDICATOR)
gauge.set_style_arc_width(10, 0)
gauge.set_style_arc_color(lv.color_hex(0x101010), 0)
gauge.set_value(0)
gauge.center()


chart = lv.chart(scrn)
chart.set_size(260, 160)
chart.align(lv.ALIGN.CENTER, 0, 35)
chart.set_range(lv.chart.AXIS.PRIMARY_Y, 0, 100)

chart.set_style_size(0, 0, lv.PART.INDICATOR)
chart.set_style_bg_color(lv.color_hex(0x010101), lv.PART.MAIN | lv.STATE.DEFAULT)
chart.set_style_line_color(lv.color_hex(0x101010), lv.PART.MAIN | lv.STATE.DEFAULT)
chart.set_style_border_color(lv.color_hex(0x101010), lv.PART.MAIN | lv.STATE.DEFAULT)

vals_len = 100
# vals = deque(list(range(vals_len)), vals_len)
vals = list(range(vals_len))
sers = chart.add_series(lv.color_hex(0x2196f3), lv.chart.AXIS.PRIMARY_Y)

chart.set_point_count(len(vals) - 1)
chart.set_ext_y_array(sers, vals)
chart.refresh()

# label = lv.label(scrn)
# label.set_text('HELLO WORLD!')
# label.align(lv.ALIGN.CENTER, 0, -50)

lv.screen_load(scrn)

import time
import random
def once_through():
    start_time = time.time_ns()
    for n in range(0, 100):
        n += random.randint(-10, 10)
        gauge.set_value(n)
        big_label.set_text(str(n))
        vals.pop(0)
        vals.append(n)
        # print(vals[:10])
        chart.set_ext_y_array(sers, vals)
        chart.refresh()
    end_time = time.time_ns()
    print(f'Drew {len(vals)} points in {(end_time - start_time) / 1000000} ms')

once_through()

# recv_buf = bytearray(4)
# recv_buf = bytearray(4)
# print(recv_buf)
# display.get_params(0x04, recv_buf)
# print(recv_buf)