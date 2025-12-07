import sys
from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {
    "packages": ["os", "sys", "base64", "random", "string", "cryptography", "PyQt6"],
    "excludes": [],
    "include_files": ["logo.ico", "logo.png"]
}

# GUI base
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Shortcuts
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "AeTxt",                  # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]AeTxt.exe",   # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     "TARGETDIR"               # WkDir
     ),
    ("StartMenuShortcut",      # Shortcut
     "ProgramMenuFolder",      # Directory_
     "AeTxt",                  # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]AeTxt.exe",   # Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     "TARGETDIR"               # WkDir
     )
]

# Registry for ShellNew (Right-click -> New -> AeTxt)
# Key: .aetxt\ShellNew (HKCR)
# Value: NullFile (String) = ""
registry_table = [
    ("ShellNew_Key", 0, r".aetxt\ShellNew", "NullFile", "", "TARGETDIR"),
]

# MSI Options
msi_data = {
    "Shortcut": shortcut_table,
    "Registry": registry_table
}

bdist_msi_options = {
    "data": msi_data,
    "upgrade_code": "{96a85bec-525d-48c7-9005-592f68903d6d}", # Unique GUID
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\AeTxt",
    
    # Register file association
    "extensions": [
        {
            "extension": "aetxt",
            "verb": "open",
            "argument": "%1",
            "context": "Open with AeTxt",
            "executable": "AeTxt.exe",
        }
    ]
}

setup(
    name="AeTxt",
    version="1.0",
    description="Aes Encrypted Text Editor",
    options={"build_exe": build_exe_options, "bdist_msi": bdist_msi_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="AeTxt.exe",
            icon="logo.ico",
            shortcut_name="AeTxt",
            shortcut_dir="DesktopFolder",
        )
    ],
)
