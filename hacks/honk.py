import lcd_bus
from micropython import const
from machine import I2C, Pin, SPI
# from nxp_periph.GPIO import PCA9554

# Boot up the IO Expander
# io_exp_i2c = I2C(0, scl=Pin(15), sda=Pin(16), freq=100000)
# io_exp = PCA9554(io_exp_i2c, 0x40)
# io_exp.config([0xFF])


# LCD parameters
_WIDTH = const(320)
_HEIGHT = const(320)
_DEPTH = const(16)

# LCD SPI Bus
# Using 
_HOST = const(1)
_FREQ = const(80 * 1000 * 1000)
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

lcd_spi_bus = SPI.Bus(
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
    display_width=320,
    display_height=320,
    backlight_pin=_BACKLIGHT,
    reset_pin=_RESET,
    color_space=lv.COLOR_FORMAT.RGB565,
)

display.set_power(True)
display.init()
display.set_backlight(100)

import task_handler

th = task_handler.TaskHandler()

scrn = lv.screen_active()
scrn.set_style_bg_color(lv.color_hex(0x0088AA), 0)