# task-scheduler-application 📅🕒✅⚙️
This is a Python-based Task Scheduler application that allows users to schedule tasks on Windows using the Windows Task Scheduler (`schtasks`). The application provides both a Command-Line Interface (CLI) and a Graphical User Interface (GUI) for scheduling tasks.

The GUI is built using `PyQt5`, and the CLI is implemented using the `click` library. The application supports scheduling tasks with a specified interval and duration, and it also allows users to browse for executable files or scripts to schedule.

![task-scheduler-application-GUI](https://github.com/Pr0ofoFw0rK/task_scheduler_application/blob/main/photo.png?raw=true)

This project does amazing things...
---

Features
- Schedule Tasks: Schedule tasks with a custom name, command path, interval (in minutes), and duration (in ISO 8601 format, e.g., `PT3H` for 3 hours).
- Check Existing Tasks: If a task with the same name already exists, the application will display its details.
- Open Task Scheduler: Directly open the Windows Task Scheduler from the application.
- Browse for Commands: Browse and select executable files or scripts to schedule.
- Readme and Requirements: Buttons to open the `README.MD` and `requirements.txt` files directly from the application.

---

Requirements
- PyQt5
- Click
- isodate

To install the required dependencies, run:
pip install -r requirements.txt

---

Usage

GUI Mode
1. Run the script without any arguments:
python with_gui.py

2. Fill in the fields:
- Task Name: Name of the task.
- Command Path: Path to the executable or script.
- Interval (minutes): Interval at which the task should repeat.
- Duration (ISO 8601 format): Duration of the task (e.g., `PT3H` for 3 hours).
3. Click Schedule Task to schedule the task.

CLI Mode
Run the script with the following arguments:
python with_gui.py "TASK_NAME" "COMMAND_PATH" "INTERVAL" "DURATION"

Ex:  python with_gui.py "MyTask" "C:\Users\user\PycharmProjects\user\my_script.bat" 15 "PT3H"

- TASK_NAME: Name of the task.
- COMMAND_PATH: Path to the executable or script.
- INTERVAL: Interval in minutes.
- DURATION: Duration in ISO 8601 format (e.g., `PT3H` for 3 hours).

Example:
python with_gui.py "MyTask" "C:\Users\user\PycharmProjects\user\my_script.bat" 15 "PT3H"

---

Notes
- The application is designed for Windows only, as it uses the `schtasks` command.
- Ensure that the command path provided is valid and accessible.
- The duration must be in ISO 8601 format (e.g., `PT3H` for 3 hours, `PT30M` for 30 minutes).

---

Version
- Version 1.0.0

---

License
This project is open-source and available under the MIT License.

---

Author
Pr0ofoFw0rK

---

For any issues or suggestions, please contact the author.
