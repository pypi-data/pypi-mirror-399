import platform
import subprocess
import multiprocessing
import os
import time

# This variable will store the process globally within the module
_current_process = None

def _windows_worker(file_path):
    """Internal worker for Windows background play."""
    try:
        from playsound3 import playsound
        playsound(file_path, block=True)
    except Exception as e:
        print(f"ez_background_music error: {e}")

def start_music(file_path):
    """
    Starts background music in a cross-platform, non-blocking way.
    Works in Terminal, CMD, and compiled Apps.
    """
    global _current_process
    
    # 1. Validate file exists
    if not os.path.exists(file_path):
        print(f"ez_background_music error: File not found at {file_path}")
        return False

    system_os = platform.system()

    try:
        if system_os == "Darwin":  # macOS
            # Spawn a native system process
            _current_process = subprocess.Popen(
                ['afplay', file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True

        elif system_os == "Windows":  # Windows
            # Use Multiprocessing to prevent the CLI from choking the thread
            _current_process = multiprocessing.Process(target=_windows_worker, args=(file_path,))
            _current_process.daemon = True # Kill music if main script crashes
            _current_process.start()
            return True

        else:  # Linux
            # Try native Linux pulse audio player first
            try:
                _current_process = subprocess.Popen(
                    ['paplay', file_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True
            except FileNotFoundError:
                # Fallback to multiprocessing worker
                _current_process = multiprocessing.Process(target=_windows_worker, args=(file_path,))
                _current_process.start()
                return True

    except Exception as e:
        print(f"ez_background_music failed to start: {e}")
        return False

def stop_music():
    """Stops the music process started by this library."""
    global _current_process
    
    if _current_process is None:
        return

    system_os = platform.system()
    
    try:
        if system_os == "Darwin" or system_os == "Linux":
            _current_process.terminate() # Kill the subprocess
        elif system_os == "Windows":
            if isinstance(_current_process, multiprocessing.Process):
                _current_process.terminate()
        
        _current_process = None
    except Exception:
        # Emergency cleanup if the process handles are lost
        if system_os == "Darwin":
            os.system("killall afplay > /dev/null 2>&1")