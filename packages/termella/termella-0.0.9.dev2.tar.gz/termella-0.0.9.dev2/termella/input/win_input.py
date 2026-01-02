import ctypes
from ctypes import Structure, Union, c_char, c_long, c_ulong, c_short, c_ushort, byref

# Constants
STD_INPUT_HANDLE = -10
ENABLE_MOUSE_INPUT = 0x0010
ENABLE_EXTENDED_FLAGS = 0x0080
ENABLE_QUICK_EDIT_MODE = 0x0040

KEY_EVENT = 0x0001
MOUSE_EVENT = 0x0002

class COORD(Structure):
    _fields_ = [("X", c_short), ("Y", c_short)]

# Define Union for Char
class CharUnion(Union):
    _fields_ = [("UnicodeChar", c_ushort), ("AsciiChar", c_char)]

class KEY_EVENT_RECORD(Structure):
    _fields_ = [
        ("bKeyDown", c_long),
        ("wRepeatCount", c_short),
        ("wVirtualKeyCode", c_short),
        ("wVirtualScanCode", c_short),
        ("uChar", CharUnion), # Use the subclass
        ("dwControlKeyState", c_ulong)
    ]

class MOUSE_EVENT_RECORD(Structure):
    _fields_ = [
        ("dwMousePosition", COORD),
        ("dwButtonState", c_ulong),
        ("dwControlKeyState", c_ulong),
        ("dwEventFlags", c_ulong)
    ]

# Define Union for Event
class EventUnion(Union):
    _fields_ = [
        ("KeyEvent", KEY_EVENT_RECORD),
        ("MouseEvent", MOUSE_EVENT_RECORD)
    ]

class INPUT_RECORD(Structure):
    _fields_ = [
        ("EventType", c_short),
        ("Event", EventUnion) # Use the subclass
    ]

kernel32 = ctypes.windll.kernel32

def enable_mouse_mode():
    hStdIn = kernel32.GetStdHandle(STD_INPUT_HANDLE)
    mode = c_ulong()
    kernel32.GetConsoleMode(hStdIn, byref(mode))
    new_mode = (mode.value | ENABLE_MOUSE_INPUT | ENABLE_EXTENDED_FLAGS) & ~ENABLE_QUICK_EDIT_MODE
    kernel32.SetConsoleMode(hStdIn, new_mode)
    return mode.value 

def disable_mouse_mode(old_mode):
    hStdIn = kernel32.GetStdHandle(STD_INPUT_HANDLE)
    kernel32.SetConsoleMode(hStdIn, old_mode)

def read_input_record():
    hStdIn = kernel32.GetStdHandle(STD_INPUT_HANDLE)
    record = INPUT_RECORD()
    read_count = c_ulong()
    kernel32.ReadConsoleInputW(hStdIn, byref(record), 1, byref(read_count))
    return record
    
def get_num_events():
    hStdIn = kernel32.GetStdHandle(STD_INPUT_HANDLE)
    count = c_ulong()
    kernel32.GetNumberOfConsoleInputEvents(hStdIn, byref(count))
    return count.value