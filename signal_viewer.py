from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton, QFileDialog,QShortcut,QColorDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont,QIcon,QKeySequence
from PyQt5.uic import loadUiType
from reportlab.pdfgen import canvas
import os
import sys
from pyqtgraph.exporters import ImageExporter
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from PIL import Image
import math
import pyqtgraph as pg
import numpy as np
import time
from PyQt5.QtWidgets import QMenu, QAction
from pyqtgraph.Qt import QtCore
from PyQt5.QtWidgets import QComboBox
import pyqtgraph as pg

# Set the PyQtGraph theme to light mode
pg.setConfigOption('background', 'w')  
pg.setConfigOption('foreground', 'k')  
pg.setConfigOption('antialias', True)  


# Define the list to store the names of signals
loaded_signal_filenames = []
loaded_signal_filenames_2 = []

# Load the UI file and get the main form class
UI_FILE = "Signal_Viewer.ui"
Ui_MainWindow, QMainWindowBase = loadUiType(os.path.join(os.path.dirname(__file__), UI_FILE))

class MainApp(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        self.signal_displayed_2 = False
        self.signal_playing_2 = False  
        self.signal_displayed = False
        self.signal_playing = False  
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.color="b"
        self.color_2 ="r"
        self.folder_path_1_1 = "C:\\Users\\Struggler\\Desktop\\DSP Task 1\\task1_gamica&hesham\\photo1"
        # self.folder_path_1_1 = "C:\\Users\\elnag\\qt\\task1_rename+zoomvertical\\photo1"
        self.photo_index_1 = 0
        self.index_1 = 0
        self.rightBoundaryUp = 0
        self.leftBoundaryUp = 0
        self.rightBoundaryDown = 0
        self.leftBoundaryDown = 0
        self.zoom_factor_x_up = 100
        self.zoom_factor_y_up = 100
        self.zoom_factor_x_down = 100
        self.zoom_factor_y_down = 100
        self.link = False

        #PlotWidget for displaying signal
        self.plotWidget = pg.PlotWidget()
        self.horizontalLayout_10.addWidget(self.plotWidget)  
        self.plotWidget.showGrid(x=True,y=True)

        self.plotWidget.plotItem.setMouseEnabled(x=False, y=False)
        
        #PlotWidget for the second signal
        self.plotWidget2 = pg.PlotWidget()
        self.verticalLayout_3.addWidget(self.plotWidget2) 
        self.plotWidget2.showGrid(x=True,y=True)
        
        self.plotWidget2.plotItem.setMouseEnabled(x=False, y=False)

        # self.folder_path_1_2 = "C:\\Users\\elnag\\qt\\task1_rename+zoomvertical\\photo2"
        self.folder_path_1_2 = "C:\\Users\\Struggler\\Desktop\\DSP Task 1\\task1_gamica&hesham\\photo2"
        self.photo_index_2 = 0
        self.index_2 = 0
        
        #panSlider
        self.panSliderUp.valueChanged.connect(lambda value: (self.panUp(value)))
        self.panUpSliderV.valueChanged.connect(lambda value: (self.pan_vertically_Up(value)))
        self.panSliderUp.setValue(self.panSliderUp.maximum())

        #panSlider
        self.panSliderDown.valueChanged.connect(lambda value: (self.panDown(value)))
        self.panDownSliderV.valueChanged.connect(lambda value: (self.pan_vertically_down(value)))
        self.panSliderDown.setValue(self.panSliderDown.maximum())
        
          


        #Handle each button to it's function in plot2
        self.pushButton_11.clicked.connect(self.select_signal_2)
        self.pushButton_17.clicked.connect(self.zoom_in_2)
        self.pushButton_18.clicked.connect(self.zoom_out_2)
        self.pushButton_19.clicked.connect(self.reset_view_2)
        self.pushButton_20.clicked.connect(self.clear_2)
        self.pushButton_13.clicked.connect(self.play_pause_2)
        self.pushButton_9.clicked.connect(self.move_down)
        self.pushButton_14.clicked.connect(self.hide_2)
        self.pushButton_15.clicked.connect(self.snapshot_2)
        self.btnOkUp.clicked.connect(self.fbtnOkUp)

        #Handle each button to it's function in plot1
        self.pushButton_2.clicked.connect(self.select_signal)
        self.pushButton_3.clicked.connect(self.play_pause)
        self.pushButton_7.clicked.connect(self.clear)
        self.pushButton_4.clicked.connect(self.zoom_in)
        self.pushButton_5.clicked.connect(self.zoom_out)
        self.pushButton_6.clicked.connect(self.reset_view)
        self.pushButton_16.clicked.connect(self.show_hide_frame)
        self.pushButton_21.clicked.connect(self.move_up)
        self.pushButton_8.clicked.connect(self.hide)
        self.pushButton_10.clicked.connect(self.snapshot)
        self.pdfBtn.clicked.connect(self.pdf_generate)
        self.btnOkDown.clicked.connect(self.fbtnOkDown)



        
        # List to store loaded and ploted signals for plotWidgets
        self.loaded_signals_2 = []
        self.plot_items_2 = []

        self.loaded_signals = []
        self.plot_items = []

        # Zoom factor for plotWidgets 
        self.zoom_factor_2 = 1.0
        self.zoom_factor = 1.0

        # Create a QTimer to update the signal for plotWidgets
        self.signal_timer_2 = QTimer(self)
        self.signal_timer_2.timeout.connect(self.update_signal_2)
        self.signal_timer_2.start(100) 
        
        self.signal_timer = QTimer(self)
        self.signal_timer.timeout.connect(self.update_signal)
        self.signal_timer.start(100)
        

        # Create a layout for widget
        self.layout_widget = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(self.layout_widget)
        self.setCentralWidget(widget)

        
        
        # Create a layout for widget_2
        widget_2 = QWidget()
        self.setCentralWidget(widget_2)

        # Create a widget to hold the verticalLayout_2
        widget = QWidget()
        widget.setLayout(self.verticalLayout_2)

        # Set widget as the central widget to fill the entire window
        self.setCentralWidget(widget)

        # Create a QTimer to update the CSV data plot for plotWidget2
        self.csv_data_timer_2 = QTimer(self)
        self.csv_data_timer_2.timeout.connect(self.update_signal_2)
        
        self.pdf = canvas.Canvas('output.pdf')

        # Handle speed slider
        self.horizontalSlider.setValue(self.horizontalSlider.minimum())
        self.horizontalSlider_2.setValue(self.horizontalSlider.minimum())
        
        self.horizontalSlider.valueChanged.connect(lambda value :(self.adjust_speed(value)))
        self.horizontalSlider_2.valueChanged.connect(lambda value :(self.adjust_speed_2(value)))

        #Handle change color
        self.color_up.clicked.connect(self.open_color_palette)
        self.color_down.clicked.connect(self.open_color_palette_2)


        # Set app icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "logo.png") 
        app_icon = QIcon(icon_path)
        self.setWindowIcon(app_icon)

        # Set app name
        self.setWindowTitle("Multi-Channel Signal Viewer")

        self.setStyleSheet('''
            QLabel {
                font-size: 14px;
                color: black; /* Text color for labels set to black */
            }
            QPushButton {
                background-color: white; /* Button background color set to white */
                color: black; /* Button text color set to black */
                border: 1px solid #CCCCFF; /* Border color */
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #CCCCFF; /* Hover background color - light cyan */
                color: black; /* Change text color on hover to black */
            }
        ''')


        # Apply margins to the verticalLayout_2
        self.verticalLayout_2.setContentsMargins(20, 20, 20, 20)  

        # Initialize CSV data
        self.signal = None
        self.signal_phase = 0.0
        self.rows_to_display = 2000  
        self.current_row = 0  
        self.current_row_2 = 0  
        self.transition_duration = 1000  # Duration of transition between rows in milliseconds
        self.transition_timer = QTimer(self)
        self.transition_timer.timeout.connect(self.increment_current_row)


    def panUp(self, value):
        if self.signal_playing_2:
            return
        limit_x = self.rightBoundaryUp
        if(self.link):
            current_selected_x = self.panSliderDown.value() / 100 *  limit_x
        else :
            current_selected_x = self.panSliderUp.value() / 100 *  limit_x

        # Set the x-axis range using setXRange
        self.plotWidget2.plotItem.getViewBox().setXRange(max(0, current_selected_x - 400 + min(150, 100/self.zoom_factor_2)), max(400,current_selected_x - min(150, 100/self.zoom_factor_2)))
        # Configure auto-visible behavior for the X-axis
        self.plotWidget2.plotItem.getViewBox().setAutoVisible(x=True, y=True)
        
        print(self.zoom_factor_2)
        print(self.zoom_factor_x_up)
        view_range = self.plotWidget2.plotItem.getViewBox().viewRange()
        x_range, y_range = view_range
        x_min, x_max = x_range
        y_min, y_max = y_range
        print(f"X Range: {x_min} to {x_max}")
        print(f"Y Range: {y_min} to {y_max}")
        
        
    def pan_vertically_Up(self, value):
        if self.signal_playing_2:
            return
        limit_y = 1.5  # Set the vertical limits to -1 and 1
        if(self.link):
            current_selected_y = self.panDownSliderV.value() / 100 *  limit_y
        else :
            current_selected_y = self.panUpSliderV.value() / 100 *  limit_y
        # Set the y-axis range using setYRange, ensuring it stays within -1 to 1
        self.plotWidget2.plotItem.getViewBox().setYRange(max(-1.5, current_selected_y - 0.5), min(1.5, current_selected_y + 0.5))
       
        self.zoom_in_whenpanning()
        # Disable auto-ranging on the Y-axis
        # self.plotWidget2.plotItem.getViewBox().enableAutoRange(pg.ViewBox.YAxis, enable=False)


    def zoom_in_whenpanning(self):
        # if self.push
        self.zoom_in()

    def pan_vertically_down(self, value):
        if self.signal_playing_2:
            return
        limit_y = 1.5  # Set the vertical limits to -1 and 1
        current_selected_y = self.panDownSliderV.value() / 100 * limit_y
        # Set the y-axis range using setYRange, ensuring it stays within -1 to 1
        self.plotWidget.plotItem.getViewBox().setYRange(max(-1.5, current_selected_y - 0.5), min(1.5, current_selected_y + 0.5))
        # Disable auto-ranging on the Y-axis
        # self.plotWidget2.plotItem.getViewBox().enableAutoRange(pg.ViewBox.YAxis, enable=False)


    def panDown(self, value):
        if self.signal_playing:
            return
        limit_x = self.rightBoundaryDown
        current_selected_x = self.panSliderDown.value() / 100 *  limit_x
        # Set the x-axis range using setXRange
        self.plotWidget.plotItem.getViewBox().setXRange(max(0, current_selected_x - 400), max(400,current_selected_x))
        # Disable auto-ranging on the X-axis
        #  self.plotWidget.plotItem.getViewBox().enableAutoRange(pg.ViewBox.XAxis, enable=False)

        
    # Handle select signal for the two plots
    def select_signal(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ExistingFiles

        file_dialog = QFileDialog(self)
        file_dialog.setOptions(options)
        file_dialog.setWindowTitle("Open CSV File")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilters(["CSV Files (*.csv)", "All Files (*)"])
        if self.signal_playing:
            self.play_pause()

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                self.load_signal(file_path)
            self.play_pause()

    def select_signal_2(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        options |= QFileDialog.ExistingFiles

        file_dialog = QFileDialog(self)
        file_dialog.setOptions(options)
        file_dialog.setWindowTitle("Open CSV File for plotWidget2")
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilters(["CSV Files (*.csv)", "All Files (*)"])

        if self.signal_playing_2:
            self.play_pause_2()

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            for file_path in selected_files:
                self.load_signal_2(file_path)

            self.play_pause_2()

    #Handle loading and setting signals in the two graphs
    def load_signal(self, file_path):
        try:
            data = np.genfromtxt(file_path, delimiter=',')  
            self.loaded_signals.append(data)
            self.signal_displayed = True
            self.current_row = 0  
            loaded_signal_filenames_2.append(os.path.basename(file_path))
            self.combo_box_bottom()
        except Exception as e:
            print(f"Error loading CSV data: {str(e)}")
            self.loaded_signals.append(None)
            self.signal_displayed = False

    def load_signal_2(self, file_path):
        try:
            data = np.genfromtxt(file_path, delimiter=',')
            self.loaded_signals_2.append(data)
            self.signal_displayed_2 = True
            self.current_row_2 = 0  
            loaded_signal_filenames.append(os.path.basename(file_path))
            self.combo_box()
        except Exception as e:
            print(f"Error loading CSV data for plotWidget2: {str(e)}")
            self.loaded_signals_2.append(None)
            self.signal_displayed_2 = False

    #Handle plot1 buttons
    def play_pause(self):
        if not self.signal_displayed:
            return
        
        if self.signal_playing:
            self.signal_timer.stop()
            self.pushButton_3.setText("Play")
        else:
            self.signal_timer.start(100)  
            self.pushButton_3.setText("Pause")

        self.signal_playing = not self.signal_playing

    #Handle plot2 buttons 
    def play_pause_2(self):
        if not self.signal_displayed_2:
            return

        if self.signal_playing_2:
            self.signal_timer_2.stop()
            self.pushButton_13.setText("Play")
        else:
            self.signal_timer_2.start(100)  
            self.pushButton_13.setText("Pause")
        
        self.signal_playing_2 = not self.signal_playing_2

    def clear(self):
        self.loaded_signals = []  
        self.signal_displayed = False
        self.plotWidget.clear()  
        self.pushButton_3.setText("Play")
        self.signal_playing = False
        self.cB_loadcsvbottom.clear()
        
    def zoom_in(self):
        if self.zoom_factor > 0.2:
            self.zoom_factor -= 0.19
        

    def zoom_out(self):
        if self.zoom_factor < 4.0:
            self.zoom_factor += 0.2


    def reset_view(self):
        self.zoom_factor = 1.0

    def combo_box(self):
        self.cB_loadcsvtop.clear()  
        self.cB_loadcsvtop.addItems(loaded_signal_filenames)   

    def hide(self):
        selected_index = self.cB_loadcsvbottom.currentIndex()

        if selected_index >= 0 and selected_index < len(self.loaded_signals):
            data_to_hide = self.loaded_signals.pop(selected_index)
            filename = loaded_signal_filenames_2.pop(selected_index)

            self.combo_box()
            self.combo_box_bottom()
            self.loaded_signals.pop(data_to_hide)
            self.update_signal()
            self.combo_box_bottom()


    def clear_2(self):
        self.loaded_signals_2 = []  
        self.signal_displayed_2 = False
        self.plotWidget2.clear()  
        self.pushButton_13.setText("Play")
        self.signal_playing_2 = False
        self.cB_loadcsvtop.clear()

    def zoom_in_2(self):
        if self.zoom_factor_2 > 0.20:
            self.zoom_factor_2 -= 0.19
            
    def zoom_out_2(self):
        if self.zoom_factor_2 < 4.0:
            self.zoom_factor_2 += 0.2

    def reset_view_2(self):
        self.zoom_factor_2 = 1.0

    def combo_box_bottom(self):
        self.cB_loadcsvbottom.clear()  
        self.cB_loadcsvbottom.addItems(loaded_signal_filenames_2)    
    
    def hide_2(self):
        selected_index = self.cB_loadcsvtop.currentIndex()

        if selected_index >= 0 and selected_index < len(self.loaded_signals_2):
            data_to_hide = self.loaded_signals_2.pop(selected_index)
            filename = loaded_signal_filenames.pop(selected_index)
            self.combo_box()
            self.combo_box_bottom()
            self.loaded_signals_2.pop(int(data_to_hide))
            self.update_signal()
            self.combo_box()

    #Handle link button 
    def show_hide_frame(self):
        if self.frame.isVisible():
            self.pushButton_16.setText("Unlink")  
            self.link = True
            self.frame.hide()
            self.framePan.hide()
            self.horizontalSlider.hide()
            self.panSliderUp.hide()
            self.panUpSliderV.hide()
            self.label_3.hide()
            self.pushButton_13.clicked.connect(self.play_pause)
            self.pushButton_11.clicked.connect(self.select_signal)
            self.pushButton_17.clicked.connect(self.zoom_in)
            self.pushButton_18.clicked.connect(self.zoom_out)
            self.pushButton_19.clicked.connect(self.reset_view)
            self.pushButton_20.clicked.connect(self.clear)
            self.horizontalSlider_2.valueChanged.connect(lambda value: (self.adjust_speed(value)))
            self.panSliderDown.valueChanged.connect(lambda value: (self.panUp(value)))
            self.panDownSliderV.valueChanged.connect(lambda value: (self.pan_vertically_Up(value)))
            
        else:
            self.pushButton_16.setText("Link")
            self.link = False  
            self.frame.show()
            self.framePan.show()
            self.horizontalSlider.show()
            self.panSliderUp.show()
            self.panUpSliderV.show()
            self.label_3.show()
            self.horizontalSlider.show()
            self.pushButton_13.clicked.disconnect(self.play_pause)
            self.pushButton_11.clicked.disconnect(self.select_signal)
            self.pushButton_17.clicked.disconnect(self.zoom_in)
            self.pushButton_18.clicked.disconnect(self.zoom_out)
            self.pushButton_19.clicked.disconnect(self.reset_view)
            self.pushButton_20.clicked.disconnect(self.clear)
            self.horizontalSlider_2.valueChanged.disconnect(lambda value: (self.adjust_speed(value)))
            self.panSliderDown.valueChanged.disconnect(lambda value: (self.panUp(value)))
            self.panDownSliderV.valueChanged.disconnect(lambda value: (self.pan_vertically_Up(value)))
            
    def update_signal(self):
        # if self.signal_displayed and self.signal_playing:
        #     self.plotWidget.clear()
            
            # Initialize variables to find the min and max x-values
            min_x = float('inf')
            max_x = float('-inf')
            
            for data_index, data in enumerate(self.loaded_signals):
                if data is not None:
                    start_row = self.current_row
                    end_row = self.current_row + int(self.rows_to_display * self.zoom_factor * 2)
                    
                    if end_row > len(data):
                        end_row = len(data)
                    
                    if start_row < len(data):
                        color = 'b' if data_index == 0 else 'r'
                        x_values = np.arange(start_row, end_row)
                        shifted_data = data[start_row:end_row]
                        # Update min_x and max_x based on current data
                        min_x = min(min_x, np.min(x_values))
                        max_x = max(max_x, np.max(x_values))
                        
                        # Calculate the vertical zoom factor
                        vertical_zoom = self.zoom_factor

                        # Calculate y_range
                        y_range = (0.3 + vertical_zoom, 0.2 - vertical_zoom)

                        # Apply upper and lower limits
                        y_range = (max(0.3, y_range[0]), min(0.2, y_range[1]))
                        
                        # Set the x and y range for the plot
                        self.plotWidget.plotItem.getViewBox().setRange(xRange=(min_x, max_x), yRange= y_range)
                        self.rightBoundaryDown = max_x
                        self.leftBoundaryDown = min_x
                        
                        self.plotWidget.plot(x_values, shifted_data, pen=color)
            
            self.current_row += 1
            # if self.current_row + int(self.rows_to_display * self.zoom_factor) > len(self.loaded_signals[0]):
            #     self.current_row = 0  # Wrap around to the beginning


    def update_signal_2(self):
        # if self.signal_displayed_2 and self.signal_playing_2:
        #     self.plotWidget2.clear()
            
            min_x = float('inf')
            max_x = float('-inf')
            
            for data_index, data in enumerate(self.loaded_signals_2):
                if data is not None:
                    start_row = self.current_row_2
                    end_row = self.current_row_2 + int(self.rows_to_display * self.zoom_factor_2 * 2)
                    
                    if end_row > len(data):
                        end_row = len(data)
                    
                    if start_row < len(data):
                        color = 'b' if data_index == 0 else 'r'
                        x_values = np.arange(start_row, end_row)
                        shifted_data = data[start_row:end_row]
                        # Update min_x and max_x based on current data
                        min_x = min(min_x, np.min(x_values))
                        max_x = max(max_x, np.max(x_values))
                        
                        # Calculate the vertical zoom factor
                        vertical_zoom_2 = self.zoom_factor_2 

                        # Calculate y_range
                        y_range = (0.3 + vertical_zoom_2, 0.2 - vertical_zoom_2)

                        # Apply upper and lower limits
                        y_range = (max(0.3, y_range[0]), min(0.2, y_range[1]))
                        
                        # Set the x and y range for the plot
                        self.plotWidget2.plotItem.getViewBox().setRange(xRange=(min_x, max_x), yRange= y_range) 
                        self.rightBoundaryUp = max_x
                        self.leftBoundaryUp = min_x                       
                        self.plotWidget2.plot(x_values, shifted_data, pen=color)
            
            self.current_row_2 += 1
            # if self.current_row_2 + int(self.rows_to_display * self.zoom_factor_2) > len(self.loaded_signals_2[0]):
            #     self.current_row_2 = 0  


    def increment_current_row(self):
        self.current_row += 1
        if self.current_row + int(self.rows_to_display * self.zoom_factor) > len(self.loaded_signals[0]):
            self.current_row = 0  
        self.transition_timer.start(self.transition_duration)

    def adjust_speed(self, value):
        scaling_factor_2 = 1000
        speed_value_2 = scaling_factor_2 / (value + 1)
        self.signal_timer_2.setInterval(int(speed_value_2))
        if self.signal_playing_2:
            self.signal_timer_2.start()
    
    
    def adjust_speed_2(self, value):
        scaling_factor_1 = 10000  
        speed_value_1 = scaling_factor_1 / (value + 1)
        self.signal_timer.setInterval(int(speed_value_1))
        if self.signal_playing:
            self.signal_timer.start()
    
    #Handle moving signals from graph to another
    def move_up(self):
        selected_index = self.cB_loadcsvbottom.currentIndex()

        if selected_index >= 0 and selected_index < len(self.loaded_signals):
            data_to_move = self.loaded_signals.pop(selected_index)
            filename = loaded_signal_filenames_2.pop(selected_index)

            self.combo_box()
            self.combo_box_bottom()
            self.loaded_signals_2.append(data_to_move)
            loaded_signal_filenames.append(filename)
            self.combo_box()
            self.update_signal()

    def move_down(self):
        selected_index = self.cB_loadcsvtop.currentIndex()
        
        if selected_index >= 0 and selected_index < len(self.loaded_signals_2):
            data_to_move = self.loaded_signals_2.pop(selected_index)
            filename = loaded_signal_filenames.pop(selected_index)
            
            self.combo_box()
            self.combo_box_bottom()
            self.loaded_signals.append(data_to_move)
            loaded_signal_filenames_2.append(filename)
            self.combo_box_bottom()
            self.update_signal_2()

    #Handle change color 
    def open_color_palette(self):
        self.color = QColorDialog.getColor()


    def open_color_palette_2(self):
        self.color_2 = QColorDialog.getColor()

    def snapshot_2(self):
        print("signal 2 done")
        exporter = ImageExporter(self.plotWidget2.getPlotItem())
        timestamp = int(time.time())  # Get the current timestamp
        file_path_2 = f"{self.folder_path_1_2}/graph_snapshot_{self.photo_index_2}_{timestamp}.png"
        exporter.export(file_path_2)
        img = Image.open(file_path_2)
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        text = f"Photo of {loaded_signal_filenames[self.index_2]}"
        position = (120, 30)
        draw.text(position, text, fill="red", font=font)
        img.save(file_path_2)
        print(f"Saved snapshot of signal {self.index_2} at: {file_path_2}")
        self.photo_index_2 += 1
        self.index_2 += 1

    def fbtnOkDown(self):
            # Change the value in the loaded_signal_filenames list to the current text
            new_value = self.lineNameDown.text()
            loaded_signal_filenames_2[-1] = new_value
            self.combo_box_bottom()
            self.lineNameDown.clear()

    def fbtnOkUp(self):
            # Change the value in the loaded_signal_filenames list to the current text
            new_value_2 = self.lineNameUp.text()
            print("zobry")
            loaded_signal_filenames[-1] = new_value_2
            self.combo_box()
            self.lineNameUp.clear()

    def snapshot(self):
        print("signal 1 done")
        exporter = ImageExporter(self.plotWidget.getPlotItem())
        timestamp = int(time.time())  # Get the current timestamp
        file_path_1 = f"{self.folder_path_1_1}/graph_snapshot_{self.photo_index_1}_{timestamp}.png"
        exporter.export(file_path_1)
        img = Image.open(file_path_1)
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        text = f"Photo of {loaded_signal_filenames[self.index_1]}"
        position = (120, 30)
        draw.text(position, text, fill="red", font=font)
        img.save(file_path_1)
        print(f"Saved snapshot of signal {self.index_1} at: {file_path_1}")
        self.photo_index_1 += 1
        self.index_1 += 1

    from fpdf import FPDF
    from PIL import Image
    import os
    import numpy as np

    def pdf_generate(self):
        # Initialize a PDF object
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Times", size=10)
        page_width = pdf.w - 4 * pdf.l_margin

        # Specify the path to the first page image
        first_page_image_path = r"reportcover.png"
        img = Image.open(first_page_image_path)
        img_width, img_height = img.size
        img_width, img_height = img_width * 0.25, img_height * 0.43  # Adjust image size if needed
        pdf.image(first_page_image_path, x=10, y=30, w=img_width, h=img_height)

        # Specify the folder path where you have the images
        folder_path_1 = "C:\\Users\\Struggler\\Desktop\\DSP Task 1\\task1_gamica&hesham\\photo1"
        folder_path_2 = "C:\\Users\\Struggler\\Desktop\\DSP Task 1\\task1_gamica&hesham\\photo2"
        # folder_path_1 = "C:\\Users\\elnag\\qt\\task1_rename+zoomvertical\\photo2"

        # Define the headers for the statistics table
        headers = ["signal name", "Mean", "Std Dev", "Median"]
        col_width = page_width / 4
        row_height = 12
        fill = 0  # Used to alternate row background color

        # Iterate through the image files in the first folder
        for photo_file in os.listdir(folder_path_1):
            if photo_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')):
                # Add a new page for each image
                pdf.add_page()

                photo_path = os.path.join(folder_path_1, photo_file)
                img = Image.open(photo_path)
                img_width, img_height = img.size
                img_width, img_height = img_width * 0.05, img_height * 0.2
                pdf.image(photo_path, x=10, y=30, w=img_width, h=img_height)

                # Create a statistics table for the current image
                statistics_list = []

                for signal , name in zip(self.loaded_signals,loaded_signal_filenames_2):
                    mean_value = round(np.min(signal),2)
                    std_deviation = round(np.std(signal),2)
                    median_value = round(np.median(signal),2)
                    signal_info = [name, mean_value, std_deviation, median_value]
                    statistics_list.append(signal_info)

                pdf.set_fill_color(0, 123, 255)
                pdf.set_text_color(255, 255, 255)
                pdf.set_xy(10, 100)

                for header in headers:
                    pdf.cell(col_width, row_height, header, 1, 0, "C", 1)
                pdf.ln()

                pdf.set_fill_color(255, 255, 255)
                pdf.set_text_color(0, 0, 0)

                pdf.ln()
                y_position = 112  # Initial Y-coordinate

                for row in statistics_list:
                    pdf.set_xy(10, y_position)  # Set the X-coordinate and the current Y-coordinate
                    for item in row:
                        pdf.cell(col_width, row_height, str(item), 1, 0, "C", fill)
                    fill = 1 - fill
                    y_position += row_height 

        # Iterate through the image files in the second folder
        for photo_file in os.listdir(folder_path_2):
            if photo_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')):
                # Add a new page for each image
                pdf.add_page()

                photo_path = os.path.join(folder_path_2, photo_file)
                img = Image.open(photo_path)
                img_width, img_height = img.size
                img_width, img_height = img_width * 0.05, img_height * 0.2
                pdf.image(photo_path, x=10, y=30, w=img_width, h=img_height)

                # Create a statistics table for the current image
                statistics_list = []
     
                for signal , name in zip(self.loaded_signals_2,loaded_signal_filenames):
                    mean_value = round(np.min(signal),2)
                    std_deviation = round(np.std(signal),2)
                    median_value = round(np.median(signal),2)
                    signal_info = [name, mean_value, std_deviation, median_value]
                    statistics_list.append(signal_info)

                pdf.set_fill_color(0, 123, 255)
                pdf.set_text_color(255, 255, 255)
                pdf.set_xy(10, 100)

                for header in headers:
                    pdf.cell(col_width, row_height, header, 1, 0, "C", 1)
                pdf.ln()

                pdf.set_fill_color(255, 255, 255)
                pdf.set_text_color(0, 0, 0)

                pdf.ln()
                y_position = 112  # Initial Y-coordinate

                for row in statistics_list:
                    pdf.set_xy(10, y_position)  # Set the X-coordinate and the current Y-coordinate
                    for item in row:
                        pdf.cell(col_width, row_height, str(item), 1, 0, "C", fill)
                    fill = 1 - fill
                    y_position += row_height 

        pdf.output('report.pdf')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()

    # Show the window in maximized mode
    window.showMaximized()

    sys.exit(app.exec_())


