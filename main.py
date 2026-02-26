import sys
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog, QStackedWidget,
    QHBoxLayout, QFrame
)
from PySide6.QtWidgets import QScrollArea
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class TutorialApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutoriel Applicatif")
        self.setMinimumSize(900, 600)

        self.stack = QStackedWidget()
        self.config_data = None
        self.current_index = 0

        self.init_file_selection_page()
        self.init_credentials_page()
        self.init_tutorial_page()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        self.apply_style()

    def init_file_selection_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Sélectionnez un fichier de configuration")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")

        btn = QPushButton("Choisir un fichier JSON")
        btn.clicked.connect(self.load_config)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(btn, alignment=Qt.AlignCenter)
        layout.addStretch()

        page.setLayout(layout)
        self.stack.addWidget(page)

    def load_config(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Choisir fichier JSON", "", "JSON Files (*.json)"
        )
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                self.config_data = json.load(f)

            self.setup_credentials_page()
            self.stack.setCurrentIndex(1)

    def init_credentials_page(self):
        self.credentials_page = QWidget()
        self.credentials_layout = QVBoxLayout()
        self.credentials_page.setLayout(self.credentials_layout)
        self.stack.addWidget(self.credentials_page)

    def setup_credentials_page(self):
        for i in reversed(range(self.credentials_layout.count())):
            self.credentials_layout.itemAt(i).widget().deleteLater()

        title = QLabel(self.config_data["title"])
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("title")

        self.credentials_layout.addWidget(title)

        creds = self.config_data["credentials"]

        for section, values in creds.items():
            frame = QFrame()
            frame.setObjectName("card")
            layout = QVBoxLayout()

            section_title = QLabel(section)
            section_title.setObjectName("subtitle")

            ident = QLabel(f"Identifiant : {values['identifiant']}")
            mdp = QLabel(f"Mot de passe : {values['mdp']}")

            layout.addWidget(section_title)
            layout.addWidget(ident)
            layout.addWidget(mdp)

            frame.setLayout(layout)
            self.credentials_layout.addWidget(frame)

        btn = QPushButton("Démarrer le tutoriel")
        btn.clicked.connect(self.start_tutorial)

        self.credentials_layout.addStretch()
        self.credentials_layout.addWidget(btn, alignment=Qt.AlignCenter)

    def start_tutorial(self):
        self.current_index = 0
        self.display_step()
        self.stack.setCurrentIndex(2)

    def init_tutorial_page(self):
        self.tutorial_page = QWidget()
        self.tutorial_layout = QVBoxLayout()

        self.step_title = QLabel("")
        self.step_title.setObjectName("subtitle")
        self.step_title.setAlignment(Qt.AlignCenter)

        self.step_text = QLabel("")
        self.step_text.setWordWrap(True)
        self.step_text.setAlignment(Qt.AlignCenter)

        # Image avec scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.step_image = QLabel()
        self.step_image.setAlignment(Qt.AlignCenter)

        self.scroll_area.setWidget(self.step_image)

        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Précédent")
        self.next_btn = QPushButton("Suivant")

        self.prev_btn.clicked.connect(self.prev_step)
        self.next_btn.clicked.connect(self.next_step)

        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)

        self.tutorial_layout.addWidget(self.step_title)
        self.tutorial_layout.addWidget(self.step_text)
        self.tutorial_layout.addWidget(self.scroll_area)
        self.tutorial_layout.addLayout(nav_layout)

        self.tutorial_page.setLayout(self.tutorial_layout)
        self.stack.addWidget(self.tutorial_page)

        self.zoom_factor = 1.0
        self.original_pixmap = None

    def display_step(self):
        step = self.config_data["steps"][self.current_index]

        self.step_title.setText(step["title"])
        self.step_text.setText(step["text"])

        self.original_pixmap = QPixmap(step["image"])
        self.zoom_factor = 1.0
        self.update_image()

        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < len(self.config_data["steps"]) - 1)

    def next_step(self):
        if self.current_index < len(self.config_data["steps"]) - 1:
            self.current_index += 1
            self.display_step()

    def prev_step(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.display_step()
    
    def update_image(self):
        if self.original_pixmap:
            size = self.original_pixmap.size()
            new_width = int(size.width() * self.zoom_factor)
            new_height = int(size.height() * self.zoom_factor)

            scaled = self.original_pixmap.scaled(
                new_width,
                new_height,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )

            self.step_image.setPixmap(scaled)

    def wheelEvent(self, event):
        if self.stack.currentIndex() == 2:  # uniquement page tuto
            if event.modifiers() == Qt.ControlModifier:
                if event.angleDelta().y() > 0:
                    self.zoom_factor *= 1.1
                else:
                    self.zoom_factor /= 1.1

                self.zoom_factor = max(0.2, min(self.zoom_factor, 5.0))
                self.update_image()

    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f8;
                font-family: Arial;
                font-size: 14px;
            }

            QLabel#title {
                font-size: 22px;
                font-weight: bold;
                margin: 20px;
            }

            QLabel#subtitle {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }

            QFrame#card {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin: 10px;
            }

            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
            }

            QPushButton:hover {
                background-color: #1565C0;
            }

            QPushButton:disabled {
                background-color: grey;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TutorialApp()
    window.show()
    sys.exit(app.exec())