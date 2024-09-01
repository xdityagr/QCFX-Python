
""" 
QC FX Engine - An FX Engine for Qt5/Qt6 Applications for dynamic blur effects like of windows, for python
Developed by Aditya Gaur
Github : @xdityagr 
Email  : adityagaur.home@gmail.com 

"""

# Imports 

import os, json

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import pyautogui
from PIL import Image, ImageFilter, ImageQt

import threading
import win32gui
import time

import ctypes

from json import JSONDecodeError
from pathlib import Path
import shutil
import imagehash


# If you import pyqt5, an error comes ; that QPIxmap only supports QImage not ImageQt.
# QC FX Settings & Modes Handling class
class QCFx:
    def __init__(self):
        # QC FX MODES FOR BLURRING 
        self.MODE_DESKTOPONLY_U = (0, 2) # ULTRA QUALITY, SLOW
        self.MODE_DESKTOPONLY_S = (0, 1) # MEDIUM QUALITY, STABLE (Use this for best experience)
        self.MODE_DESKTOPONLY_L = (0, 0) # LOW QUALITY, FAST
        
        self.MODE_WINDOW_U = (1, 0) # ULTRA QUALITY, SLOW
        self.MODE_WINDOW_S = (1, 1) # MEDIUM QUALITY, STABLE
        self.MODE_WINDOW_L = (1, 2) # LOW QUALITY, FAST
        
        # Default Settings :
        self.SETTINGS_DEFAULT = {
            'blurScalingFactor':2, # Scaling factor of blurred background (Basically, Quality of blurred image) ; Less means higher quality
            'recursiveFixedUpdate':False, # Recursive Fixed update; If you do not want dynamic experience
            'updateInterval':None,  # If recursiveFixedUpdate is enabled, default value=500ms
            'windowStateMonitoring':True, # Monitor the window and change blur effects dynamically, (includes maximizing, minimizing, resizing);
            'windowMoveMonitoring':True,  # Very Important for dynamic experience, Should remain True.
            'otherWindowsStateMonitoring':True, # Monitor othr windows for changes, to remain more dynamic;
            'desktopMonitoring':True, # Monitoring only on desktop (detects desktop wallpaper changes), If you are developing an app which sticks to desktop only, perfect mode for you! 
            'blurringFunction': 2,  # Basically, Quality factor; Lower means worse quality (0,1,2);
            'blurRadius':40, # Blur radius; Magnitude of blur 
            'blurLayerStylesheet' : "background-color:none; border-radius:8px; padding:2px;", # Stylesheet of Blur Layer
            "showWindowTitlebar":True ,
            "showWindowBorders":True 
        }

        appdata_path = os.path.join(os.getenv('APPDATA'), '/QCFxData/')
        self.SETTINGS_PATH = os.path.join(appdata_path, 'settings.json')
        
        if not os.path.exists(appdata_path): 
            os.mkdir(appdata_path)
            with open(self.SETTINGS_PATH, 'w') as sFile: 
                try:
                    temp = {"Settings": self.SETTINGS_DEFAULT}
                    json.dump(temp, sFile, indent=4)
                except JSONDecodeError as e:
                    print(e)
                    
        if not os.path.exists(self.SETTINGS_PATH): 
            with open(self.SETTINGS_PATH, 'w') as sFile: 
                try:
                    temp = {"Settings": self.SETTINGS_DEFAULT}
                    json.dump(temp, sFile, indent=4)
                except JSONDecodeError as e:
                    print(e)

        self.loadSettings()

    def loadSettings(self):
        with open(self.SETTINGS_PATH, 'r') as file:
            try:
                self.sessionSettings = json.load(file)
                self.sessionSettings = self.sessionSettings['Settings']
            except JSONDecodeError as e:
                self.sessionSettings = None
                print('error: ')
                print(e)

        if self.sessionSettings != None:
            return self.sessionSettings
        
    def regenerateSettings(self):
        os.remove(self.SETTINGS_PATH)
        with open(self.SETTINGS_PATH, 'w') as sFile: 
            try:
                temp = {"Settings": self.SETTINGS_DEFAULT}
                json.dump(temp, sFile, indent=4)
            except JSONDecodeError as e:
                print(e)

    def applySettings_fromMode(self, mode):
        qualityFactor = mode[1]
        if mode[0] == 0:
            newSettings = self.sessionSettings.copy()
            newSettings['otherWindowsStateMonitoring'] = False
            newSettings['windowStateMonitoring'] = False
            newSettings['otherWindowsStateMonitoring'] = False
            newSettings['desktopMonitoring'] = True
            newSettings['blurringFunction'] = qualityFactor
        elif mode[0] == 1:
            newSettings = self.sessionSettings.copy()
            newSettings['otherWindowsStateMonitoring'] = True
            newSettings['windowStateMonitoring'] = True
            newSettings['otherWindowsStateMonitoring'] = True
            newSettings['desktopMonitoring'] = True
            newSettings['blurringFunction'] = qualityFactor

        return self.overwriteSettings(newSettings)

    def applySetting(self, key, value):
        newSetting = self.sessionSettings.copy()
        newSetting[key] = value
        return self.overwriteSettings(newSetting)

    def overwriteSettings(self, newSettings):
        with open(self.SETTINGS_PATH, 'w') as ovr:
            try:
                temp = {"Settings": newSettings}
                json.dump(temp, ovr, indent=4)
            except JSONDecodeError as e:
                print('error: ')
                print(e)

        return self.loadSettings()

class QCFx_Blur:
    def __init__(self, parent, overlay=None, mode=None):
        
        self.parent = parent
        self.qcfx = QCFx()
        self.mode = mode if mode!=None else self.qcfx.MODE_DESKTOPONLY_S
        self.settings = self.qcfx.applySettings_fromMode(mode)
        
        
        if not self.settings['showWindowTitlebar']:
            self.parent.setWindowFlags(Qt.FramelessWindowHint)
        if not self.settings['showWindowBorders']:
            self.parent.setAttribute(Qt.WA_TranslucentBackground)
        
        
        if overlay==None:
            self.blurLayer = QLabel(self.parent)
            self.blurLayer.setObjectName(u"blurLayer")
            self.blurLayer.setGeometry(self.parent.rect())
        else:
            self.blurLayer = overlay

        self.blurLayer.setStyleSheet(self.settings['blurLayerStylesheet'])

        radius = 10 
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.blurLayer.width(), self.blurLayer.height()), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.blurLayer.setMask(mask)

        # Set the stylesheet for the label
        # # self.blurLayer.setStyleSheet("""
        #     border-radius: 20px;
        #     background-color: transparent;
        # """)
        self.blurLayer.lower()

    
        self.initializeParent()
        
    def initializeParent(self):
        self.recursiveFixedUpdateMode = self.settings['recursiveFixedUpdate']

        if self.recursiveFixedUpdateMode:
            self.updateInterval= self.settings['updateInterval'] if self.settings['updateInterval'] else 500
            print('rCF')                
            self.RFUpdate= QTimer(self.parent)
            self.RFUpdate.timeout.connect(self.FixedUpdate)
            self.RFUpdate.start(self.updateInterval)  


        self.blurScalingFactor = self.settings['blurScalingFactor']
        self.monitorWindowState = self.settings['windowStateMonitoring']
        self.monitorWindowMovement = self.settings['windowMoveMonitoring']
        self.monitorDesktop = self.settings['desktopMonitoring']
        self.monitorOtherWindowsState = self.settings['otherWindowsStateMonitoring']
        self.blurRadius = self.settings['blurRadius']
        self.blurringFunction = self.settings['blurringFunction']

        self.cached_image = None  
        self.image_qimage = None  # QImage for parent
        self.processing_thread = None  # Background thread
        self.current_hwnd = None # Window control

        if self.monitorWindowState:
            self.monitor_thread = threading.Thread(target=self.monitor_window_state)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
        
        if self.monitorWindowMovement:
            self.parent_is_moving = False 
            self.last_position = QPoint()  
            self.parent.moveEvent = self.updateAsynchronous_
        
            self.movement_timer = QTimer(self.parent)
            self.movement_timer.timeout.connect(self.isParentStoppedMoving)
            self.movement_timer.start(50)  # Check every 50 ms (adjust as needed)

            self.stopped_timer = QTimer(self.parent)
            self.stopped_timer.setSingleShot(True)
            self.stopped_timer.timeout.connect(self.OnParentStoppedMoving)


        if self.monitorOtherWindowsState:    
            
            self.check_windows_thread = threading.Thread(target=self.check_all_windows)
            self.check_windows_thread.daemon = True
            self.check_windows_thread.start()

        if self.monitorDesktop:
            self.wallpaper_thread = threading.Thread(target=self.wallpaperChangeCheck)
            self.wallpaper_thread.daemon = True
            self.wallpaper_thread.start()


        self.init_backgroundCapture()


    def Reload(self):
        self.settings = self.qcfx.loadSettings()
        self.recursiveFixedUpdateMode = self.settings['recursiveFixedUpdate']
        
        if self.recursiveFixedUpdateMode:
            self.updateInterval= self.settings['updateInterval'] if self.settings['updateInterval'] else 500
            print('rCF')                
            self.RFUpdate= QTimer(self.parent)
            self.RFUpdate.timeout.connect(self.FixedUpdate)
            self.RFUpdate.start(self.updateInterval)  


        self.blurScalingFactor = self.settings['blurScalingFactor']
        self.monitorWindowState = self.settings['windowStateMonitoring']
        self.monitorWindowMovement = self.settings['windowMoveMonitoring']
        self.monitorDesktop = self.settings['desktopMonitoring']
        self.monitorOtherWindowsState = self.settings['otherWindowsStateMonitoring']
        self.blurRadius = self.settings['blurRadius']
        self.blurringFunction = self.settings['blurringFunction']

        self.cached_image = None  
        self.image_qimage = None  # QImage for parent
        self.processing_thread = None  # Background thread
        self.current_hwnd = None # Window control

        if self.monitorWindowState:
            self.monitor_thread = threading.Thread(target=self.monitor_window_state)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
        
        if self.monitorWindowMovement:
            self.parent_is_moving = False 
            self.last_position = QPoint()  
            self.parent.moveEvent = self.updateAsynchronous_
        
            self.movement_timer = QTimer(self.parent)
            self.movement_timer.timeout.connect(self.isParentStoppedMoving)
            self.movement_timer.start(50)  # Check every 50 ms (adjust as needed)

            self.stopped_timer = QTimer(self.parent)
            self.stopped_timer.setSingleShot(True)
            self.stopped_timer.timeout.connect(self.OnParentStoppedMoving)

        if self.monitorDesktop:
            
            self.wallpaper_path = None
            self.desktopWallpaperChange = QTimer(self.parent)
            self.desktopWallpaperChange.timeout.connect(self.wallpaperChangeCheck)
            self.desktopWallpaperChange.start(2000)
        print(self.monitorDesktop)
        if self.monitorOtherWindowsState:    
            
            self.check_windows_thread = threading.Thread(target=self.check_all_windows)
            self.check_windows_thread.daemon = True
            self.check_windows_thread.start()

        self.init_backgroundCapture()
        
        

    def updateAsynchronous_(self, event):
        if self.processing_thread is None or not self.processing_thread.is_alive():
            self.processing_thread = threading.Thread(target=self.generateParentBackground)
            self.processing_thread.start()
    
    def FixedUpdate(self):
        self.init_backgroundCapture()
        print('called fixed update')
    
        
    def generateParentBackground(self):
        if self.cached_image is None:
            return

        x = self.parent.pos().x()
        y = self.parent.pos().y()
        width = self.parent.width()
        height = self.parent.height()
        
        scaled_x = int(x / self.blurScalingFactor)
        scaled_y = int(y / self.blurScalingFactor)
        scaled_width = int(width / self.blurScalingFactor)
        scaled_height = int(height / self.blurScalingFactor)

        scaled_x = max(scaled_x, 0)
        scaled_y = max(scaled_y, 0)
        scaled_width = min(scaled_width, self.cached_image.width - scaled_x)
        scaled_height = min(scaled_height, self.cached_image.height - scaled_y)

        # Crop and blur the image from the smaller image
        cropped_image = self.cached_image.crop((scaled_x, scaled_y, scaled_x + scaled_width, scaled_y + scaled_height))

        # Resize the cropped image to match the window size
        if self.blurringFunction == 2:
            cropped_image = cropped_image.resize((width, height), Image.LANCZOS)
        elif self.blurringFunction == 1:
            cropped_image = cropped_image.resize((width, height), Image.BILINEAR)
        else:
            cropped_image = cropped_image.resize((width, height), Image.NEAREST)

        # Convert PIL image to QImage

        self.cropped_image_qimage = ImageQt.ImageQt(cropped_image)
        # self.cropped_image_qimage = cropped_image

        # Update the UI from the main thread
        self.updateParentBackground()

    @Slot()
    def updateParentBackground(self):
        # pixmap = self.__convertPiltoPixmap(self.cropped_image_qimage)
        
        pixmap = QPixmap.fromImage(self.cropped_image_qimage)
        scaled_pixmap = pixmap.scaled(self.blurLayer.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.blurLayer.setPixmap(scaled_pixmap)

    def _fade_step(self):
        opacity = 1.0 - (self.fade_step / self.fade_steps)
        self.opacity_effect.setOpacity(opacity)

        if self.fade_step == self.fade_steps // 2:
            # Update the pixmap halfway through the fade out
            self.blurLayer.setPixmap(self.new_pixmap)

        if self.fade_step < self.fade_steps:
            self.fade_step += 1
            QTimer.singleShot(self.fade_step_duration, self._fade_step)
        else:
            # Ensure full opacity at the end
            self.opacity_effect.setOpacity(1.0)

            
    # WORKES FOR WINDOWS ONLY
    def init_backgroundCapture(self):
        screen_width, screen_height = pyautogui.size() 
        if self.monitorDesktop and self.mode[0]==0:

            SPI_GETDESKWALLPAPER = 0x0073
            wallpaper_path_bin = ctypes.create_string_buffer(260)
            ctypes.windll.user32.SystemParametersInfoA(SPI_GETDESKWALLPAPER, 260, wallpaper_path_bin, 0)
            self.wallpaperPath =  wallpaper_path_bin.value.decode()

            bgC = Image.open(self.wallpaperPath)

            if self.blurringFunction == 2:
                bgC = bgC.resize((screen_width, screen_height), Image.LANCZOS)
            elif self.blurringFunction == 1:
                bgC = bgC.resize((screen_width, screen_height), Image.BILINEAR)
            else:
                bgC = bgC.resize((screen_width, screen_height), Image.NEAREST)

        else:
            screen_rect = (0, 0, *pyautogui.size())
            bgC = pyautogui.screenshot(region=screen_rect)
        
        if bgC.mode not in ("RGB", "L"):
            bgC = bgC.convert("RGB")

        bgC = bgC.filter(ImageFilter.GaussianBlur(radius=self.blurRadius))

        if self.blurringFunction == 2:
            self.cached_image = bgC.resize((screen_width // self.blurScalingFactor, screen_height // self.blurScalingFactor), Image.LANCZOS)
        elif self.blurringFunction == 1:
            self.cached_image = bgC.resize((screen_width // self.blurScalingFactor, screen_height // self.blurScalingFactor), Image.BILINEAR)
        else:
            self.cached_image = bgC.resize((screen_width // self.blurScalingFactor, screen_height // self.blurScalingFactor), Image.NEAREST)


    def wallpaperChangeCheck(self):
        old_hash = None
        while True:
            try:
                SPI_GETDESKWALLPAPER = 0x0073
                wallpaper_path_bin = ctypes.create_string_buffer(260)
                ctypes.windll.user32.SystemParametersInfoA(SPI_GETDESKWALLPAPER, 260, wallpaper_path_bin, 0)
                self.wallpaper_path = wallpaper_path_bin.value.decode()
            
                try:
                    img = Image.open(self.wallpaper_path)
                    img_hash = imagehash.average_hash(img)
                    
                    if old_hash is None:
                        old_hash = img_hash

                    elif old_hash != img_hash:
                        old_hash = img_hash

                        self.init_backgroundCapture()
                        self.updateAsynchronous_(None)

                except PermissionError as e:
                    print(f"Permission error accessing wallpaper: {e}")
                    
                    time.sleep(2)
                    
            except Exception as e:
                print(f"Error in wallpaperChangeCheck: {e}")

            time.sleep(2)  # Check every 5 seconds for changes Check every 5 seconds for changes


    def _get_desktop_wallpaper(self):
        SPI_GETDESKWALLPAPER = 0x0073
        buffer = ctypes.create_unicode_buffer(280)
        ctypes.windll.user32.SystemParametersInfoW(SPI_GETDESKWALLPAPER, 280, buffer, 0)
        return buffer.value

    def monitor_window_state(self):
        self.current_hwnd = win32gui.GetForegroundWindow()
        while True:
            time.sleep(1)  # Check every second
            new_hwnd = win32gui.GetForegroundWindow()
            if new_hwnd != self.current_hwnd:
                self.init_backgroundCapture()
                self.current_hwnd = new_hwnd
    
    
    def isParentStoppedMoving(self):
        current_position = self.parent.pos()
        if current_position != self.last_position:
            if not self.parent_is_moving:
                self.parent_is_moving = True
            self.last_position = current_position
            self.stopped_timer.start(200)  # Check if it stops moving after 200 ms
            

    def OnParentStoppedMoving(self):
        if self.parent_is_moving:
            self.parent_is_moving = False
            self.init_backgroundCapture()
            
                
            

    def check_all_windows(self):
        """Periodically check the state of all windows and refresh the background if needed."""
        previous_states = {}
        while True:
            time.sleep(1)  # Check every second
            all_windows = self.get_all_windows()
            current_states = {}

            for hwnd in all_windows:
                try:
                    if win32gui.IsWindow(hwnd):
                        current_states[hwnd] = win32gui.IsIconic(hwnd)
                except Exception as e:
                    print(f"Error checking window {hwnd}: {e}")

            # Check for minimized windows
            for hwnd, is_minimized in current_states.items():
                was_minimized = previous_states.get(hwnd, False)
                if is_minimized and not was_minimized:
                    
                    self.init_backgroundCapture()
    
                elif not is_minimized and was_minimized:
    
                    self.init_backgroundCapture()
                
            previous_states = current_states

    def get_all_windows(self):
        """Get a list of all window handles."""
        windows = []
        win32gui.EnumWindows(lambda hwnd, _: windows.append(hwnd), None)
        return windows
    

    def __convertPiltoPixmap(self, im):
        if im.mode == "RGB":
            r, g, b = im.split()
            im = Image.merge("RGB", (b, g, r))
        elif  im.mode == "RGBA":
            r, g, b, a = im.split()
            im = Image.merge("RGBA", (b, g, r, a))
        elif im.mode == "L":
            im = im.convert("RGBA")
        # Bild in RGBA konvertieren, falls nicht bereits passiert
        im2 = im.convert("RGBA")
        data = im2.tobytes("raw", "RGBA")
        qim = QImage(data, im.size[0], im.size[1], QImage.Format_ARGB32)
        pixmap = QPixmap.fromImage(qim)
        return pixmap
