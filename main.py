import sys
import os
import base64
import random
import string
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QFileDialog, 
                             QMessageBox, QInputDialog, QDialog, QVBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QHBoxLayout, QWidget, QToolBar, QFontDialog)
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QAction, QKeySequence, QWheelEvent, QPixmap
from PyQt6.QtCore import Qt, QSize
from crypto_handler import CryptoHandler, AESGCM

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Theme Definitions
THEMES = {
    "Dark": {
        "bg": "#1e1e1e",
        "fg": "#d4d4d4",
        "editor_bg": "#252526",
        "editor_fg": "#d4d4d4",
        "accent": "#007acc",
        "accent_hover": "#0062a3",
        "input_bg": "#3c3c3c",
        "border": "#333",
        "toolbar_bg": "#2d2d2d",
        "toolbar_border": "#333",
    },
    "Light": {
        "bg": "#f3f3f3",
        "fg": "#333333",
        "editor_bg": "#ffffff",
        "editor_fg": "#000000",
        "accent": "#0078d7",
        "accent_hover": "#005a9e",
        "input_bg": "#ffffff",
        "border": "#cccccc",
        "toolbar_bg": "#e0e0e0",
        "toolbar_border": "#c0c0c0",
    }
}

class StealthTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.default_font_size = 14
        self.stealth_mode = False
        self.real_content = ""

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn(1)
            else:
                self.zoomOut(1)
            event.accept()
        else:
            super().wheelEvent(event)

    def set_stealth_mode(self, enabled: bool):
        if self.stealth_mode == enabled:
            return
            
        cursor = self.textCursor()
        pos = cursor.position()
        
        self.stealth_mode = enabled
        if enabled:
            # Entering stealth mode: Backup real text, obfuscate visual text
            self.real_content = self.toPlainText()
            self.update_visual_text()
        else:
            # Exiting stealth mode: Restore real text
            self.setPlainText(self.real_content)
            
        # Restore cursor
        new_cursor = self.textCursor()
        new_cursor.setPosition(pos)
        self.setTextCursor(new_cursor)

    def update_visual_text(self):
        # Re-generates visual text based on real_content for stealth mode
        if not self.stealth_mode:
            return
            
        visual_chars = []
        for char in self.real_content:
            if char == '\n':
                visual_chars.append('\n')
            elif char.isspace():
                visual_chars.append(char) # Keep tabs/spaces
            elif char.isupper():
                visual_chars.append(random.choice(string.ascii_uppercase))
            elif char.islower():
                visual_chars.append(random.choice(string.ascii_lowercase))
            else:
                visual_chars.append(random.choice(string.ascii_letters))
        
        blocked_signals = self.blockSignals(True)
        self.setPlainText("".join(visual_chars))
        self.blockSignals(blocked_signals)

    def keyPressEvent(self, event):
        if not self.stealth_mode:
            super().keyPressEvent(event)
            return

        # Handle simple typing in stealth mode
        key = event.text()
        
        # Allow navigation and control keys to pass through normally
        if not key or event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier):
            super().keyPressEvent(event)
            return
            
        cursor = self.textCursor()
        
        # Handle selection deletion/replacement
        if cursor.hasSelection():
            # If user types something while text is selected, we must remove that range from real_content
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
            self.real_content = self.real_content[:start] + self.real_content[end:]
            # Let default handler delete the selection visually
            cursor.removeSelectedText()

        pos = cursor.position()
        
        if event.key() == Qt.Key.Key_Backspace:
            if pos > 0:
                self.real_content = self.real_content[:pos-1] + self.real_content[pos:]
                super().keyPressEvent(event)
        elif event.key() == Qt.Key.Key_Delete:
            if pos < len(self.real_content):
                self.real_content = self.real_content[:pos] + self.real_content[pos+1:]
                super().keyPressEvent(event)
        elif key: # Printable char
             # Insert into real content
             self.real_content = self.real_content[:pos] + key + self.real_content[pos:]
             
             # Insert random char visually
             if key == '\n':
                 visual_char = '\n'
             elif key.isspace():
                 visual_char = key
             elif key.isupper():
                 visual_char = random.choice(string.ascii_uppercase)
             elif key.islower():
                 visual_char = random.choice(string.ascii_lowercase)
             else:
                 visual_char = random.choice(string.ascii_letters)
            
             cursor.insertText(visual_char)
        else:
            super().keyPressEvent(event)

    def get_actual_text(self):
        if self.stealth_mode:
            return self.real_content
        return self.toPlainText()

    def set_actual_text(self, text):
        self.real_content = text
        if self.stealth_mode:
             self.update_visual_text()
        else:
             self.setPlainText(text)


STYLESHEET_TEMPLATE = """
QMainWindow {{
    background-color: {bg};
}}

QInternalMdiSubWindow {{
    background-color: {bg}; 
}}

QTextEdit {{
    background-color: {editor_bg};
    color: {editor_fg};
    border: none;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    padding: 10px;
    selection-background-color: {accent};
}}

QMenuBar {{
    background-color: {bg};
    color: {fg};
    border-bottom: 1px solid {border};
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 12px;
}}

QMenuBar::item:selected {{
    background-color: {border};
}}

QMenu {{
    background-color: {bg};
    color: {fg};
    border: 1px solid {border};
}}

QMenu::item {{
    padding: 6px 24px;
}}

QMenu::item:selected {{
    background-color: {accent};
}}

QDialog {{
    background-color: {bg};
    color: {fg};
}}

QLabel {{
    color: {fg};
    font-size: 14px;
}}

QLineEdit {{
    background-color: {input_bg};
    color: {fg};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 8px;
    selection-background-color: {accent};
}}

QLineEdit:focus {{
    border: 1px solid {accent};
}}

QPushButton {{
    background-color: {accent};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {accent_hover};
}}

QPushButton#cancel_btn {{
    background-color: {input_bg};
    border: 1px solid {border};
    color: {fg};
}}

QPushButton#cancel_btn:hover {{
    background-color: {border};
}}

QStatusBar {{
    background-color: {accent};
    color: white;
}}

QToolBar {{
    background-color: {toolbar_bg};
    border-bottom: 1px solid {toolbar_border};
    spacing: 10px;
    padding: 5px;
}}

QToolButton {{
    background-color: transparent;
    color: {fg};
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 5px 10px;
    font-size: 14px;
}}

QToolButton:hover {{
    background-color: {border};
    border: 1px solid {border};
}}
"""


class PasswordDialog(QDialog):
    def __init__(self, parent=None, title="Enter Password", is_save=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 200)
        self.password = None
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.label = QLabel("Password:" if not is_save else "Create/Enter Password:")
        layout.addWidget(self.label)
        
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        self.input.setPlaceholderText("Enter your password here...")
        layout.addWidget(self.input)
        
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept_password)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def accept_password(self):
        self.password = self.input.text()
        if self.password:
            self.accept()
        else:
            self.input.setFocus()

class ModernNotepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.crypto = CryptoHandler()
        self.current_file = None
        self.current_password = None
        self.is_hidden = False
        self.current_theme = "Dark"
        self.markdown_mode = False
        self.last_alt_time = 0
        
        self.init_ui()

        # Handle file open from command line (e.g. "Open with...")
        if len(sys.argv) > 1:
            file_to_open = sys.argv[1]
            if os.path.isfile(file_to_open):
                self.open_file(file_to_open)
        
    def init_ui(self):
        self.setWindowTitle("AeTxt - Aes Encrypted Text Editor")
        self.resize(1000, 700)
        
        # Set Icon
        # Set Icon
        icon_path = resource_path("logo.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        self.update_title()
        
        # Central Widget
        self.resize(1000, 700)
        
        # Central Widget
        self.editor = StealthTextEdit()
        self.setCentralWidget(self.editor)
        
        # Toolbar
        self.setCentralWidget(self.editor)
        
        # Toolbar
        self.create_toolbar()

        # Menu Bar
        self.create_menus()
        
        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Ready")
        
        # Apply Styles
        self.apply_theme("Dark")
        
    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        theme = THEMES[theme_name]
        self.setStyleSheet(STYLESHEET_TEMPLATE.format(**theme))
        self.editor.setStyleSheet(f"background-color: {theme['editor_bg']}; color: {theme['editor_fg']}; border: none; padding: 10px; selection-background-color: {theme['accent']};")
        self.editor.setFont(QFont("Segoe UI", 14))
        
    def create_menus(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View Menu
        view_menu = menubar.addMenu("View")
        
        # Theme Submenu
        theme_menu = view_menu.addMenu("Theme")
        dark_action = QAction("Dark", self)
        dark_action.triggered.connect(lambda: self.apply_theme("Dark"))
        theme_menu.addAction(dark_action)
        
        light_action = QAction("Light", self)
        light_action.triggered.connect(lambda: self.apply_theme("Light"))
        theme_menu.addAction(light_action)

        view_menu.addSeparator()
        
        self.markdown_action = QAction("Toggle Markdown View", self)
        self.markdown_action.setCheckable(True)
        self.markdown_action.setShortcut("Ctrl+M")
        self.markdown_action.triggered.connect(self.toggle_markdown)
        view_menu.addAction(self.markdown_action)
        
        # Security Menu
        security_menu = menubar.addMenu("Security")
        change_pass_action = QAction("Change Session Password", self)
        change_pass_action.triggered.connect(self.change_session_password)
        security_menu.addAction(change_pass_action)

    def toggle_markdown(self):
        self.markdown_mode = not self.markdown_mode
        if self.markdown_mode:
            text = self.editor.toPlainText()
            self.editor.setMarkdown(text)
            self.editor.setReadOnly(True)
            self.status.showMessage("Markdown view enabled (Ready-Only)")
        else:
            text = self.editor.toMarkdown()
            self.editor.setPlainText(text)
            self.editor.setReadOnly(False)
            self.status.showMessage("Editor mode")

    def create_toolbar(self):
        toolbar = QToolBar("Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.hide_action = QAction("Hide", self)
        self.hide_action.triggered.connect(self.toggle_visibility)
        # Font ayarlaması opsiyoneldir, stil dosyasından kontrol ediliyor fakat burada da belirtebiliriz
        toolbar.addAction(self.hide_action)

        self.stealth_action = QAction("Stealth Mode", self)
        self.stealth_action.setCheckable(True)
        self.stealth_action.triggered.connect(self.toggle_stealth_mode)
        toolbar.addAction(self.stealth_action)

    def toggle_stealth_mode(self):
        is_stealth = self.stealth_action.isChecked()
        self.editor.set_stealth_mode(is_stealth)
        if is_stealth:
            self.status.showMessage("Stealth Mode ON - Typing is obfuscated")
        else:
            self.status.showMessage("Stealth Mode OFF")

    def toggle_visibility(self):
        if self.is_hidden:
            # Şifre Çözme İşlemi
            dialog = PasswordDialog(self, "Enter Password Again", is_save=False)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                password = dialog.password
                try:
                    b64_content = self.editor.toPlainText().strip() # Encrypted blob is always visible as is
                    encrypted_data = base64.b64decode(b64_content)
                    
                    decrypted_text = self.crypto.decrypt(encrypted_data, password)
                    self.editor.set_actual_text(decrypted_text)
                    self.editor.setReadOnly(False)
                    self.is_hidden = False
                    self.hide_action.setText("Hide")
                    self.current_password = password
                    self.status.showMessage("Content decrypted.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", "Incorrect password or corrupted content!")
        else:
            # Gizleme İşlemi
            password = self.current_password
            if not password:
                dialog = PasswordDialog(self, "Set Password to Hide", is_save=True)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    password = dialog.password
                    self.current_password = password
                else:
                    return

                    return

            try:
                content = self.editor.get_actual_text()
                encrypted_bytes = self.crypto.encrypt(content, password)
                b64_str = base64.b64encode(encrypted_bytes).decode('utf-8')
                
                # When hiding, we force stealth mode OFF internally for the view because we are showing the cipher blob
                if self.editor.stealth_mode:
                    self.stealth_action.setChecked(False)
                    self.editor.set_stealth_mode(False) # Reset stealth so we see the blob

                self.editor.setPlainText(b64_str)
                self.editor.setReadOnly(True)
                self.is_hidden = True
                self.hide_action.setText("Decrypt")
                self.status.showMessage("Content encrypted and hidden.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Encryption error: {e}")

    def new_file(self):
        self.current_file = None
        self.current_password = None
        self.editor.clear()
        self.editor.setReadOnly(False)
        self.is_hidden = False
        self.hide_action.setText("Hide")
        self.status.showMessage("New file")
        self.update_title()

    def update_title(self):
        title = "AeTxt - Aes Encrypted Text Editor"
        if self.current_file:
            filename = os.path.basename(self.current_file)
            title = f"{filename} - AeTxt"
        self.setWindowTitle(title)
        
    def open_file(self, file_name=None):
        if not file_name:
            file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "AeTxt Files (*.aetxt);;All Files (*)")
        
        if file_name:
            try:
                with open(file_name, 'rb') as f:
                    data = f.read()
                
                if not data:
                    self.editor.setPlainText("")
                    self.current_file = file_name
                    self._reset_state_after_load()
                    return

                dialog = PasswordDialog(self, "File Password", is_save=False)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    password = dialog.password
                    try:
                        decrypted_text = self.crypto.decrypt(data, password)
                        self.editor.set_actual_text(decrypted_text)
                        self.current_file = file_name
                        self.current_password = password
                        self._reset_state_after_load()
                        self.status.showMessage(f"Opened: {file_name}")
                        self.update_title()
                    except Exception as e:
                        QMessageBox.critical(self, "Error", "Decryption failed! Incorrect password or corrupted file.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"File could not be read: {str(e)}")

    def _reset_state_after_load(self):
        self.editor.setReadOnly(False)
        self.is_hidden = False
        self.hide_action.setText("Hide")

    def save_file(self):
        if self.current_file and self.current_password:
            self._write_file(self.current_file, self.current_password)
        else:
            self.save_as_file()

    def save_as_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save As", "", "AeTxt Files (*.aetxt)")
        
        if file_name:
            if not file_name.endswith('.aetxt'):
                file_name += '.aetxt'
                
            dialog = PasswordDialog(self, "Set Password", is_save=True)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                password = dialog.password
                self._write_file(file_name, password)
                self.current_file = file_name
                self.current_password = password
    
    def _write_file(self, filename, password):
        content = self.editor.get_actual_text()
        try:
            encrypted_data = self.crypto.encrypt(content, password)
            with open(filename, 'wb') as f:
                f.write(encrypted_data)
            self.status.showMessage(f"Saved: {filename}")
            self.update_title()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Save error: {str(e)}")

    def change_session_password(self):
         dialog = PasswordDialog(self, "New Session Password", is_save=True)
         if dialog.exec() == QDialog.DialogCode.Accepted:
             self.current_password = dialog.password
             self.status.showMessage("Session password updated. (You must Save to apply changes to the file)")

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Alt:
            # Ignore auto-repeats (holding down key)
            if event.isAutoRepeat():
                super().keyReleaseEvent(event)
                return
            
            current_time = time.time()
            if current_time - self.last_alt_time < 0.4:  # 400ms threshold
                # PANIC LOGIC: Ensure content is hidden/obfuscated.
                # 1. If we have a password and are NOT hidden, hide it.
                if self.current_password and not self.is_hidden:
                    self.toggle_visibility() # Will encrypt and hide
                # 2. If we do NOT have a password, force Stealth Mode (if not already on)
                elif not self.current_password and not self.editor.stealth_mode:
                    self.stealth_action.setChecked(True)
                    self.editor.set_stealth_mode(True)
                    self.status.showMessage("Panic Mode: Stealth Activated")
                # 3. If already hidden or in stealth, DO NOTHING (Safety: don't reveal)
            
            self.last_alt_time = current_time
        
        super().keyReleaseEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = ModernNotepad()
    window.show()
    
    sys.exit(app.exec())
