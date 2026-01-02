import sys
import os
import re

MOUSE_RE = re.compile(r'\x1b\[<(\d+);(\d+);(\d+)([Mm])')

class InputListener:
    """
    Reads a single keypress from STDIN without blocking line buffering.
    Returns normalized key names: 'UP', 'DOWN', 'ENTER', or the char.
    """

    def key_available(self):
        """Returns True if a key is waiting to be read."""
        if os.name == 'nt':
            import msvcrt
            return msvcrt.kbhit()
        else:
            import select
            dr, dw, de = select.select([sys.stdin], [], [], 0)
            return bool(dr)

    def read_key(self):
        """Waits for a single keypress and returns it."""
        if os.name == 'nt':
            return self._read_windows()
        else:
            return self._read_unix()
        
    def _read_windows(self):
        import msvcrt
        key = msvcrt.getch()
        if key == b'\r': return 'ENTER'
        if key == b' ': return 'SPACE'
        if key == b'\x1b': return 'ESC' # Windows usually handles ESC directly
        if key == b'\xe0': # Special keys (arrows)
            key = msvcrt.getch()
            if key == b'H': return 'UP'
            if key == b'P': return 'DOWN'
            if key == b'K': return 'LEFT'
            if key == b'M': return 'RIGHT'
        return key.decode('utf-8', 'ignore')
    
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