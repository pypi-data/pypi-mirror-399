import time
from smbus2 import SMBus
from .lcd_api import LcdApi

MASK_RS = 0x01
MASK_E  = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4

class I2cLcd(LcdApi):

    def __init__(self, i2c_bus, i2c_addr, num_lines, num_columns):
        self.bus = SMBus(i2c_bus)
        self.addr = i2c_addr

        self.bus.write_byte(self.addr, 0x00)
        time.sleep(0.02)

        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.005)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.001)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.001)

        self.hal_write_init_nibble(self.LCD_FUNCTION)
        time.sleep(0.001)

        super().__init__(num_lines, num_columns)

        cmd = self.LCD_FUNCTION
        if num_lines > 1:
            cmd |= self.LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)

    def hal_write_init_nibble(self, nibble):
        byte = ((nibble >> 4) & 0x0F) << SHIFT_DATA
        self.bus.write_byte(self.addr, byte | MASK_E)
        self.bus.write_byte(self.addr, byte)

    def hal_backlight_on(self):
        self.bus.write_byte(self.addr, 1 << SHIFT_BACKLIGHT)

    def hal_backlight_off(self):
        self.bus.write_byte(self.addr, 0x00)

    def hal_write_command(self, cmd):
        self._write(cmd, 0)
        if cmd <= 3:
            time.sleep(0.005)

    def hal_write_data(self, data):
        self._write(data, MASK_RS)

    def _write(self, value, mode):
        high = mode | (self.backlight << SHIFT_BACKLIGHT) | ((value >> 4) << SHIFT_DATA)
        low  = mode | (self.backlight << SHIFT_BACKLIGHT) | ((value & 0x0F) << SHIFT_DATA)

        self.bus.write_byte(self.addr, high | MASK_E)
        self.bus.write_byte(self.addr, high)
        self.bus.write_byte(self.addr, low | MASK_E)
        self.bus.write_byte(self.addr, low)
