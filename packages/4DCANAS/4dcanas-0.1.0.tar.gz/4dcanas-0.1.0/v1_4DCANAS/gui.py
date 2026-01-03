try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QPushButton, QSlider, QLabel, 
                                 QSpinBox, QDoubleSpinBox, QFileDialog)
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtGui import QFont
    import sys
    
    class Application4D(QMainWindow):
        def __init__(self):
            super().__init__()
            self.initUI()
            self.tesseract = None
            self. visualizer = None
        
        def initUI(self):
            self.setWindowTitle('4DCANAS - 4D Visualization Suite')
            self.setGeometry(100, 100, 1200, 800)
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            layout = QVBoxLayout()
            
            title = QLabel('4D TESSERACT VISUALIZER')
            title.setFont(QFont('Arial', 16, QFont.Bold))
            layout.addWidget(title)
            
            control_layout = QHBoxLayout()
            
            control_layout.addWidget(QLabel('Rotation X:'))
            self.slider_x = QSlider(Qt.Horizontal)
            self.slider_x.setMinimum(0)
            self.slider_x.setMaximum(360)
            control_layout.addWidget(self. slider_x)
            
            control_layout.addWidget(QLabel('Rotation Y:'))
            self.slider_y = QSlider(Qt.Horizontal)
            self.slider_y. setMinimum(0)
            self.slider_y.setMaximum(360)
            control_layout.addWidget(self.slider_y)
            
            control_layout.addWidget(QLabel('Rotation Z:'))
            self.slider_z = QSlider(Qt.Horizontal)
            self.slider_z.setMinimum(0)
            self.slider_z. setMaximum(360)
            control_layout.addWidget(self.slider_z)
            
            control_layout.addWidget(QLabel('Rotation W:'))
            self.slider_w = QSlider(Qt. Horizontal)
            self.slider_w.setMinimum(0)
            self.slider_w.setMaximum(360)
            control_layout.addWidget(self.slider_w)
            
            layout.addLayout(control_layout)
            
            button_layout = QHBoxLayout()
            
            btn_visualize = QPushButton('Visualize')
            btn_visualize.clicked.connect(self.visualize)
            button_layout. addWidget(btn_visualize)
            
            btn_animate = QPushButton('Animate')
            btn_animate.clicked. connect(self.animate)
            button_layout.addWidget(btn_animate)
            
            btn_export_obj = QPushButton('Export OBJ')
            btn_export_obj.clicked.connect(self. export_obj)
            button_layout.addWidget(btn_export_obj)
            
            btn_export_json = QPushButton('Export JSON')
            btn_export_json.clicked.connect(self.export_json)
            button_layout.addWidget(btn_export_json)
            
            layout.addLayout(button_layout)
            
            central_widget.setLayout(layout)
        
        def visualize(self):
            from .core import Tesseract
            from .visualization import MatplotlibVisualizer
            
            self.tesseract = Tesseract()
            self.visualizer = MatplotlibVisualizer()
            
            angles = np.array([
                np.radians(self.slider_x. value()),
                np.radians(self.slider_y.value()),
                np.radians(self.slider_z.value()),
                np.radians(self.slider_w.value())
            ])
            
            self. tesseract.rotate(angles)
            fig = self.visualizer.visualize(self.tesseract)
            fig.show()
        
        def animate(self):
            from .core import Tesseract
            from . visualization import MatplotlibVisualizer
            
            self.tesseract = Tesseract()
            self.visualizer = MatplotlibVisualizer()
            anim = self.visualizer.animate(self.tesseract, frames=200)
            plt.show()
        
        def export_obj(self):
            from .export import ExportManager
            filename, _ = QFileDialog.getSaveFileName(self, 'Export OBJ', '', 'OBJ Files (*. obj)')
            if filename: 
                if self.tesseract: 
                    ExportManager.export_obj(self.tesseract, filename)
        
        def export_json(self):
            from .export import ExportManager
            filename, _ = QFileDialog.getSaveFileName(self, 'Export JSON', '', 'JSON Files (*.json)')
            if filename:
                if self.tesseract:
                    ExportManager.export_json(self.tesseract, filename)
    
    def launch_gui():
        app = QApplication(sys.argv)
        window = Application4D()
        window.show()
        sys.exit(app.exec_())

except ImportError:
    class Application4D: 
        def __init__(self):
            raise ImportError("PyQt5 is not installed. Install with: pip install PyQt5")
    
    def launch_gui():
        raise ImportError("PyQt5 is not installed. Install with: pip install PyQt5")