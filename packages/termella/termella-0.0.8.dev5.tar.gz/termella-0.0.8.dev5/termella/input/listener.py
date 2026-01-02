import sys
import os
import re

MOUSE_RE = re.compile(r'\x1b\[<(\d+);(\d+);(\d+)([Mm])')

class InputListener:
    """
    Reads a single keypress from STDIN without blocking line buffering.
    Returns normalized key names: 'UP', 'DOWN', 'ENTER', or the char.
    """
    def __init__(self):
        self._win_old_mode = None

    def enable_mouse(self):
        if os.name == 'nt':
            from .win_input import enable_mouse_mode
            self._win_old_mode = enable_mouse_mode()

    def disable_mouse(self):
        if os.name == 'nt' and self._win_old_mode:
            from .win_input import disable_mouse_mode
            disable_mouse_mode(self._win_old_mode)

    def key_available(self):
        """Returns True if a key is waiting to be read."""
        if os.name == 'nt':
            import msvcrt
            return msvcrt.kbhit()
            from .win_input import get_num_events
            return get_num_events() > 0
        else:
            import select
            dr, dw, de = select.select([sys.stdin], [], [], 0)
            return bool(dr)

    def read_key(self):
        """Waits for a single keypress and returns it."""
        if os.name == 'nt':
            return self._read_windows_api()
        else:
            return self._read_unix()
        
    def _read_windows_api(self):
        from .win_input import read_input_record, KEY_EVENT, MOUSE_EVENT

        while True:
            record = read_input_record()

            if record.EventType == KEY_EVENT:
                if not record.Event.KeyEvent.bKeyDown: continue

                vk = record.Event.KeyEvent.wVirtualKeyCode
                char = record.Event.KeyEvent.uChar.UnicodeChar

                if vk == 0x26: return 'UP'
                if vk == 0x28: return 'DOWN'
                if vk == 0x25: return 'LEFT'
                if vk == 0x27: return 'RIGHT'
                if vk == 0x1B: return 'ESC'
                if vk == 0x0D: return 'ENTER'

                if char > 0:
                    return chr(char)
                
            elif record.EventType == MOUSE_EVENT:
                x = record.Event.MouseEvent.dwMousePosition.X
                y = record.Event.MouseEvent.dwMousePosition.Y
                btn = record.Event.MouseEvent.dwButtonState

                x += 1
                y += 1

                if btn == 1: return f"CLICK_LEFT {x} {y}"
                if btn == 2: return f"CLICK_RIGHT {x} {y}"

                return None
    
    def _read_unix(self):
        import tty
        import termios
        import select

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)

            # Handle Escape Sequences (Arrows)
            if ch == '\x1b':
                # Check if there is more data ready to read (timeout 0.1s)
                # If no data, it's just the ESC key.
                dr, dw, de = select.select([sys.stdin], [], [], 0.01)
                if not dr: return 'ESC'
                seq = sys.stdin.read(10)
                full_seq = '\x1b' + seq

                match = MOUSE_RE.match(full_seq)
                if match:
                    btn = int(match.group(1))
                    x = int(match.group(2))
                    y = int(match.group(3))
                    action = match.group(4)

                    if action == 'M':
                        if btn == 0: return f"CLICK_LEFT {x} {y}"
                        if btn == 2: return f"CLICK_RIGHT {x} {y}"
                        if btn >= 64: return "SCROLL"
                    return None

                if seq.startswith('[A'): return 'UP'
                if seq.startswith('[B'): return 'DOWN'
                if seq.startswith('[C'): return 'RIGHT'
                if seq.startswith('[D'): return 'LEFT'
                
                return 'ESC'
            
            if ch == '\r' or ch == '\n': return 'ENTER'
            if ch == ' ': return 'SPACE'
            if ch == '\x03': raise KeyboardInterrupt # Handle Ctrl+C
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)