"""
Progress Display Module

Provides user-friendly progress bar and status messages for the AutoML pipeline.
"""

import sys
import os
import time
from typing import Optional, List
from dataclasses import dataclass

# Enable UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass  # Python < 3.7


@dataclass
class Step:
    """Represents a pipeline step."""
    name: str
    description: str


class ProgressBar:
    """
    User-friendly progress bar for CLI display.

    Usage:
        progress = ProgressBar(total_steps=9)
        progress.start("Loading data...")
        # ... do work ...
        progress.advance("Profiling data...")
        # ... do work ...
        progress.complete()
    """

    STEPS = [
        Step("Loading", "Loading data"),
        Step("Profiling", "Profiling data"),
        Step("Inference", "Inferring task type"),
        Step("Splitting", "Splitting train/test"),
        Step("Preprocessing", "Preprocessing data"),
        Step("Balancing", "Balancing classes"),
        Step("Training", "Training models"),
        Step("Evaluating", "Evaluating model"),
        Step("Exporting", "Exporting results"),
    ]

    def __init__(
        self,
        total_steps: int = 9,
        bar_width: int = 30,
        show_percentage: bool = True,
        show_step_count: bool = True,
        use_ascii: bool = True  # Use ASCII for Windows compatibility
    ):
        """
        Initialize the progress bar.

        Args:
            total_steps: Total number of steps in the pipeline
            bar_width: Width of the progress bar in characters
            show_percentage: Whether to show percentage complete
            show_step_count: Whether to show step count (e.g., 3/9)
            use_ascii: Use ASCII characters for compatibility (default: True)
        """
        self.total_steps = total_steps
        self.bar_width = bar_width
        self.show_percentage = show_percentage
        self.show_step_count = show_step_count
        self.use_ascii = use_ascii
        self.current_step = 0
        self.current_message = ""
        self.start_time = None
        self._last_line_length = 0

        # Characters for progress bar
        if use_ascii:
            self.fill_char = '#'
            self.empty_char = '-'
        else:
            self.fill_char = '█'
            self.empty_char = '░'

    def _clear_line(self):
        """Clear the current line."""
        sys.stdout.write('\r' + ' ' * self._last_line_length + '\r')
        sys.stdout.flush()

    def _render_bar(self) -> str:
        """Render the progress bar string."""
        # Calculate progress
        progress = self.current_step / self.total_steps
        filled = int(self.bar_width * progress)
        empty = self.bar_width - filled

        # Build bar
        bar = self.fill_char * filled + self.empty_char * empty

        # Build status line
        parts = []

        # Step count
        if self.show_step_count:
            parts.append(f"[{self.current_step}/{self.total_steps}]")

        # Progress bar
        parts.append(f"[{bar}]")

        # Percentage
        if self.show_percentage:
            parts.append(f"{int(progress * 100):3d}%")

        # Current step message
        if self.current_message:
            parts.append(f"| {self.current_message}")

        return " ".join(parts)

    def _display(self):
        """Display the current progress."""
        line = self._render_bar()
        self._clear_line()
        sys.stdout.write(line)
        sys.stdout.flush()
        self._last_line_length = len(line)

    def start(self, message: str = "Starting..."):
        """Start the progress bar."""
        self.start_time = time.time()
        self.current_step = 0
        self.current_message = message

        # Print header
        print("=" * 60)
        print("  TabuLaML - Tabular Machine Learning")
        print("=" * 60)
        print()

        self._display()

    def update(self, step: int, message: str):
        """
        Update progress to a specific step.

        Args:
            step: Current step number (1-based)
            message: Status message to display
        """
        self.current_step = step
        self.current_message = message
        self._display()

    def advance(self, message: str = ""):
        """
        Advance to the next step.

        Args:
            message: Status message to display
        """
        self.current_step += 1
        if message:
            self.current_message = message
        self._display()

    def set_message(self, message: str):
        """Update the current message without advancing."""
        self.current_message = message
        self._display()

    def complete(self, message: str = "Complete!"):
        """Mark the progress as complete."""
        self.current_step = self.total_steps
        self.current_message = message
        self._display()

        # Move to new line
        print()

        # Show completion time
        if self.start_time:
            elapsed = time.time() - self.start_time
            print()
            print(f"  Completed in {elapsed:.1f} seconds")

        print()
        print("=" * 60)

    def step_loading(self):
        """Update for loading step."""
        self.update(1, "Loading data...")

    def step_profiling(self):
        """Update for profiling step."""
        self.update(2, "Profiling data...")

    def step_inference(self):
        """Update for task inference step."""
        self.update(3, "Inferring task type...")

    def step_splitting(self):
        """Update for train/test split step."""
        self.update(4, "Splitting train/test...")

    def step_preprocessing(self):
        """Update for preprocessing step."""
        self.update(5, "Preprocessing features...")

    def step_balancing(self):
        """Update for class balancing step."""
        self.update(6, "Balancing classes...")

    def step_training(self, model_name: str = ""):
        """Update for training step."""
        msg = f"Training {model_name}..." if model_name else "Training models..."
        self.update(7, msg)

    def step_evaluating(self):
        """Update for evaluation step."""
        self.update(8, "Evaluating model...")

    def step_exporting(self):
        """Update for export step."""
        self.update(9, "Exporting results...")


class QuietProgress:
    """Silent progress tracker that doesn't display anything."""

    def start(self, message: str = ""): pass
    def update(self, step: int, message: str): pass
    def advance(self, message: str = ""): pass
    def set_message(self, message: str): pass
    def complete(self, message: str = ""): pass
    def step_loading(self): pass
    def step_profiling(self): pass
    def step_inference(self): pass
    def step_splitting(self): pass
    def step_preprocessing(self): pass
    def step_balancing(self): pass
    def step_training(self, model_name: str = ""): pass
    def step_evaluating(self): pass
    def step_exporting(self): pass
