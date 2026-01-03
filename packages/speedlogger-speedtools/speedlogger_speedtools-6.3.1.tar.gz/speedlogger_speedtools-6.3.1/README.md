# SpeedLogger

Fast, colorful Python logger with gradients, inputs, visualizations, and full customization.

---

## Features

- Colorful logs with custom symbols and prefixes  
- Rate-limited logging  
- Input prompts: standard, password, confirm, choice  
- Visualizations: progress bars, loading, spinner, countdown  
- Data display: tables, lists, key-value pairs  
- Centered or normal terminal output  

---

## Installation

pip install speedlogger-speedtools

---

## Quick Example

from speedlogger import info, success, inp, progress_bar

info("SYSTEM", "Starting application")
username = inp("Enter your username")
success("AUTH", f"User {username} logged in")

for i in range(101):
    progress_bar(i, 100)

---

## License

MIT License © 2024 SpeedLogger Team
