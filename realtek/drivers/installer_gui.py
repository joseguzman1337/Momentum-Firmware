"""RTL88xxAU macOS Driver GUI Installer."""

import sys
import os
import subprocess
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QTextEdit, QProgressBar, QMessageBox, QGroupBox
)
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon

# Global constants for GUI configuration
WINDOW_TITLE = "RTL88xxAU macOS Driver Installer v1.0.0"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
STATUS_READY = "Ready to install RTL88xxAU USB WiFi driver"
STATUS_INSTALLING = "Installing driver... Please wait"
STATUS_SUCCESS = "Installation completed successfully!"
STATUS_ERROR = "Installation failed. Check details below."

class InstallWorker(QObject):
    """Worker thread for installation process."""
    
    finished = pyqtSignal(bool, str)
    progress = pyqtSignal(str)
    
    def run_installation(self):
        """Execute the installation process."""
        try:
            self.progress.emit("Checking system requirements...")
            
            # Check if running on macOS
            if sys.platform != "darwin":
                self.finished.emit(False, "This installer only works on macOS")
                return
            
            # Get absolute paths to avoid permission issues
            current_dir = os.path.abspath(os.getcwd())
            install_script = os.path.join(current_dir, "scripts", "install.sh")
            
            if not os.path.exists(install_script):
                self.finished.emit(False, f"Installation script not found: {install_script}")
                return
            
            self.progress.emit("Starting installation with admin privileges...")
            
            # Create AppleScript command with absolute paths
            applescript_cmd = f'''
            tell application "Terminal"
                activate
                do script "cd '{current_dir}' && sudo bash '{install_script}'"
            end tell
            '''
            
            # Run installation script with Terminal for better permission handling
            process = subprocess.Popen(
                ['osascript', '-e', applescript_cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.progress.emit("Installation completed successfully!")
                self.finished.emit(True, stdout)
            else:
                self.progress.emit("Installation failed")
                self.finished.emit(False, stderr or "Unknown error occurred")
                
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

class RTL88xxAUInstaller(QMainWindow):
    """Main installer GUI application."""
    
    def __init__(self):
        """Initialize the installer GUI."""
        super().__init__()
        self.setup_ui()
        self.setup_worker()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle(WINDOW_TITLE)
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Header section
        self.create_header(main_layout)
        
        # Device info section
        self.create_device_info(main_layout)
        
        # Status section
        self.create_status_section(main_layout)
        
        # Control buttons
        self.create_control_buttons(main_layout)
        
        # Output section
        self.create_output_section(main_layout)
    
    def create_header(self, parent_layout):
        """Create header section with title and description."""
        header_group = QGroupBox("RTL88xxAU USB WiFi Driver")
        header_layout = QVBoxLayout(header_group)
        
        title_label = QLabel("Realtek RTL8812AU/8821AU/8814AU Driver Installer")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        desc_label = QLabel(
            "This installer will install the RTL88xxAU USB WiFi driver\n"
            "for macOS including support for Alfa AWUS1900 devices."
        )
        desc_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(desc_label)
        parent_layout.addWidget(header_group)
    
    def create_device_info(self, parent_layout):
        """Create device information section."""
        device_group = QGroupBox("Supported Devices")
        device_layout = QVBoxLayout(device_group)
        
        supported_devices = [
            "• Realtek RTL8812AU (Dual-band 802.11ac USB 3.0)",
            "• Realtek RTL8821AU (Single-band 802.11ac USB)",
            "• Realtek RTL8814AU (Dual-band 802.11ac USB 3.0 with 4x4 MIMO)",
            "• Alfa AWUS1900 (RTL8814AU-based)",
            "• Alfa AWUS036ACS (RTL8812AU-based)"
        ]
        
        device_text = "\n".join(supported_devices)
        device_label = QLabel(device_text)
        device_label.setWordWrap(True)
        
        device_layout.addWidget(device_label)
        parent_layout.addWidget(device_group)
    
    def create_status_section(self, parent_layout):
        """Create status display section."""
        status_group = QGroupBox("Installation Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel(STATUS_READY)
        self.status_label.setStyleSheet("QLabel { color: blue; font-weight: bold; }")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        parent_layout.addWidget(status_group)
    
    def create_control_buttons(self, parent_layout):
        """Create control buttons section."""
        button_layout = QHBoxLayout()
        
        self.detect_button = QPushButton("Detect Devices")
        self.detect_button.clicked.connect(self.detect_devices)
        
        self.install_button = QPushButton("Install Driver (Simple)")
        self.install_button.clicked.connect(self.install_driver_simple)
        self.install_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; "
            "font-weight: bold; padding: 8px; }"
        )
        
        self.advanced_button = QPushButton("Advanced Install")
        self.advanced_button.clicked.connect(self.install_driver)
        self.advanced_button.setStyleSheet(
            "QPushButton { background-color: #FF9800; color: white; "
            "font-weight: bold; padding: 8px; }"
        )
        
        self.terminal_button = QPushButton("Open Terminal")
        self.terminal_button.clicked.connect(self.open_terminal)
        self.terminal_button.setStyleSheet(
            "QPushButton { background-color: #2196F3; color: white; "
            "font-weight: bold; padding: 8px; }"
        )
        
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.detect_button)
        button_layout.addWidget(self.install_button)
        button_layout.addWidget(self.advanced_button)
        button_layout.addWidget(self.terminal_button)
        button_layout.addWidget(self.quit_button)
        parent_layout.addLayout(button_layout)
    
    def create_output_section(self, parent_layout):
        """Create output log section."""
        output_group = QGroupBox("Installation Log")
        output_layout = QVBoxLayout(output_group)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(150)
        self.output_text.append("Ready to begin installation...")
        
        output_layout.addWidget(self.output_text)
        parent_layout.addWidget(output_group)
    
    def setup_worker(self):
        """Setup worker thread for installation."""
        self.worker = InstallWorker()
        self.worker.finished.connect(self.installation_finished)
        self.worker.progress.connect(self.update_progress)
    
    def detect_devices(self):
        """Detect connected RTL devices."""
        self.output_text.append("\nDetecting RTL88xxAU devices...")
        try:
            result = subprocess.run(
                ['system_profiler', 'SPUSBDataType'],
                capture_output=True, text=True, timeout=10
            )
            
            if "realtek" in result.stdout.lower() or "rtl" in result.stdout.lower():
                self.output_text.append("✓ RTL device(s) detected!")
                self.status_label.setText("RTL device detected - ready to install")
                self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            else:
                self.output_text.append("⚠ No RTL devices detected")
                self.status_label.setText("No RTL devices found - check connection")
                self.status_label.setStyleSheet("QLabel { color: orange; font-weight: bold; }")
                
        except Exception as e:
            self.output_text.append(f"Error detecting devices: {e}")
    
    def install_driver_simple(self):
        """Install driver using simplified installer."""
        reply = QMessageBox.question(
            self, 'Install Driver (Simple)',
            'This will install the RTL88xxAU driver using a simplified method that works better with modern macOS security.\n\n'
            'This method will open Terminal. Continue?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            current_dir = os.path.abspath(os.getcwd())
            simple_script = os.path.join(current_dir, "scripts", "simple_install.sh")
            
            # Create a terminal command for simple installation
            terminal_cmd = f"cd '{current_dir}' && sudo bash '{simple_script}'"
            
            # Open Terminal with the simplified installer
            applescript = f'''
            tell application "Terminal"
                activate
                do script "{terminal_cmd}"
            end tell
            '''
            
            subprocess.run(['osascript', '-e', applescript])
            
            self.output_text.append("\nOpened Terminal with simplified installer.")
            self.output_text.append("This installer works better with modern macOS security.")
            self.output_text.append("Please enter your password in Terminal when prompted.")
            
            # Show information dialog
            QMessageBox.information(
                self, 'Simplified Installer Started',
                'Terminal has opened with the simplified installer.\n\n'
                'This installer automatically handles modern macOS security restrictions.\n\n'
                'Please enter your administrator password in Terminal when prompted.'
            )
            
        except Exception as e:
            self.output_text.append(f"Error opening simplified installer: {e}")
            QMessageBox.warning(
                self, 'Error',
                f'Failed to open simplified installer: {e}'
            )
    
    def open_terminal(self):
        """Open Terminal with the installation command ready."""
        try:
            current_dir = os.path.abspath(os.getcwd())
            install_script = os.path.join(current_dir, "scripts", "install.sh")
            
            # Create a terminal command that navigates to directory and runs installer
            terminal_cmd = f"cd '{current_dir}' && sudo bash '{install_script}'"
            
            # Open Terminal with the command
            applescript = f'''
            tell application "Terminal"
                activate
                do script "{terminal_cmd}"
            end tell
            '''
            
            subprocess.run(['osascript', '-e', applescript])
            
            self.output_text.append("\nOpened Terminal with full installation command.")
            self.output_text.append("Please enter your password in Terminal when prompted.")
            
            # Show information dialog
            QMessageBox.information(
                self, 'Terminal Opened',
                'Terminal has been opened with the full installation command.\n\n'
                'Please enter your administrator password when prompted '
                'in the Terminal window to proceed with installation.'
            )
            
        except Exception as e:
            self.output_text.append(f"Error opening Terminal: {e}")
            QMessageBox.warning(
                self, 'Error',
                f'Failed to open Terminal: {e}'
            )
    
    def install_driver(self):
        """Start the advanced driver installation process."""
        reply = QMessageBox.question(
            self, 'Advanced Install',
            'This will run the full installation process with all system checks.\n\n'
            'This method provides more detailed feedback but may require SIP to be disabled.\n\n'
            'Continue with advanced installation?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        self.install_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText(STATUS_INSTALLING)
        self.status_label.setStyleSheet("QLabel { color: blue; font-weight: bold; }")
        self.output_text.clear()
        self.output_text.append("Opening Terminal for installation...")
        self.output_text.append("Please follow the prompts in Terminal window.")
        
        # Run installation in separate thread
        thread = threading.Thread(target=self.worker.run_installation)
        thread.daemon = True
        thread.start()
    
    def update_progress(self, message):
        """Update progress display."""
        self.output_text.append(message)
    
    def installation_finished(self, success, message):
        """Handle installation completion."""
        self.install_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText(STATUS_SUCCESS)
            self.status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            self.output_text.append("\n✓ Installation completed successfully!")
            self.output_text.append("Please restart your Mac or reconnect your device.")
            
            QMessageBox.information(
                self, 'Success',
                'Driver installed successfully!\n\n'
                'Your RTL88xxAU device should now be available in Network Preferences.\n'
                'You may need to restart your Mac or reconnect the USB device.'
            )
        else:
            self.status_label.setText(STATUS_ERROR)
            self.status_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            self.output_text.append(f"\n✗ Installation failed: {message}")
            
            QMessageBox.warning(
                self, 'Installation Failed',
                f'Installation failed:\n\n{message}\n\n'
                'Please check the log for details.'
            )

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("RTL88xxAU Driver Installer")
    app.setApplicationVersion("1.0.0")
    
    # Check if running on macOS
    if sys.platform != "darwin":
        QMessageBox.critical(
            None, 'Platform Error',
            'This installer only works on macOS systems.'
        )
        sys.exit(1)
    
    # Check if script directory exists
    if not os.path.exists("scripts/install.sh"):
        QMessageBox.critical(
            None, 'File Error',
            'Installation script not found.\n\n'
            'Please run this GUI from the RTL88xxAU driver directory.'
        )
        sys.exit(1)
    
    installer = RTL88xxAUInstaller()
    installer.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

