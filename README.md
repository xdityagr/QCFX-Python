![Alt text](https://github.com/xdityagr/QCFX-Python/blob/main/banner_qcfxpython.png?raw=true "Banner Image")

---

# QCFx - Dynamic Background Blurring for PyQt Applications

QCFx is a Python library designed to add dynamic, real-time background blurring effects to PyQt5 applications. It provides various modes of operation, allowing for different levels of quality and performance to suit the needs of your application. The project leverages multi-threading to maintain smooth user experience even while performing complex image processing tasks.
(This library is still under work)
## Features

- **Multiple Blurring Modes**: QCFx supports different levels of blurring quality, allowing you to choose between ultra, medium, and low-quality blurring depending on your application's needs.
- **Window Movement Monitoring**: QCFx can detect when a window is being moved and update the background blur dynamically.
- **Desktop Wallpaper Monitoring**: Automatically updates the blur effect when the desktop wallpaper changes.
- **Other Windows State Monitoring**: Detects and responds to changes in the state of other windows (e.g., minimized or restored).
- **Settings Persistence**: QCFx settings are saved to a JSON file and can be reloaded or modified as needed.
- **Customizable UI**: The blurred background can be styled using custom CSS stylesheets for a more tailored look.

## Installation

To use QCFx in your project, ensure you have the following dependencies installed:

```bash
pip install QCFxPython
```

## Usage

Below is a basic example of how to integrate QCFx into your PyQt5 application.

### Example

```python
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import sys
from qcfx import QCFx_Blur, QCFx
from ui_testWindow import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.qcfx = QCFx()
        self.blur = QCFx_Blur(self, mode=self.qcfx.MODE_WINDOW_S)
        
        self.ui.body.setStyleSheet('background-color:rgba(0,0,0,0);')
        self.ui.overlay.setStyleSheet('background-color:rgba(0,0,0,0);')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
```

### Modes

QCFx provides several predefined modes for blurring:

- `MODE_DESKTOPONLY_U`: Ultra-quality blurring of the desktop background only.
- `MODE_DESKTOPONLY_S`: Medium-quality blurring of the desktop background only.
- `MODE_DESKTOPONLY_L`: Low-quality blurring of the desktop background only.
- `MODE_WINDOW_U`: Ultra-quality blurring that includes window monitoring.
- `MODE_WINDOW_S`: Medium-quality blurring that includes window monitoring.
- `MODE_WINDOW_L`: Low-quality blurring that includes window monitoring.

### Settings

QCFx allows you to configure various settings via a JSON file stored in the AppData directory. The default settings include:

```json
{
    "blurScalingFactor": 2,
    "recursiveFixedUpdate": false,
    "updateInterval": 500,
    "windowStateMonitoring": true,
    "windowMoveMonitoring": true,
    "otherWindowsStateMonitoring": true,
    "desktopMonitoring": true,
    "blurringFunction": 2,
    "blurRadius": 40,
    "blurLayerStylesheet": "background-color:none; border-radius:8px; padding:2px;",
    "showWindowTitlebar": true,
    "showWindowBorders": true
}
```

### Methods

#### `applySettings_fromMode(mode)`
Apply settings based on the selected mode (e.g., `MODE_WINDOW_S`).

#### `applySetting(key, value)`
Apply a specific setting dynamically during runtime.

#### `reloadSettings()`
Reload settings from the JSON file.

## Customization

QCFx provides several points of customization, including:

- **Stylesheet Customization**: Modify the appearance of the blur effect by changing the `blurLayerStylesheet` setting.
- **Blurring Function**: Choose between different blurring algorithms (Lanczos, Bilinear, Nearest Neighbor) by adjusting the `blurringFunction` setting.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you encounter any bugs or have suggestions for new features.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgements

- The project makes use of the PySide2 library for the PyQt5 framework.
- Image processing is handled by the Pillow library.

---
