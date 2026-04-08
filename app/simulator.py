"""
Simulator wrapper: bridges the GUI to demura_functions.Meta_Demura.
Runs the demura pipeline in a background thread with stdout capture.
"""

import sys
import os
import io
import threading
import json


class DemuraSimulator:
    """Wraps Meta_Demura for GUI-driven execution."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self._running = False

    def run_pipeline(self, config: dict, log_callback=None, done_callback=None):
        """Run the full demura pipeline in a background thread."""
        if self._running:
            if log_callback:
                log_callback("[WARNING] Pipeline already running.\n")
            return
        self._running = True

        def _worker():
            try:
                old_cwd = os.getcwd()
                os.chdir(self.base_dir)

                # Add project root to sys.path so demura_functions can be imported
                if self.base_dir not in sys.path:
                    sys.path.insert(0, self.base_dir)

                # Redirect stdout to capture print statements
                old_stdout = sys.stdout
                sys.stdout = _LogCapture(log_callback)

                try:
                    # Re-import each time to pick up config changes
                    import importlib
                    import app.demura_functions as df
                    importlib.reload(df)

                    processor = df.Meta_Demura(config)
                    success = processor.run()

                    if success:
                        if log_callback:
                            log_callback("\n✅  Demura Process Completed Successfully.\n")
                    else:
                        if log_callback:
                            log_callback("\n❌  Demura process failed.\n")
                except Exception as e:
                    if log_callback:
                        log_callback(f"\n❌  Error: {e}\n")
                finally:
                    sys.stdout = old_stdout
                    os.chdir(old_cwd)

            finally:
                self._running = False
                if done_callback:
                    done_callback()

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    @property
    def is_running(self):
        return self._running


class _LogCapture:
    """File-like object that sends write() calls to a callback."""

    def __init__(self, callback):
        self._callback = callback

    def write(self, text):
        if text and self._callback:
            self._callback(text)

    def flush(self):
        pass
