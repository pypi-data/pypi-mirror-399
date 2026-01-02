import ctypes
from ctypes import wintypes
import time

# basic Windows stuff
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

# long result for 64-bit compatibility
LRESULT = ctypes.c_longlong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long

WNDPROC = ctypes.WINFUNCTYPE(
    LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM
)

# set some function signatures
user32.DefWindowProcW.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
user32.DefWindowProcW.restype = LRESULT
user32.GetMessageW.argtypes = (ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT)
user32.GetMessageW.restype = wintypes.BOOL
user32.CreateWindowExW.restype = wintypes.HWND

class Window:
    def __init__(self, title="purewind", width=600, height=400):
        self.title = title
        self.width = width
        self.height = height
        self.running = True
        self.keys = set()
        self.mouse_x = 0
        self.mouse_y = 0
        self.last_time = time.perf_counter()
        self.fps_timer = self.last_time
        self.frames = 0
        self.locked_fps = 0  # 0 = unlimited
        self.hInstance = kernel32.GetModuleHandleW(None)
        self.class_name = f"pw_{id(self)}"

        # New callback features
        self.key_callbacks = {}        # vk_code -> function
        self.mouse_move_callback = None

        self._register_class()
        self._create_window()

    # simple log helper
    def _log(self, msg):
        print(f"[purewind] {msg}")

    # handle messages from Windows
    def _WndProc(self, hwnd, msg, wparam, lparam):
        if msg == 0x0010:  # window close
            self.running = False
            user32.PostQuitMessage(0)
            self._log("window close requested")
            return 0
        elif msg == 0x0100:  # key down
            self.keys.add(wparam)
            if wparam in self.key_callbacks:
                self.key_callbacks[wparam]()
        elif msg == 0x0101:  # key up
            self.keys.discard(wparam)
        elif msg == 0x0200:  # mouse move
            self.mouse_x = lparam & 0xFFFF
            self.mouse_y = (lparam >> 16) & 0xFFFF
            if self.mouse_move_callback:
                self.mouse_move_callback(self.mouse_x, self.mouse_y)
        elif msg == 0x0005:  # window resized
            self.width = lparam & 0xFFFF
            self.height = (lparam >> 16) & 0xFFFF
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    # register a simple window class
    def _register_class(self):
        self._wndproc = WNDPROC(self._WndProc)

        class WNDCLASS(ctypes.Structure):
            _fields_ = [
                ("style", wintypes.UINT),
                ("lpfnWndProc", WNDPROC),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", wintypes.HINSTANCE),
                ("hIcon", wintypes.HICON),
                ("hCursor", wintypes.HCURSOR),
                ("hbrBackground", wintypes.HBRUSH),
                ("lpszMenuName", wintypes.LPCWSTR),
                ("lpszClassName", wintypes.LPCWSTR),
            ]

        wc = WNDCLASS()
        wc.lpfnWndProc = self._wndproc
        wc.hInstance = self.hInstance
        wc.lpszClassName = self.class_name
        wc.hCursor = user32.LoadCursorW(None, 32512)
        wc.hbrBackground = ctypes.c_void_p(5)
        user32.RegisterClassW(ctypes.byref(wc))
        self._log("registered window class")

    # create the main window
    def _create_window(self):
        self.hwnd = user32.CreateWindowExW(
            0,
            self.class_name,
            self.title,
            0x00CF0000,
            100,
            100,
            self.width,
            self.height,
            None,
            None,
            self.hInstance,
            None,
        )
        user32.ShowWindow(self.hwnd, 1)
        user32.UpdateWindow(self.hwnd)
        self._log("created main window")

    # hooks you can override
    def update(self, dt):
        if 0x1B in self.keys:
            self.close()
            self._log("ESC pressed, quitting")

    def render(self):
        pass

    # helpers for input & window
    def getMousePosition(self):
        return (self.mouse_x, self.mouse_y)

    def isKeyPressed(self, vk_code):
        return vk_code in self.keys

    def setWindowTitle(self, title):
        self.title = title
        user32.SetWindowTextW(self.hwnd, title)

    def resizeWindow(self, width, height):
        self.width = width
        self.height = height
        user32.MoveWindow(self.hwnd, 100, 100, width, height, True)

    def close(self):
        self.running = False
        user32.PostQuitMessage(0)
        self._log("window closed")

    def wait(self, seconds):
        time.sleep(seconds)

    def lockFPS(self, fps):
        self.locked_fps = fps

    # draw text
    def drawText(self, text, x, y, color=0x000000, font_name="Arial", font_size=20):
        hdc = user32.GetDC(self.hwnd)
        hFont = gdi32.CreateFontW(-font_size, 0, 0, 0, 400, 0, 0, 0, 0, 0, 0, 0, 0, font_name)
        gdi32.SelectObject(hdc, hFont)
        gdi32.SetTextColor(hdc, color)
        gdi32.SetBkMode(hdc, 1)
        gdi32.TextOutW(hdc, x, y, text, len(text))
        gdi32.DeleteObject(hFont)
        user32.ReleaseDC(self.hwnd, hdc)

    # assign callback for key press
    def onKeyPress(self, vk_code, callback):
        """Assign a function to be called when a key is pressed."""
        self.key_callbacks[vk_code] = callback

    # assign callback for mouse movement
    def onMouseMove(self, callback):
        """Assign a function to be called when the mouse moves."""
        self.mouse_move_callback = callback

    # main loop
    def run(self):
        msg = wintypes.MSG()
        while self.running:
            start_time = time.perf_counter()

            # handle messages
            while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                if msg.message == 0x0012:
                    self.running = False
                    break
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

            now = time.perf_counter()
            dt = now - self.last_time
            self.last_time = now

            # hooks
            self.update(dt)
            self.render()

            # fps counter
            self.frames += 1
            if now - self.fps_timer >= 1.0:
                user32.SetWindowTextW(
                    self.hwnd,
                    f"{self.title} | FPS: {self.frames} | {self.width}x{self.height} | Mouse: {self.mouse_x},{self.mouse_y}"
                )
                self._log(f"FPS: {self.frames}, size: {self.width}x{self.height}, mouse: {self.mouse_x},{self.mouse_y}")
                self.frames = 0
                self.fps_timer = now

            # fps limiter
            if self.locked_fps > 0:
                frame_time = time.perf_counter() - start_time
                target = 1.0 / self.locked_fps
                if frame_time < target:
                    time.sleep(target - frame_time)

# shortcut function
def createWindow(title="purewind", width=600, height=400):
    return Window(title, width, height)
