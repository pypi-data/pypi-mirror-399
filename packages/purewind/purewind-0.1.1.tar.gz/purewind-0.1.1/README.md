# purewind 🌬️

A **tiny Windows‑only** Python wrapper that creates a native window and gives you a simple game‑loop, input handling, and immediate‑mode text rendering via the Win32 API.  
Only the standard library (`ctypes`) is required, so there are no external binary dependencies to ship.

---  

# CHANGELOG
```markdown
0.1.1:
[+] Added key press callback system
[+] Added mouse move callback system
[+] Added onKeyPress() and onMouseMove() helper methods
[*] Updated _WndProc to trigger callbacks automatically
```

## How to install

```bash
pip install purewind