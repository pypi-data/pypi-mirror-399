"""Core tracing functionality using sys.setprofile."""

import sys
import time
import os
from typing import Any, Dict, Optional, Set
from rich.console import Console

console = Console()


class FunctionTracer:
    """Traces function calls and execution times."""

    def __init__(self, threshold_ms: float = 100.0):
        """
        Initialize the function tracer.

        Args:
            threshold_ms: Threshold in milliseconds for marking slow functions.
        """
        self.threshold_ms = threshold_ms
        self.start_times: Dict[int, float] = {}
        self.old_profile = None
        self.traced_file: Optional[str] = None
        self.traced_file_dir: Optional[str] = None
        self.stdlib_paths: Set[str] = set()
        self._identify_stdlib_paths()

    def _identify_stdlib_paths(self) -> None:
        """Identify standard library and site-packages paths to exclude."""
        import sysconfig
        stdlib = sysconfig.get_path('stdlib')
        platstdlib = sysconfig.get_path('platstdlib')
        purelib = sysconfig.get_path('purelib')
        platlib = sysconfig.get_path('platlib')
        
        paths_to_add = [stdlib, platstdlib, purelib, platlib]
        for path in paths_to_add:
            if path:
                self.stdlib_paths.add(os.path.normcase(os.path.normpath(path)))

    def set_traced_file(self, filepath: str) -> None:
        """
        Set the file to trace.

        Args:
            filepath: Path to the script being traced.
        """
        abs_path = os.path.abspath(filepath)
        self.traced_file = os.path.normcase(os.path.normpath(abs_path))
        self.traced_file_dir = os.path.normcase(os.path.normpath(os.path.dirname(abs_path)))

    def _should_trace(self, frame: Any) -> bool:
        """
        Determine if a frame should be traced.

        Args:
            frame: The stack frame to check.

        Returns:
            True if the frame should be traced, False otherwise.
        """
        filename = frame.f_code.co_filename
        func_name = frame.f_code.co_name
        
        # Skip if filename indicates internal/generated code
        if not filename or filename.startswith('<') or filename == '<string>':
            return False
        
        # Normalize the filename for comparison
        try:
            abs_filename = os.path.abspath(filename)
            filename_normalized = os.path.normcase(os.path.normpath(abs_filename))
        except (OSError, ValueError):
            return False
        
        # Check if file is in stdlib or site-packages
        for stdlib_path in self.stdlib_paths:
            if filename_normalized.startswith(stdlib_path):
                return False
        
        # If we have a traced file set, only trace from that file/directory
        if self.traced_file:
            if filename_normalized == self.traced_file:
                return True
            if self.traced_file_dir and filename_normalized.startswith(self.traced_file_dir):
                return True
            return False
        
        # Fallback: trace anything not in stdlib
        return True

    def profile_callback(
        self, frame: Any, event: str, arg: Any
    ) -> None:
        """
        Callback for sys.setprofile.

        Args:
            frame: The current stack frame.
            event: Event type ('call', 'return', 'exception').
            arg: Additional event argument.
        """
        if not self._should_trace(frame):
            return

        if event == "call":
            frame_id = id(frame)
            self.start_times[frame_id] = time.perf_counter()
        elif event == "return":
            frame_id = id(frame)
            if frame_id in self.start_times:
                duration_sec = time.perf_counter() - self.start_times[frame_id]
                duration_ms = duration_sec * 1000
                del self.start_times[frame_id]

                func_name = frame.f_code.co_name
                self._print_trace(func_name, duration_ms)

    def _print_trace(self, func_name: str, duration_ms: float) -> None:
        """
        Print traced function execution.

        Args:
            func_name: Name of the function.
            duration_ms: Duration in milliseconds.
        """
        duration_display = f"{duration_ms:7.0f} ms"

        if duration_ms >= self.threshold_ms * 5:
            status = "🚨 VERY SLOW"
            color = "bold red"
        elif duration_ms >= self.threshold_ms:
            status = "⚠ SLOW"
            color = "yellow"
        else:
            status = ""
            color = "green"

        output = f"→ {func_name:30s} {duration_display}"
        if status:
            output += f"  {status}"

        console.print(output, style=color, highlight=False)

    def start(self) -> None:
        """Start profiling."""
        self.old_profile = sys.getprofile()
        sys.setprofile(self.profile_callback)

    def stop(self) -> None:
        """Stop profiling and restore previous profiler."""
        sys.setprofile(self.old_profile)
        self.start_times.clear()