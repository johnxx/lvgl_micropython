
from micropython import const  # NOQA
import display_driver_framework

import lvgl as lv

STATE_HIGH = display_driver_framework.STATE_HIGH
STATE_LOW = display_driver_framework.STATE_LOW
STATE_PWM = display_driver_framework.STATE_PWM

BYTE_ORDER_RGB = display_driver_framework.BYTE_ORDER_RGB
BYTE_ORDER_BGR = display_driver_framework.BYTE_ORDER_BGR

_WRITE_CMD = const(0x02)
_READ_CMD = const(0x0B)
_WRITE_COLOR = const(0x32)

_MADCTL_MV = const(0x20)
_MADCTL_MX = const(0x40)
_MADCTL_MY = const(0x80)


class ST77916(display_driver_framework.DisplayDriver):

    _ORIENTATION_TABLE = (
        _MADCTL_MX,
        _MADCTL_MV | _MADCTL_MY | _MADCTL_MX,
        _MADCTL_MY,
        _MADCTL_MV
    )

    @staticmethod
    def __quad_spi_read_cmd_modifier(cmd):
        cmd <<= 8
        cmd |= _READ_CMD << 24
        return cmd

    @staticmethod
    def __quad_spi_cmd_modifier(cmd):
        cmd <<= 8
        cmd |= _WRITE_CMD << 24
        return cmd

    def __init__(
        self,
        data_bus,
        display_width,
        display_height,
        frame_buffer1=None,
        frame_buffer2=None,
        reset_pin=None,
        reset_state=STATE_HIGH,
        power_pin=None,
        power_on_state=STATE_HIGH,
        backlight_pin=None,
        backlight_on_state=STATE_HIGH,
        offset_x=0,
        offset_y=0,
        color_byte_order=BYTE_ORDER_RGB,
        color_space=lv.COLOR_FORMAT.RGB888,  # NOQA
        rgb565_byte_swap=False,  # NOQA
    ):

        num_lanes = data_bus.get_lane_count()

        self.__cmd_modifier = self.__quad_spi_cmd_modifier
        self.__read_cmd_modifier = self.__quad_spi_read_cmd_modifier
        _cmd_bits = 32

        super().__init__(
            data_bus,
            display_width,
            display_height,
            frame_buffer1,
            frame_buffer2,
            reset_pin,
            reset_state,
            power_pin,
            power_on_state,
            backlight_pin,
            backlight_on_state,
            offset_x,
            offset_y,
            color_byte_order,
            color_space,  # NOQA
            # we don't need to sue RGB565 byte swap so we override it
            rgb565_byte_swap,
            _cmd_bits=_cmd_bits,
            _param_bits=8,
            _init_bus=True
        )


    def set_params(self, cmd, params=None):
        cmd = self.__cmd_modifier(cmd)
        print("Sending cmd 0x{:08X} with params 0x{:02X}".format(cmd, params[0]))
        self._data_bus.tx_param(cmd, params)


    def get_params(self, cmd, params):
        cmd = self.__read_cmd_modifier(cmd)
        self._data_bus.rx_param(cmd, params)
        print("Sent cmd 0x{:02X} and got params {}".format(cmd, str(params)))
