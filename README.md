KAREL is a lightweight, GUI-based desktop automation tool designed to streamline operational reporting for businesses. Developed specifically to assist staff in monitoring and reporting system status, the application automates the process of capturing browser-based reports and delivering them directly via WhatsApp Web.

Key Features
Precision Window Capture: Uses DPI-aware coordinate mapping to capture only the relevant browser window, excluding the taskbar and background for a clean report.

Smart Scheduling: Features a mathematical synchronization algorithm that aligns reports with the top of the hour (e.g., 14:00, 14:20) rather than just relative intervals.

Real-time Countdown: A dynamic UI countdown timer informs the user exactly when the next report will be dispatched.

Fully Configurable: Users can customize the browser type (Edge/Chrome), WhatsApp chat name, report captions, and delivery intervals through a modern Dark Mode interface.

Error Resilient: Built with multi-threading to ensure the GUI remains responsive while automation tasks run in the background.

Tech Stack
Language: Python 3.12

GUI Framework: CustomTkinter (Modernized Tkinter UI)

Automation: PyAutoGUI (Keyboard & Mouse Control)

Image Processing: Pillow (PIL) for screenshots and icon management

Windows API: ctypes and win32clipboard for professional system integration.

How It Works
The system operates on a "Dual-Tab" logic where the browser's first tab holds the monitoring site and the second tab holds WhatsApp Web. KAREL refreshes the target site, captures the content, and automates the keyboard shortcuts to search for the target contact and paste the report with a custom message.
