try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                 QPushButton, QSlider, QLabel, QSpinBox, QDoubleSpinBox,
                                 QFileDialog, QComboBox, QTabWidget, QListWidget, QListWidgetItem,
                                 QInputDialog, QProgressBar, QColorDialog, QDockWidget, QTreeWidget,
                                 QTreeWidgetItem, QMessageBox, QCheckBox, QGroupBox)
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread
    from PyQt5.QtGui import QFont, QColor, QIcon
    from PyQt5.QtOpenGL import QGLWidget
    from PyQt5.Qt import QAction, QMenu
    import sys
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    
    class AdvancedApplication4D(QMainWindow):
        
        def __init__(self):
            super().__init__()
            self.tesseract = None
            self.visualizer = None
            self.shapes = {}
            self.current_shape = None
            self. is_animating = False
            self.animation_timer = QTimer()
            self.animation_timer.timeout. connect(self.update_animation)
            self.animation_frame = 0
            self.initUI()
        
        def initUI(self):
            self.setWindowTitle('4DCANAS - Advanced 4D Visualization Suite')
            self.setGeometry(0, 0, 1600, 1000)
            self.setStyleSheet(self.get_stylesheet())
            
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QHBoxLayout()
            
            left_panel = self.create_left_panel()
            main_layout.addWidget(left_panel, 1)
            
            canvas_layout = QVBoxLayout()
            self.figure = Figure(figsize=(8, 6), dpi=100)
            self.canvas = FigureCanvas(self.figure)
            canvas_layout.addWidget(self.canvas)
            
            control_layout = self.create_control_layout()
            canvas_layout.addLayout(control_layout)
            
            main_layout.addLayout(canvas_layout, 2)
            
            right_panel = self.create_right_panel()
            main_layout.addWidget(right_panel, 1)
            
            central_widget.setLayout(main_layout)
            
            self.create_menu_bar()
            self.create_status_bar()
        
        def create_left_panel(self) -> QWidget:
            panel = QWidget()
            layout = QVBoxLayout()
            
            title = QLabel('🎨 SHAPE LIBRARY')
            title.setFont(QFont('Arial', 12, QFont.Bold))
            layout.addWidget(title)
            
            self.shape_list = QListWidget()
            shapes = ['Tesseract', '16-Cell', '24-Cell', 'Icositetrachoron', 'Custom']
            for shape in shapes:
                item = QListWidgetItem(shape)
                self.shape_list.addItem(item)
            self.shape_list.itemClicked.connect(self.on_shape_selected)
            layout.addWidget(self.shape_list)
            
            separator = QLabel('─' * 30)
            layout.addWidget(separator)
            
            title2 = QLabel('⚙️ TRANSFORMATION')
            title2.setFont(QFont('Arial', 12, QFont.Bold))
            layout.addWidget(title2)
            
            layout.addWidget(QLabel('Scale:'))
            self.scale_slider = QSlider(Qt.Horizontal)
            self.scale_slider.setMinimum(10)
            self.scale_slider.setMaximum(300)
            self.scale_slider.setValue(100)
            self.scale_slider.valueChanged. connect(self.on_scale_changed)
            layout.addWidget(self.scale_slider)
            
            layout.addWidget(QLabel('Rotation Speed:'))
            self.rotation_speed = QDoubleSpinBox()
            self.rotation_speed.setMinimum(0.0)
            self.rotation_speed. setMaximum(1.0)
            self.rotation_speed.setSingleStep(0.01)
            self.rotation_speed.setValue(0.05)
            layout.addWidget(self.rotation_speed)
            
            layout. addSpacing(20)
            
            btn_preset1 = QPushButton('Preset:  Spin XY')
            btn_preset1.clicked.connect(lambda: self.apply_preset('xy'))
            layout.addWidget(btn_preset1)
            
            btn_preset2 = QPushButton('Preset: Spin XW')
            btn_preset2.clicked.connect(lambda: self. apply_preset('xw'))
            layout.addWidget(btn_preset2)
            
            layout.addStretch()
            
            panel. setLayout(layout)
            return panel
        
        def create_control_layout(self) -> QHBoxLayout:
            layout = QHBoxLayout()
            
            layout.addWidget(QLabel('X Rotation:'))
            self.slider_x = QSlider(Qt.Horizontal)
            self.slider_x.setMinimum(0)
            self.slider_x.setMaximum(360)
            self.slider_x.valueChanged.connect(self.update_visualization)
            layout.addWidget(self.slider_x)
            
            layout. addWidget(QLabel('Y Rotation:'))
            self.slider_y = QSlider(Qt.Horizontal)
            self.slider_y.setMinimum(0)
            self.slider_y.setMaximum(360)
            self.slider_y.valueChanged.connect(self.update_visualization)
            layout.addWidget(self.slider_y)
            
            layout. addWidget(QLabel('Z Rotation: '))
            self.slider_z = QSlider(Qt. Horizontal)
            self.slider_z.setMinimum(0)
            self.slider_z.setMaximum(360)
            self.slider_z. valueChanged.connect(self.update_visualization)
            layout.addWidget(self.slider_z)
            
            layout.addWidget(QLabel('W Rotation:'))
            self.slider_w = QSlider(Qt.Horizontal)
            self.slider_w.setMinimum(0)
            self.slider_w.setMaximum(360)
            self.slider_w.valueChanged.connect(self.update_visualization)
            layout.addWidget(self.slider_w)
            
            btn_animate = QPushButton('▶️ Animate')
            btn_animate.clicked.connect(self. toggle_animation)
            layout. addWidget(btn_animate)
            
            btn_reset = QPushButton('↺ Reset')
            btn_reset.clicked.connect(self.reset_view)
            layout.addWidget(btn_reset)
            
            return layout
        
        def create_right_panel(self) -> QWidget:
            panel = QWidget()
            layout = QVBoxLayout()
            
            title = QLabel('📊 PROPERTIES')
            title.setFont(QFont('Arial', 12, QFont.Bold))
            layout.addWidget(title)
            
            self.properties_tree = QTreeWidget()
            self.properties_tree.setHeaderLabels(['Property', 'Value'])
            layout.addWidget(self.properties_tree)
            
            separator = QLabel('─' * 30)
            layout.addWidget(separator)
            
            title2 = QLabel('🎬 EXPORT')
            title2.setFont(QFont('Arial', 12, QFont.Bold))
            layout.addWidget(title2)
            
            btn_export_obj = QPushButton('Export OBJ')
            btn_export_obj.clicked.connect(self.export_obj)
            layout.addWidget(btn_export_obj)
            
            btn_export_json = QPushButton('Export JSON')
            btn_export_json. clicked.connect(self.export_json)
            layout.addWidget(btn_export_json)
            
            btn_export_video = QPushButton('Export Video')
            btn_export_video. clicked.connect(self.export_video)
            layout.addWidget(btn_export_video)
            
            separator2 = QLabel('─' * 30)
            layout.addWidget(separator2)
            
            title3 = QLabel('🎓 EDUCATIONAL')
            title3.setFont(QFont('Arial', 12, QFont.Bold))
            layout.addWidget(title3)
            
            self.difficulty = QComboBox()
            self.difficulty.addItems(['Beginner', 'Intermediate', 'Advanced'])
            layout.addWidget(QLabel('Difficulty Level:'))
            layout.addWidget(self.difficulty)
            
            btn_tutorial = QPushButton('📚 Show Tutorial')
            btn_tutorial. clicked.connect(self.show_tutorial)
            layout.addWidget(btn_tutorial)
            
            layout.addStretch()
            
            panel.setLayout(layout)
            return panel
        
        def create_menu_bar(self):
            menubar = self.menuBar()
            
            file_menu = menubar.addMenu('File')
            
            new_action = QAction('New Project', self)
            new_action.triggered.connect(self.new_project)
            file_menu.addAction(new_action)
            
            open_action = QAction('Open', self)
            open_action. triggered.connect(self.open_project)
            file_menu. addAction(open_action)
            
            save_action = QAction('Save', self)
            save_action.triggered.connect(self.save_project)
            file_menu.addAction(save_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction('Exit', self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            view_menu = menubar.addMenu('View')
            
            projection_menu = view_menu.addMenu('Projection')
            
            ortho_action = QAction('Orthogonal', self)
            ortho_action.triggered.connect(lambda: self.set_projection('orthogonal'))
            projection_menu.addAction(ortho_action)
            
            persp_action = QAction('Perspective', self)
            persp_action.triggered.connect(lambda: self.set_projection('perspective'))
            projection_menu.addAction(persp_action)
            
            stereo_action = QAction('Stereographic', self)
            stereo_action.triggered.connect(lambda: self.set_projection('stereographic'))
            projection_menu.addAction(stereo_action)
            
            help_menu = menubar.addMenu('Help')
            
            about_action = QAction('About 4DCANAS', self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
        
        def create_status_bar(self):
            self.statusBar().showMessage('Ready')
        
        def on_shape_selected(self, item):
            self.current_shape = item. text()
            self.load_shape(self.current_shape)
        
        def load_shape(self, shape_name:  str):
            from 4DCANAS.core import Tesseract, Point4D
            
            if shape_name == 'Tesseract':
                self.tesseract = Tesseract(size=1.0)
            
            self.update_visualization()
        
        def update_visualization(self):
            if self.tesseract is None:
                return
            
            self.figure.clear()
            ax = self.figure.add_subplot(111, projection='3d')
            
            angles = np.array([
                np.radians(self.slider_x. value()),
                np.radians(self.slider_y.value()),
                np.radians(self.slider_z.value()),
                np.radians(self.slider_w.value())
            ])
            
            tesseract_copy = Tesseract(self.tesseract. center, self.tesseract.size)
            tesseract_copy.vertices = [v.coords. copy() for v in self.tesseract.vertices]
            
            from 4DCANAS.core import Rotation4D
            rotation = Rotation4D(angles)
            projected, edges = tesseract_copy.get_3d_projection()
            
            vertices_array = np.array([p.coords for p in projected])
            ax.scatter(vertices_array[:, 0], vertices_array[:, 1], vertices_array[:, 2],
                      c='red', s=100, alpha=0.8)
            
            for edge in edges:
                p1, p2 = projected[edge[0]], projected[edge[1]]
                ax.plot([p1. x, p2.x], [p1.y, p2.y], [p1.z, p2.z], 'b-', alpha=0.6)
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title('4D Visualization')
            
            self.canvas.draw()
        
        def toggle_animation(self):
            self.is_animating = not self.is_animating
            if self. is_animating:
                self.animation_timer.start(50)
            else:
                self.animation_timer.stop()
        
        def update_animation(self):
            self.animation_frame += self.rotation_speed. value()
            
            self.slider_x.setValue(int(self.animation_frame) % 360)
            self.slider_y.setValue(int(self.animation_frame * 0.7) % 360)
            self.slider_z.setValue(int(self.animation_frame * 0.5) % 360)
            self.slider_w.setValue(int(self.animation_frame * 0.3) % 360)
        
        def on_scale_changed(self):
            scale = self.scale_slider.value() / 100.0
            if self.tesseract:
                self.tesseract. size = scale
                self.update_visualization()
        
        def apply_preset(self, preset_type: str):
            self.is_animating = True
            self.animation_timer.start(50)
        
        def reset_view(self):
            self.slider_x.setValue(0)
            self.slider_y.setValue(0)
            self.slider_z.setValue(0)
            self.slider_w.setValue(0)
            self.is_animating = False
            self.animation_timer.stop()
            self.animation_frame = 0
        
        def export_obj(self):
            from 4DCANAS.export import ExportManager
            filename, _ = QFileDialog.getSaveFileName(self, 'Export OBJ', '', 'OBJ Files (*.obj)')
            if filename and self.tesseract:
                ExportManager.export_obj(self.tesseract, filename)
                QMessageBox.information(self, 'Success', f'Exported to {filename}')
        
        def export_json(self):
            from 4DCANAS. export import ExportManager
            filename, _ = QFileDialog.getSaveFileName(self, 'Export JSON', '', 'JSON Files (*.json)')
            if filename and self.tesseract:
                ExportManager.export_json(self.tesseract, filename)
                QMessageBox.information(self, 'Success', f'Exported to {filename}')
        
        def export_video(self):
            QMessageBox.information(self, 'Video Export', 'Video export feature coming soon!')
        
        def set_projection(self, projection_type: str):
            self.statusBar().showMessage(f'Projection: {projection_type}')
        
        def show_tutorial(self):
            if self.difficulty.currentText() == 'Beginner':
                msg = '4D Basics:\n- The 4th dimension (W) is perpendicular to X, Y, Z\n- Rotation in 4D can happen in 6 different planes'
            elif self.difficulty.currentText() == 'Intermediate':
                msg = '4D Geometry:\n- A Tesseract is a 4D hypercube\n- It has 16 vertices and 32 edges\n- 3D projections show cross-sections of 4D objects'
            else:
                msg = 'Advanced 4D Concepts:\n- Clifford algebra for 4D rotations\n- Minkowski space for relativity\n- Conformal geometry in 4D'
            
            QMessageBox.information(self, 'Tutorial', msg)
        
        def show_about(self):
            msg = '''4DCANAS v0.2.0
Advanced 4D Visualization Suite

Developer:  MERO
Telegram: @QP4RM

Features: 
✓ Advanced 4D mathematics
✓ Physics simulation
✓ AI-powered predictions
✓ Professional export
✓ Interactive visualization
'''
            QMessageBox.information(self, 'About 4DCANAS', msg)
        
        def new_project(self):
            self.tesseract = None
            self.figure. clear()
            self.canvas.draw()
        
        def open_project(self):
            filename, _ = QFileDialog.getOpenFileName(self, 'Open Project', '', 'JSON Files (*.json)')
            if filename:
                self.statusBar().showMessage(f'Opened: {filename}')
        
        def save_project(self):
            filename, _ = QFileDialog.getSaveFileName(self, 'Save Project', '', 'JSON Files (*.json)')
            if filename:
                self. statusBar().showMessage(f'Saved: {filename}')
        
        def get_stylesheet(self) -> str:
            return '''
            QMainWindow {
                background-color:  #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color:  #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QSlider:: groove:horizontal {
                background-color: #3e3e3e;
                height: 5px;
            }
            QSlider::handle:horizontal {
                background-color: #0078d4;
                width: 12px;
                margin: -3px 0;
                border-radius: 6px;
            }
            QLabel {
                color: #ffffff;
            }
            QListWidget {
                background-color:  #2d2d2d;
                color: #ffffff;
                border: 1px solid #3e3e3e;
            }
            QTreeWidget {
                background-color:  #2d2d2d;
                color: #ffffff;
                border: 1px solid #3e3e3e;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3e3e3e;
                padding: 3px;
            }
            QMenuBar {
                background-color:  #2d2d2d;
                color: #ffffff;
                border-bottom: 1px solid #3e3e3e;
            }
            QMenu {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3e3e3e;
            }
            QMenu::item: selected {
                background-color:  #0078d4;
            }
            '''
    
    def launch_advanced_gui():
        app = QApplication(sys.argv)
        window = AdvancedApplication4D()
        window