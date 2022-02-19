import board
import busio
import time
from adafruit_bus_device.i2c_device import I2CDevice

'''
- 2022/02/19 ver.0.04
- Author : emguse
- Applied to Akizukidenshi's small I2C character display 8X2 'AQM0802A'
- Commands are the same as HD44780 series controllers and can also be used in SC1608
'''

_I2C_ADRESS=0x3e
_FOLLOWER_CTL = 0x6C

_CLEAR_DISP = 0x01
_RETURN_HOME = 0x02

_ENTRY_MODE_SET = 0x04
_INC_DEC = True
_SHIFT_ENTRY = False

_DISP_ON_OFF = 0x08
_DISP_ON_OFF_CTL = True # True = ON
_CURSOR_ON_OFF_CTL = True # True = ON
_CURSOR_BLINK_CTL = True # True = ON

_CURSOR_DISP_SHIFT = 0x10
_SCREEN_CURSOL_SELECT = False
_RIGHT_LEFT_SELECT = True

_FUNCTION_SET = 0x20 # const
_BIT_MODE_8 = True # True it means 8-bit bus mode with MPU 
_NUM_OF_LINE_2 = True # True is 2 lines
_DOUBLE_HEIGHT = False # True is double height font
_EXT_INSTRUCTION_SELECT = False

_SET_CGRAM = 0x40
_SET_DDRAM = 0x80

_IOSC_FREQ = 0x10
_BIAS = 0x04
_ADJ_IOSC_FREQ = 0x00

_INITIAL_CONT = 0x20
_COLMUNS = 8
_LINES = 2

class CharacterLcdAqm0802():
    def __init__(self, i2c, colmuns=_COLMUNS, lines=_LINES) -> None:
        self._device = I2CDevice(i2c, _I2C_ADRESS)
        self._inc_dec = _INC_DEC
        self._shift_entry = _SHIFT_ENTRY
        self._disp = _DISP_ON_OFF_CTL
        self._cursor = _CURSOR_ON_OFF_CTL
        self._cur_blink = _CURSOR_BLINK_CTL
        self._screen_cursor_select = _SCREEN_CURSOL_SELECT
        self._right_left_select = _RIGHT_LEFT_SELECT
        self._if_data_len = _BIT_MODE_8
        self._num_of_line = _NUM_OF_LINE_2 # True is 2 lines
        self._double_height = _DOUBLE_HEIGHT
        self._instruction_table = _EXT_INSTRUCTION_SELECT
        self.contrast = _INITIAL_CONT
        self.colmuns = colmuns
        self.lines = lines
        self.init_display()
    def init_display(self):
        self._instruction_table = False
        self._function_set(self._if_data_len, self._num_of_line, self._double_height, self._instruction_table)
        time.sleep(0.0000263)
        self._instruction_table = True
        self._function_set(self._if_data_len, self._num_of_line, self._double_height, self._instruction_table)
        time.sleep(0.0000263)
        self._set_iosc_freq()
        time.sleep(0.0000263)
        self._contrast(_INITIAL_CONT)
        time.sleep(0.0000263)
        self._set_folower()
        time.sleep(0.2)
        self._instruction_table = False
        self._function_set(self._if_data_len, self._num_of_line, self._double_height, self._instruction_table)
        time.sleep(0.0000263)
        self._display_onoff()
        time.sleep(0.0000263)
        self.clear_disp()
        time.sleep(0.108)
        # Initialize changed settings
        self.set_entry_mode()
        time.sleep(0.0000263)
        self.return_home()
    def _send_cmmand(self, com):
        with self._device:
            self._device.write(bytes([0x00, com]))
    def send_chr(self, s):
        with self._device:
            for c in s:
                self._device.write(bytes([0x40, ord(c)]))
    def cut(self, s):
        s = s[:_COLMUNS]
        return s
    def _function_set(self, bit=None, lines=None, double=None, is_=None ):
        if bit is None:
            bit = self._if_data_len
        if lines is None:
            lines = self._num_of_line
        if double is None:
            double = self._double_height
        if is_ is None:
            is_ = self._instruction_table
        self._send_cmmand(_FUNCTION_SET | (bit << 4) | (lines << 3) | (double << 2) | is_)
    def _set_iosc_freq(self):
        self._send_cmmand(_IOSC_FREQ | _BIAS | _ADJ_IOSC_FREQ)
    def _contrast(self, cont):
        c1234 = cont & 0b00001111
        contrast_set = 0b01110000 | c1234
        c56 = (cont & 0b00110000) >> 4
        pw_icon_cont = 0b01010100 | c56
        self._send_cmmand(contrast_set)
        time.sleep(0.0000263)
        self._send_cmmand(pw_icon_cont)
    def _set_folower(self):
        self._send_cmmand(_FOLLOWER_CTL)
    def clear_disp(self):
        self._send_cmmand(_CLEAR_DISP)
    def return_home(self):
        self._send_cmmand(_RETURN_HOME)
    def _entry_mode(self):
        self._send_cmmand(_ENTRY_MODE_SET | (self._inc_dec << 1) | self._shift_entry)
    def _display_onoff(self):
        self._send_cmmand(_DISP_ON_OFF | (self._disp << 2) | (self._cursor << 1) | self._cur_blink)
    def _cursor_disp_shift(self):
        self._send_cmmand(_CURSOR_DISP_SHIFT | (self._screen_cursor_select << 3) | (self._right_left_select << 2))
    def _set_DDRAM_pos(self, pos=0x00):
        self._send_cmmand(_SET_DDRAM | pos)
    # Functions to change settings
    def set_entry_mode(self, dir=_INC_DEC, shift=_SHIFT_ENTRY):
        '''Shift the display to the left  = 1,1 , 
           Shift the display to the right = 1,0'''
        self._inc_dec = dir
        self._shift_entry = shift
        self._entry_mode()
    def set_display_on_off(self, state=_DISP_ON_OFF_CTL):
        '''on = 1 / off = 0'''
        self._disp = state
        self._display_onoff()
    def set_cursor_on_off(self, state=_CURSOR_ON_OFF_CTL):
        '''on = 1 / off = 0'''
        self._cursor = state
        self._display_onoff()
    def set_blink_on_off(self, state=_CURSOR_BLINK_CTL):
        '''on = 1 / off = 0'''
        self._cur_blink = state
        self._display_onoff()
    def set_cursor_disp_shift(self, sc=_SCREEN_CURSOL_SELECT, dir=_RIGHT_LEFT_SELECT):
        '''
        - cursor to the left   = 0,0
        - cursor to the right  = 0,1
        - display to the left  = 1,0
        - display to the right = 1,1
        '''
        self._screen_cursor_select = sc
        self._right_left_select = dir
        self._cursor_disp_shift()
    def set_display_lines(self, line=_NUM_OF_LINE_2):
        '''
        True = 2 lines display mode
        False = 1 line display mode
        '''
        self._num_of_line = line
        self._function_set(lines=self._num_of_line)
    def set_double_hight_fonts(self, hight=_DOUBLE_HEIGHT):
        '''
        - When using double height, display Lines must be set to 1 line
        - If the EXT option pin is connected to high, the font will not be double height
        - In 'AQM0802A', the EXT option pin is connected to Hi by the internal hardware, so the double height is not enabled.
        '''
        self._double_height = hight
        self._function_set(double=self._double_height)
    def set_contrast(self, contrast=_INITIAL_CONT):
        if contrast <= 0x00:
            contrast = 0x00
        if contrast >= 0x3F:
            contrast = 0x3F
        self._instruction_table = True
        self._function_set(is_=self._instruction_table)
        time.sleep(0.0000263)
        self._contrast(contrast)
        time.sleep(0.0000263)
        self._instruction_table = False
        self._function_set(is_=self._instruction_table)
    def move_cursor(self, colmun, line):
        if colmun >= _COLMUNS:
            colmun = _COLMUNS - 1
        if line >= _LINES:
            line = _LINES - 1
        self._send_cmmand(_SET_DDRAM | colmun | (line * 0x40))

    
def main():
    i2c = busio.I2C(board.GP3, board.GP2)
    lcd = CharacterLcdAqm0802(i2c)
    while True:
        print('Input string')
        s = input()
        #print(bytearray(s))
        #print(s == '@cls')
        if s == '@cls':
            lcd.clear_disp()
            continue
        if s == '@home':
            lcd.return_home()
            continue
        elif s == '@init display':
            lcd.init_display()
            time.sleep(0.0000263)
            lcd.set_entry_mode()
            time.sleep(0.0000263)
            lcd.set_display_on_off()
            time.sleep(0.0000263)
            lcd.set_cursor_on_off()
            time.sleep(0.0000263)
            lcd.set_blink_on_off()
            time.sleep(0.0000263)
            lcd.return_home()
            continue
        elif s == '@display to left':
            lcd.set_entry_mode(1, 1)
            continue
        elif s == '@display to right':
            lcd.set_entry_mode(1, 0)
            continue
        elif s == '@display on':
            lcd.set_display_on_off(1)
            continue
        elif s == '@display off':
            lcd.set_display_on_off(0)
            continue
        elif s == '@cursor on':
            lcd.set_cursor_on_off(1)
            continue
        elif s == '@cursor off':
            lcd.set_cursor_on_off(0)
            continue
        elif s == '@blink on':
            lcd.set_blink_on_off(1)
            continue
        elif s == '@blink off':
            lcd.set_blink_on_off(0)
            continue
        elif s == '@cursor to the left':
            lcd.set_cursor_disp_shift(0, 0)
            continue
        elif s == '@cursor to the right':
            lcd.set_cursor_disp_shift(0, 1)
            continue
        elif s == '@display to the left':
            lcd.set_cursor_disp_shift(1, 0)
            continue
        elif s == '@display to the right':
            lcd.set_cursor_disp_shift(1, 1)
            continue
        elif s == '@2lines':
            lcd.set_display_lines(1)
            continue
        elif s == '@1lines':
            lcd.set_display_lines(0)
            continue
        elif s == '@upper':
            lcd.move_cursor(0, 0)
            continue
        elif s == '@lower':
            lcd.move_cursor(0, 1)
            continue
        elif s == '@make lighter':
            lcd.contrast -= 1
            lcd.set_contrast(lcd.contrast)
            print('contrust set to {}'.format(hex(lcd.contrast)))
            continue
        elif s == '@make richer':
            lcd.contrast += 1
            lcd.set_contrast(lcd.contrast)
            print('contrust set to {}'.format(hex(lcd.contrast)))
            continue
        #lcd.clear_disp()
        if len(s) > lcd.colmuns:
            s = lcd.cut(s)
        lcd.send_chr(str(s))

if __name__ == "__main__":
    main()