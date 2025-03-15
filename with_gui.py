import sys
import datetime
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QGridLayout, QHBoxLayout,
    QMessageBox, QVBoxLayout, QDesktopWidget
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
import isodate
import click


def parse_iso_duration(duration_str: str) -> datetime.timedelta:
    try:
        duration = isodate.parse_duration(duration_str)
        if not isinstance(duration, datetime.timedelta):
            raise ValueError("Invalid duration format.")
        return duration
    except Exception as e:
        raise ValueError(f"Error parsing duration: {e}")


def format_duration_for_schtasks(duration: datetime.timedelta) -> str:
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours:02}:{minutes:02}"


def get_existing_task_details(task_name: str):
    try:
        cmd = ["schtasks", "/query", "/tn", task_name, "/fo", "LIST", "/v"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Extract relevant details
        details = {}
        for line in result.stdout.splitlines():
            if line.startswith("Task Name:"):
                details["Task Name"] = line.split(":", 1)[1].strip()
            elif line.startswith("Task To Run:"):
                details["Command Path"] = line.split(":", 1)[1].strip()
            elif line.startswith("Repeat: Every"):
                details["Interval"] = line.split(" ", 2)[2].strip().split(" ")[0]  # Extract interval in minutes
            elif line.startswith("Duration:"):
                details["Duration"] = line.split(":", 1)[1].strip()

        if details:
            return details
        return None
    except subprocess.CalledProcessError:
        return None  # Task does not exist


def schedule_task(task_name: str, command_path: str, interval: int, duration_str: str):
    existing_task = get_existing_task_details(task_name)

    if existing_task:
        return (f"Task '{task_name}' already exists with the following details:\n"
                f"Task Name: {existing_task.get('Task Name', task_name)}\n"
                f"Command Path: {existing_task.get('Command Path', command_path)}\n"
                f"Interval (minutes): {existing_task.get('Interval', interval)}\n"
                f"Duration (ISO 8601 format): {existing_task.get('Duration', duration_str)}")

    try:
        duration_td = parse_iso_duration(duration_str)
        du_value = format_duration_for_schtasks(duration_td)
        start_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime("%H:%M")

        cmd = [
            "schtasks", "/create", "/tn", task_name,
            "/sc", "DAILY", "/tr", command_path,
            "/st", start_time, "/ri", str(interval), "/du", du_value, "/f"
        ]

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return f"Task '{task_name}' scheduled successfully.\n{result.stdout}"
    except subprocess.CalledProcessError as e:
        return f"Error scheduling task '{task_name}':\n{e.stderr}"
    except ValueError as e:
        return str(e)


@click.command()
@click.argument("task_name", type=str)
@click.argument("command_path", type=click.Path(exists=True))
@click.argument("interval", type=int)
@click.argument("duration", type=str)
def cli_schedule_task(task_name, command_path, interval, duration):
    """
    Command-line tool to schedule a task on Windows Task Scheduler.

    TASK_NAME: Name of the task to be scheduled.
    COMMAND_PATH: Path to the command or script to be executed.
    INTERVAL: Interval in minutes at which the task should repeat.
    DURATION: Duration in ISO 8601 format (e.g., PT3H for 3 hours).
    """
    message = schedule_task(task_name, command_path, interval, duration)
    click.echo(message)


class TaskSchedulerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Task Scheduler")
        self.setFixedSize(500, 300)  # Set fixed size to make the window non-resizable

        # Center the window on the screen
        self.center()

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        self.setPalette(palette)

        layout = QGridLayout()

        self.task_name_label = QLabel("Task Name:")
        self.task_name_input = QLineEdit()
        self.task_name_input.setPlaceholderText("Enter task name")

        self.command_label = QLabel("Command Path:")
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Browse or enter command path")
        self.browse_button = QPushButton("Browse")
        self.browse_button.setStyleSheet("background-color: #0078D7; color: white; font-weight: bold;")
        self.browse_button.clicked.connect(self.browse_file)

        self.interval_label = QLabel("Interval (minutes):")
        self.interval_input = QLineEdit()
        self.interval_input.setPlaceholderText("Enter interval in minutes")

        self.duration_label = QLabel("Duration (ISO 8601 format, e.g., PT3H):")
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("Enter duration in ISO 8601 format: PT3H")

        self.schedule_button = QPushButton("Schedule Task")
        self.schedule_button.setStyleSheet("background-color: #28A745; color: white; font-weight: bold;")
        self.schedule_button.clicked.connect(self.schedule)

        self.open_scheduler_button = QPushButton("Open Task Scheduler")
        self.open_scheduler_button.setStyleSheet("background-color: #6C757D; color: white; font-weight: bold;")
        self.open_scheduler_button.clicked.connect(self.open_task_scheduler)

        # Create a horizontal layout for the README and Requirements buttons
        button_layout = QHBoxLayout()

        # Set specific paths for README and Requirements files
        self.readme_button = QPushButton("README")
        self.readme_button.setStyleSheet("background-color: #17A2B8; color: white; font-weight: bold;")
        self.readme_button.clicked.connect(self.open_readme)

        self.requirements_button = QPushButton("Requirements")
        self.requirements_button.setStyleSheet("background-color: #FFC107; color: white; font-weight: bold;")
        self.requirements_button.clicked.connect(self.open_requirements)

        # Add buttons to the horizontal layout
        button_layout.addWidget(self.readme_button)
        button_layout.addWidget(self.requirements_button)

        # Add widgets to the grid layout
        layout.addWidget(self.task_name_label, 0, 0)
        layout.addWidget(self.task_name_input, 0, 1, 1, 2)
        layout.addWidget(self.command_label, 1, 0)
        layout.addWidget(self.command_input, 1, 1)
        layout.addWidget(self.browse_button, 1, 2)
        layout.addWidget(self.interval_label, 2, 0)
        layout.addWidget(self.interval_input, 2, 1, 1, 2)
        layout.addWidget(self.duration_label, 3, 0)
        layout.addWidget(self.duration_input, 3, 1, 1, 2)
        layout.addWidget(self.schedule_button, 4, 0, 1, 3)
        layout.addWidget(self.open_scheduler_button, 5, 0, 1, 3)

        # Add the button layout to the grid layout on the 6th row (same line)
        layout.addLayout(button_layout, 6, 0, 1, 3)

        # Add version label in the bottom right corner
        self.version_label = QLabel("Version 1.0.0")
        self.version_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(self.version_label, 7, 2, 1, 1)

        self.setLayout(layout)

    def center(self):
        # Get the geometry of the screen
        screen = QDesktopWidget().screenGeometry()
        # Get the geometry of the window
        size = self.geometry()
        # Move the window to the center of the screen
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Command File")
        if file_path:
            self.command_input.setText(file_path)

    def schedule(self):
        task_name = self.task_name_input.text()
        command_path = self.command_input.text()
        interval = self.interval_input.text()
        duration = self.duration_input.text()

        if not task_name or not command_path or not interval or not duration:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            interval = int(interval)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Interval must be a valid number.")
            return

        message = schedule_task(task_name, command_path, interval, duration)
        QMessageBox.information(self, "Task Scheduler", message)

    def open_task_scheduler(self):
        subprocess.run(["taskschd.msc"], shell=True)

    def open_readme(self):
        # Specify the path for the README file
        file_path = "README.MD"  # Change this to the correct path
        self.open_file(file_path)

    def open_requirements(self):
        # Specify the path for the Requirements file
        file_path = "requirements.txt"  # Change this to the correct path
        self.open_file(file_path)

    def open_file(self, file_path):
        try:
            # Try to open the file using the default text editor (Notepad on Windows)
            subprocess.run(["notepad", file_path], check=True)
        except FileNotFoundError:
            QMessageBox.warning(self, "File Not Found", f"The file '{file_path}' could not be found.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while opening the file: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_schedule_task()
    else:
        app = QApplication(sys.argv)
        window = TaskSchedulerApp()
        window.show()
        sys.exit(app.exec_())