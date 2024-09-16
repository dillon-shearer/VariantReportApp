# variant_reports.py
# C: Nov 23, 2021
# M: Feb  3, 2022
# A: Leandro Lima <leandro.lima@gladstone.ucsf.edu>
# M: May 13, 2024
# A: Stacia Wyman <staciawyman@berkeley.edu>
# M: September 15, 2024
# A: Dillon Shearer <dillon@onpointsci.com>

__version__ = "2.0.0"

import sys
import pandas as pd
import numpy as np
import datetime, pytz
import os
import logging
from PyQt5.QtCore import (
    Qt, QObject, pyqtSignal, pyqtSlot, QThread, QSize
)
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush, QMovie, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit,
    QRadioButton, QCheckBox, QTextEdit, QPushButton, QGroupBox, QButtonGroup,
    QWidget, QMessageBox, QGraphicsDropShadowEffect, QToolTip,
    QAction, QHBoxLayout, QStackedWidget, QFrame, QDialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt  # Importing pyplot for color maps

def resource_path(relative_path):
    """ Get the absolute path to the resource """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Static file paths
als_gene_file = resource_path('./data/ALS_genes.txt')
acmg_gene_file = resource_path('./data/ACMG_genes.txt')
variant_file = resource_path('./data/AALS_937_exonic_report.txt.gz')
metadata_file = resource_path('./data/answer_metadata.csv')
alsod_gene_file = resource_path('./data/alsod_genes.csv')
data_dictionary_file = resource_path('./data/data_dictionary.txt')

class VariantReportApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Variant Report Tool v{__version__}")
        self.setGeometry(100, 100, 1400, 900)  # Increased window size for better layout

        # Set the logo (make sure to replace './images/logo.png' with the actual path to your logo)
        self.setWindowIcon(QIcon(resource_path('./images/logo.png')))  # Logo file path

        # Apply styles and set up the UI
        self.setup_ui()

        # Set the background image using QPalette
        self.set_background_image()

    def setup_ui(self):
        # Create the menu bar
        menubar = self.menuBar()  # Initialize the menu bar

        # Apply styles to the menu bar and menu items
        menubar.setStyleSheet("""
            QMenuBar {
                background: transparent;  /* Makes the background transparent */
                color: white;  /* Set the text color to white */
                font-weight: bold;  /* Makes the text bold */
                padding: 5px;  /* Add some padding */
                font-size: 22px;
            }
            
            QMenuBar::item {
                background: transparent;  /* Transparent background for the menu items */
            }

            QMenuBar::item:selected {
                background: rgba(255, 255, 255, 0.1);  /* Light hover effect */
            }
            
            QMenu {
                background-color: #663366;  /* Match the purple theme */
                color: white;  /* Text color */
            }

            QMenu::item {
                background-color: transparent;
                padding: 5px 25px;
            }

            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 0.2);  /* Hover effect */
            }
        """)

        # Create Help menu
        help_menu = menubar.addMenu("Help")  # Add the "Help" menu
        
        # Add an "About" action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        # Add a "Documentation" action
        doc_action = QAction("Documentation", self)
        doc_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(doc_action)

        # Initialize QStackedWidget to manage multiple pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create pages
        self.create_report_page()
        self.create_summary_page()

    def create_report_page(self):
        # Main widget and layout for Report Generation Page
        self.report_page = QWidget()
        report_layout = QVBoxLayout(self.report_page)
        report_layout.setAlignment(Qt.AlignCenter)

        # Purple container (for the form)
        purple_container = QWidget()
        purple_container.setObjectName("purple_container")
        purple_layout = QVBoxLayout(purple_container)
        purple_layout.setContentsMargins(40, 40, 40, 40)  # Increased padding inside the purple box

        # Apply shadow effect to purple container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 0)
        shadow.setColor(Qt.black)
        purple_container.setGraphicsEffect(shadow)

        # Form elements
        title_section_label = QLabel('ALS WGS SNV Report Generator')
        title_section_label.setAlignment(Qt.AlignCenter)
        title_section_label.setStyleSheet("font-size: 30px; margin-bottom: 25px; color: white; font-weight: bold;")
        purple_layout.addWidget(title_section_label)

        # Bold "Report title:"
        title_label = QLabel("Report title")
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("color: white; font-weight: bold;")
        purple_layout.addWidget(title_label)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter the report title")
        purple_layout.addWidget(self.title_input)

        # Bold "Choose genes" (Group box title only)
        gene_group = QGroupBox("Choose genes")
        gene_group.setStyleSheet("QGroupBox { font-weight: bold; }")  # Make only the header bold
        gene_layout = QVBoxLayout()
        self.gene_button_group = QButtonGroup()

        # Set tooltip font size to 14
        QToolTip.setFont(QFont('Helvetica', 14))
        
        # Read gene lists for tooltips
        with open(als_gene_file, 'r') as f:
            als_genes_list = f.read().splitlines()
        with open(acmg_gene_file, 'r') as f:
            acmg_genes_list = f.read().splitlines()

        # Prepare tooltips with fixed size and black background
        tooltip_style = """
            <div style="
                background-color: black;
                color: white;
                padding: 5px;
                width: 300px;
                white-space: normal;
                font-size: 14px;
            ">
                {}
            </div>
        """

        # Create ALS Genes radio button with tooltip
        als_genes_radio = QRadioButton("ALS Genes ⓘ")
        als_genes_radio.setChecked(True)
        als_genes_tooltip_text = ', '.join(als_genes_list)
        als_genes_radio.setToolTip(tooltip_style.format(als_genes_tooltip_text))
        self.gene_button_group.addButton(als_genes_radio)
        gene_layout.addWidget(als_genes_radio)

        # Create ACMG Genes radio button with tooltip
        acmg_genes_radio = QRadioButton("ACMG Genes ⓘ")
        acmg_genes_tooltip_text = ', '.join(acmg_genes_list)
        acmg_genes_radio.setToolTip(tooltip_style.format(acmg_genes_tooltip_text))
        self.gene_button_group.addButton(acmg_genes_radio)
        gene_layout.addWidget(acmg_genes_radio)

        # Custom Genes option
        custom_genes_radio = QRadioButton("Custom gene list (one per line)")
        self.gene_button_group.addButton(custom_genes_radio)
        gene_layout.addWidget(custom_genes_radio)

        self.custom_genes_text = QTextEdit()
        self.custom_genes_text.setPlaceholderText("Enter custom gene list (SOD1, etc.)")
        gene_layout.addWidget(self.custom_genes_text)

        gene_group.setLayout(gene_layout)
        purple_layout.addWidget(gene_group)

        self.custom_genes_text.setToolTip("Enter custom gene list here, one gene per line.")

        # Bold "Samples" (Group box title only)
        sample_group = QGroupBox("Samples")
        sample_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        sample_layout = QVBoxLayout()
        self.answer_als_checkbox = QCheckBox("AnswerALS (937 whole genomes)")
        self.answer_als_checkbox.setChecked(True)  # Preselect the checkbox
        sample_layout.addWidget(self.answer_als_checkbox)
        sample_group.setLayout(sample_layout)
        purple_layout.addWidget(sample_group)

        # Create the group box for variants with a bold title
        variant_group = QGroupBox("Choose variants")
        variant_group.setStyleSheet("QGroupBox { font-weight: bold; }")  # Make only the header bold

        # Create a layout for the group box
        variant_layout = QVBoxLayout()

        # Add italic subtext for variants inside the group box (under the title)
        variant_subtext = QLabel("<i>Default: Non-synonymous</i>")
        variant_subtext.setStyleSheet("font-size: 14px; color: white;")  # Smaller font size and color
        variant_subtext.setAlignment(Qt.AlignLeft)
        variant_layout.addWidget(variant_subtext)

        # Add checkbox for synonymous SNVs
        self.synonymous_checkbox = QCheckBox("Include synonymous SNVs")
        self.synonymous_checkbox.setStyleSheet("color: white;")  # Ensure the text is white
        variant_layout.addWidget(self.synonymous_checkbox)

        # Add to the UI: A checkbox for including upstream/downstream variants
        self.include_up_down_checkbox = QCheckBox("Include upstream/downstream variants (3kb)")
        self.include_up_down_checkbox.setStyleSheet("color: white;")  # Ensure the text is white
        variant_layout.addWidget(self.include_up_down_checkbox)

        # Set the layout for the group box
        variant_group.setLayout(variant_layout)

        # Add the variant group box to the main layout
        purple_layout.addWidget(variant_group)

        # Create the group box for ethnicities with a bold title
        ethnicity_group = QGroupBox("Choose ethnicities")
        ethnicity_group.setStyleSheet("QGroupBox { font-weight: bold; }")  # Make only the header bold

        # Create a layout for the group box
        ethnicity_layout = QVBoxLayout()

        # Add italic subtext for ethnicities inside the group box (under the title)
        ethnicity_subtext = QLabel("<i>Default: All ethnicities</i>")
        ethnicity_subtext.setStyleSheet("font-size: 14px; color: white;")  # Smaller font size and color
        ethnicity_subtext.setAlignment(Qt.AlignLeft)
        ethnicity_layout.addWidget(ethnicity_subtext)

        # Add checkbox for EUR ancestry
        self.eur_checkbox = QCheckBox("EUR (European Ancestry >= 85%)")
        self.eur_checkbox.setStyleSheet("color: white;")  # Ensure the text is white
        ethnicity_layout.addWidget(self.eur_checkbox)

        # Set the layout for the group box
        ethnicity_group.setLayout(ethnicity_layout)

        # Add the ethnicity group box to the main layout
        purple_layout.addWidget(ethnicity_group)

        # Add Generate Report Button
        self.generate_button = QPushButton("Create report")
        self.generate_button.setMaximumWidth(250)  # Slightly larger button
        purple_layout.addWidget(self.generate_button, alignment=Qt.AlignCenter)

        # Add spinning indicator
        self.spinner_label = QLabel()
        self.spinner_movie = QMovie(resource_path('./images/spinner.gif'))  # Path to spinner GIF
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_label.setAlignment(Qt.AlignCenter)
        self.spinner_label.setVisible(False)  # Hidden by default
        purple_layout.addWidget(self.spinner_label)

        # Add purple container to the report layout
        report_layout.addWidget(purple_container)

        # Style the purple container
        purple_container.setStyleSheet("""
            QWidget#purple_container {
                background-color: #663366;
                border-radius: 15px;
                max-width: 900px;  /* Increased max width for better layout */
            }
            QLabel, QRadioButton, QCheckBox, QGroupBox {
                color: white;
            }
            QLineEdit, QTextEdit {
                background-color: rgba(245, 245, 245, 0.8);
                color: black;
                border-radius: 10px;
                padding: 10px;
                width: 100%;  /* Ensure input fields take up the available width */
            }
            QPushButton {
                background-color: rgba(153, 102, 153, 0.9);
                color: white;
                padding: 12px;  /* Increased padding for a larger button */
                border-radius: 5px;
                font-size: 16px;  /* Increased font size for better readability */
            }
            QPushButton:hover {
                background-color: rgba(153, 102, 153, 1);
            }
        """)

        # Connect Generate Report button
        self.generate_button.clicked.connect(self.generate_report)

        # Add the report page to the stacked widget
        self.stacked_widget.addWidget(self.report_page)

    def create_summary_page(self):
        # Summary Visuals Page
        self.summary_page = QWidget()
        summary_layout = QVBoxLayout(self.summary_page)
        summary_layout.setAlignment(Qt.AlignCenter)

        # Purple container for summary (similar to report page)
        purple_container = QWidget()
        purple_container.setObjectName("purple_container_summary")
        purple_layout = QVBoxLayout(purple_container)
        purple_layout.setContentsMargins(40, 40, 40, 40)  # Increased padding inside the purple box

        # Apply shadow effect to purple container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 0)
        shadow.setColor(Qt.black)
        purple_container.setGraphicsEffect(shadow)

        # Title
        summary_title = QLabel("Report Summary")
        summary_title.setAlignment(Qt.AlignCenter)
        summary_title.setStyleSheet("font-size: 28px; margin-bottom: 25px; color: white; font-weight: bold;")
        purple_layout.addWidget(summary_title)

        # Applied Filters Section
        filters_label = QLabel("Applied Filters:")
        filters_label.setStyleSheet("font-size: 18px; color: white; font-weight: bold;")
        purple_layout.addWidget(filters_label)

        self.applied_filters_text = QLabel()
        self.applied_filters_text.setStyleSheet("font-size: 16px; color: white;")
        self.applied_filters_text.setWordWrap(True)
        purple_layout.addWidget(self.applied_filters_text)

        # Summary Statistics Labels
        self.total_variants_label = QLabel("Total Variants: ")
        self.total_variants_label.setStyleSheet("font-size: 18px; color: white;")
        purple_layout.addWidget(self.total_variants_label)

        self.total_samples_label = QLabel("Total Samples: ")
        self.total_samples_label.setStyleSheet("font-size: 18px; color: white;")
        purple_layout.addWidget(self.total_samples_label)

        self.num_genes_label = QLabel("Number of Genes: ")
        self.num_genes_label.setStyleSheet("font-size: 18px; color: white;")
        purple_layout.addWidget(self.num_genes_label)

        # Variant Types Pie Chart
        self.variant_types_canvas = FigureCanvas(Figure(figsize=(6, 5), facecolor='#663366'))  # Set figure facecolor to purple
        purple_layout.addWidget(self.variant_types_canvas)
        self.variant_types_ax = self.variant_types_canvas.figure.subplots()
        self.variant_types_ax.set_facecolor('#663366')  # Set axes facecolor to purple

        # Remove spines to eliminate white lines
        for spine in self.variant_types_ax.spines.values():
            spine.set_visible(False)

        # Set the title with white color
        self.variant_types_ax.set_title("Variant Types Distribution", fontsize=16, color='white')

        # Initialize annotation for hover-over
        self.annotation = self.variant_types_ax.annotate(
            "",
            xy=(0,0),
            xytext=(20,20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="#663366"),  # Match annotation box color to purple
            arrowprops=dict(arrowstyle="->", color="white")  # Arrow color white for visibility
        )
        self.annotation.set_visible(False)

        # Set the background color of the FigureCanvas widget to purple
        self.variant_types_canvas.setStyleSheet("background-color: #663366;")

        # Connect the motion_notify_event to the hover function
        self.variant_types_canvas.mpl_connect("motion_notify_event", self.on_hover)

        # Buttons at the bottom
        button_layout = QHBoxLayout()

        self.create_another_button = QPushButton("Create Another Report")
        self.create_another_button.setMaximumWidth(250)  # Increased button size
        self.create_another_button.clicked.connect(self.reset_form)

        self.exit_button = QPushButton("Exit")
        self.exit_button.setMaximumWidth(150)  # Increased button size
        self.exit_button.clicked.connect(QApplication.quit)

        button_layout.addStretch()
        button_layout.addWidget(self.create_another_button)
        button_layout.addWidget(self.exit_button)

        purple_layout.addLayout(button_layout)

        # Style the summary container
        purple_container.setStyleSheet("""
            QWidget#purple_container_summary {
                background-color: #663366;
                border-radius: 15px;
                max-width: 1000px;  /* Increased max width for better layout */
            }
            QLabel, QPushButton {
                color: white;
            }
            QPushButton {
                background-color: rgba(153, 102, 153, 0.9);
                padding: 12px;  /* Increased padding for larger buttons */
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(153, 102, 153, 1);
            }
        """)

        # Add purple container to the summary layout
        summary_layout.addWidget(purple_container)

        # Add the summary page to the stacked widget
        self.stacked_widget.addWidget(self.summary_page)

    def set_background_image(self):
        # Load the image
        background_image = QPixmap(resource_path('./images/background.jpeg'))

        # Scale the image to the window size
        scaled_image = background_image.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

        # Create a palette and set the brush
        palette = self.palette()
        palette.setBrush(QPalette.Window, QBrush(scaled_image))
        self.setPalette(palette)

    def resizeEvent(self, event):
        # Call the base class resizeEvent
        super().resizeEvent(event)
        # Update the background image
        self.set_background_image()

    def generate_report(self):
        # Gather form data
        report_title = self.title_input.text()

        # Determine selected genes
        if self.gene_button_group.checkedButton().text() == "ALS Genes ⓘ":
            genes_list = "ALSgenes"
            custom_genes = None
            genes_selected = "ALS Genes"
        elif self.gene_button_group.checkedButton().text() == "ACMG Genes ⓘ":
            genes_list = "ACMGgenes"
            custom_genes = None
            genes_selected = "ACMG Genes"
        else:
            genes_list = "textboxgenes"
            custom_genes = self.custom_genes_text.toPlainText()
            genes_selected = f"Custom Genes: {custom_genes.replace(',', ', ')}"

        answer_als = self.answer_als_checkbox.isChecked()
        samples_selected = "AnswerALS (937 whole genomes)" if answer_als else "No AnswerALS samples selected"

        synonymous_snvs = self.synonymous_checkbox.isChecked()
        synonymous_selected = "Included" if synonymous_snvs else "Excluded"

        include_up_down = self.include_up_down_checkbox.isChecked()
        up_down_selected = "Included" if include_up_down else "Excluded"

        eur_selected = self.eur_checkbox.isChecked()
        ethnicity_selected = "EUR ancestry >= 85%" if eur_selected else "All ethnicities"

        # Disable the button while processing
        self.generate_button.setEnabled(False)

        # Create timestamp for logging and reports
        timestamp = datetime.datetime.now(pytz.timezone('America/Los_Angeles')).strftime('%Y-%m-%d_%H%M')

        # Set up logging
        if not os.path.exists('./log'):
            os.makedirs('./log')
        logging.basicConfig(
            filename=f'./log/report_generation_{timestamp}.log',
            filemode='w',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        logging.info("Report generation started.")

        if not os.path.exists('./reports'):
                os.makedirs('./reports')

        # Show and start the spinner
        self.spinner_movie.setScaledSize(QSize(50, 50))  # Adjust the QSize values to control the spinner size
        self.spinner_label.setVisible(True)
        self.spinner_movie.start()

        # Create a QThread
        self.thread = QThread()
        # Create a worker object
        self.worker = ReportGeneratorWorker(
            report_title, genes_list, answer_als, synonymous_snvs,
            eur_selected, custom_genes if genes_list == "textboxgenes" else None, timestamp
        )
        # Move the worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Start the thread
        self.thread.start()

    def on_finished(self, file_path, summary_data):
        # Stop and hide the spinner
        self.spinner_movie.stop()
        self.spinner_label.setVisible(False)
        
        logging.info(f"Report generated successfully: {file_path}")
        
        # Store summary data for visualization
        self.summary_data = summary_data

        # Update the summary visuals
        self.update_summary_visuals()

        # Switch to the summary page
        self.stacked_widget.setCurrentWidget(self.summary_page)

        # Re-enable the generate button
        self.generate_button.setEnabled(True)

    def on_error(self, error_message):
        # Stop and hide the spinner on error
        self.spinner_movie.stop()
        self.spinner_label.setVisible(False)

        logging.error(f"Error occurred during report generation: {error_message}")
        
        QMessageBox.critical(self, "Error", f"An error occurred while generating the report: {error_message}")
        self.generate_button.setEnabled(True)

    def reset_form(self):
        # Switch back to the report page
        self.stacked_widget.setCurrentWidget(self.report_page)
        # Reset the form
        self._reset_form()

    def _reset_form(self):
        # Reset the title input
        self.title_input.clear()
        # Reset the gene selection
        for button in self.gene_button_group.buttons():
            if button.text() == "ALS Genes ⓘ":
                button.setChecked(True)
            else:
                button.setChecked(False)
        # Clear custom genes text
        self.custom_genes_text.clear()
        # Reset checkboxes
        self.answer_als_checkbox.setChecked(True)
        self.synonymous_checkbox.setChecked(False)
        self.eur_checkbox.setChecked(False)
        self.include_up_down_checkbox.setChecked(False)
        # Enable the generate button
        self.generate_button.setEnabled(True)

    def show_about_dialog(self):
        about_text = """
        <div style="text-align: center; font-size: 18px; color: black;">
            <img src='{}' alt='logo' width='100' height='100'/>
            <h2 style="color: black;"><b><u>Variant Report Tool v{}</b></u></h2>
            <p style="text-align: left;">Authors:</p>
            <p style="text-align: left;"><strong>Leandro Lima</strong></p>
            <p style="text-align: left;"><strong>Stacia Wyman</strong></p>
            <p style="text-align: left;"><strong>Dillon Shearer</strong></p>
            <br>
            <p style="text-align: left;">For more information, please contact:</p>
            <p style="text-align: left;"><strong>Terri Thompson</strong><br> &lt;<a href="mailto:terri@onpointsci.com" style="color: black;">terri@onpointsci.com</a>&gt;</p>
        </div>
        """.format(resource_path('./images/logo.png'), __version__)

        msg = QMessageBox(self)
        msg.setWindowTitle("About Variant Report Tool")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #ADD8E6;  /* Light blue background */
                color: black;
                font-family: Arial;
            }
            QLabel {
                color: black;
                font-size: 14px;
            }
            QPushButton {
                background-color: #ADD8E6;  /* Match background */
                color: black;
                padding: 5px 10px;
                border: 1px solid black;
            }
            QPushButton:hover {
                background-color: #88B0C8;  /* Slightly darker shade for hover effect */
            }
        """)
        msg.setText(about_text)
        msg.exec_()

    def show_help_dialog(self):
        help_text = """
        <div style="text-align: center; font-size: 16px; color: black;">
            <img src='{}' alt='logo' width='100' height='100'/>
            <h2 style="color: black;"><b><u>Help Documentation</b></u></h2>
            <div style="text-align: left;">
                <p><strong>Report Title:</strong> Enter a descriptive title for your report.</p>
                <p><strong>Choose Genes:</strong> Select which genes to include in the analysis (ALS Genes, ACMG Genes, or a custom list).</p>
                <p><strong>Samples:</strong> Select the dataset to use for analysis.</p>
                <p><strong>Variants:</strong> Choose whether to include synonymous variants.</p>
                <p><strong>Ethnicities:</strong> Optionally filter by ethnicity (e.g., European Ancestry >= 85%).</p>
            </div>
        </div>
        """.format(resource_path('./images/logo.png'))

        # Create a custom QDialog for the help window
        dialog = QDialog(self)
        dialog.setWindowTitle("Help")
        dialog.setMinimumSize(500, 600)

        # Set layout for the dialog
        layout = QVBoxLayout()

        # Add the help text
        help_label = QLabel()
        help_label.setTextFormat(Qt.RichText)
        help_label.setText(help_text)
        help_label.setWordWrap(True)
        layout.addWidget(help_label)

        # Add a collapsible version log
        version_log_button = QPushButton("Show Version Log")
        version_log_button.setStyleSheet("""
            font-size: 16px; 
            padding: 8px; 
            text-align: left; 
            font-weight: bold;  /* Make the text bold */
            text-align: center;  /* Center the text */
            background-color: #ADD8E6;  /* Light blue background */
            color: black;
            border: 1px solid black;
        """)
        layout.addWidget(version_log_button)

        # Create a QTextEdit for the version log content (or QLabel for simple text)
        version_log_content = QTextEdit()
        version_log_content.setReadOnly(True)
        version_log_content.setFrameStyle(QFrame.NoFrame)
        version_log_content.setVisible(False)  # Initially hidden
        version_log_content.setStyleSheet("""
            font-size: 14px; 
            color: black; 
            background-color: #ADD8E6;  /* Light blue background */
            border: none;
        """)

        # Set the version log content
        version_log_content.setHtml("""
            <h3 style="text-align: left; color: black;"><u>Version Log</u></h3>
            <div style="text-align: left;">
                <p><strong>v2.0.0 (September 15, 2024) - Dillon Shearer:</strong></p>
                <ul>
                    <li>Converted the tool to a GUI-based application</li>
                    <li>Added enhancements like the help menu and version log</li>
                </ul>
                <p><strong>v1.1.0 (May 13, 2024) - Stacia Wyman:</strong></p>
                <ul>
                    <li>General enhancements and optimizations</li>
                </ul>
                <p><strong>v1.0.0 (February 3, 2022) - Leandro Lima:</strong></p>
                <ul>
                    <li>Initial release with core functionality for report generation</li>
                </ul>
            </div>
        """)

        # Add the version log to the layout
        layout.addWidget(version_log_content)

        # Connect the button to show/hide the version log
        def toggle_version_log():
            if version_log_content.isVisible():
                version_log_content.setVisible(False)
                version_log_button.setText("Show Version Log")
            else:
                version_log_content.setVisible(True)
                version_log_button.setText("Hide Version Log")

        version_log_button.clicked.connect(toggle_version_log)

        # Apply the custom style to the dialog
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ADD8E6;  /* Light blue background */
                font-family: Arial;
            }
            QLabel {
                color: black;
                font-size: 14px;
            }
            QPushButton {
                background-color: #ADD8E6;  /* Light blue background */
                color: black;
                padding: 5px 10px;
                border: 1px solid black;
            }
            QPushButton:hover {
                background-color: #88B0C8;  /* Slightly darker shade for hover effect */
            }
        """)

        # Set the layout to the dialog
        dialog.setLayout(layout)

        # Show the dialog
        dialog.exec_()

    def update_summary_visuals(self):
        """
        Update the summary visuals using the summary_data provided by the worker.
        """
        if not hasattr(self, 'summary_data') or not self.summary_data:
            logging.error("No summary data available to display.")
            return

        # Update applied filters text
        applied_filters = self.summary_data.get('applied_filters', {})
        filters_text = ""
        if applied_filters.get('report_title'):
            filters_text += f"<b>Report Title:</b> {applied_filters['report_title']}<br>"
        if applied_filters.get('genes_selected'):
            filters_text += f"<b>Gene Selection:</b> {applied_filters['genes_selected']}<br>"
        if applied_filters.get('samples_selected'):
            filters_text += f"<b>Samples Selected:</b> {applied_filters['samples_selected']}<br>"
        if applied_filters.get('synonymous_selected'):
            filters_text += f"<b>Synonymous SNVs:</b> {applied_filters['synonymous_selected']}<br>"
        if applied_filters.get('up_down_selected'):
            filters_text += f"<b>Upstream/Downstream Variants:</b> {applied_filters['up_down_selected']}<br>"
        if applied_filters.get('ethnicity_selected'):
            filters_text += f"<b>Ethnicity Filter:</b> {applied_filters['ethnicity_selected']}<br>"

        self.applied_filters_text.setText(filters_text)

        # Update summary labels
        self.total_variants_label.setText(f"Total Variants: {self.summary_data.get('total_variants', 0)}")
        self.total_samples_label.setText(f"Total Samples: {self.summary_data.get('total_samples', 0)}")
        self.num_genes_label.setText(f"Number of Genes: {self.summary_data.get('num_genes', 0)}")

        # Update variant types pie chart
        variant_types = self.summary_data.get('variant_types', {})
        if variant_types:
            self.variant_types_ax.clear()
            labels = list(variant_types.keys())
            sizes = list(variant_types.values())
            colors = plt.cm.Paired.colors[:len(labels)]  # Ensure enough colors

            # Set the background color of the axes to match the page
            self.variant_types_ax.set_facecolor('#663366')

            # Set the background color of the figure to match the page
            self.variant_types_canvas.figure.set_facecolor('#663366')

            # Create pie chart without labels
            wedges, _ = self.variant_types_ax.pie(sizes, labels=None, startangle=140, colors=colors)
            self.variant_types_ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            self.variant_types_ax.set_title("Variant Types Distribution", fontsize=16, color='white')  # Set title color to white

            # Adjust layout to make space for the legend below
            self.variant_types_canvas.figure.subplots_adjust(bottom=0.35)  # Increased bottom margin

            # Add legend centered below the pie chart with white background
            legend = self.variant_types_ax.legend(
                wedges, labels,
                title="Variant Types",
                loc="upper center",
                bbox_to_anchor=(0.5, -0.25),  # Positioned below the pie chart
                ncol=min(len(labels), 3),    # Adjust number of columns based on number of labels
                fontsize='small'  # Smaller font size
            )
            legend.get_title().set_fontsize('small')  # Smaller font size for legend title

            # Make legend background white
            frame = legend.get_frame()
            frame.set_facecolor('white')  # Set legend background to white
            frame.set_edgecolor('white')  # Set frame edge to white

            # Store wedges for hover functionality
            self.wedges = wedges
            self.sizes = sizes
            self.labels = labels

            # Apply tight layout to ensure everything fits
            self.variant_types_canvas.figure.tight_layout()

            self.variant_types_canvas.draw()
        else:
            # If no variant types data, hide the chart
            self.variant_types_canvas.hide()

    def on_hover(self, event):
        """Show annotation when hovering over a pie slice."""
        if not hasattr(self, 'wedges'):
            return

        vis = self.annotation.get_visible()
        for wedge, size, label in zip(self.wedges, self.sizes, self.labels):
            contains, attr = wedge.contains(event)
            if contains:
                # Calculate the angle of the mouse position
                angle = (wedge.theta2 - wedge.theta1)/2. + wedge.theta1
                x = wedge.r * 0.7 * np.cos(np.deg2rad(angle))
                y = wedge.r * 0.7 * np.sin(np.deg2rad(angle))
                self.annotation.xy = (x, y)
                text = f"{label}: {size}"
                self.annotation.set_text(text)
                self.annotation.set_visible(True)
                self.variant_types_canvas.draw_idle()
                return
        if vis:
            self.annotation.set_visible(False)
            self.variant_types_canvas.draw_idle()

class ReportGeneratorWorker(QObject):
    finished = pyqtSignal(str, dict)  # Signal to emit when finished, with file path and summary data
    error = pyqtSignal(str)           # Signal to emit if there is an error

    def __init__(self, report_title, genes_list, answer_als, synonymous_snvs, eur_selected, custom_genes, timestamp):
        super().__init__()
        self.report_title = report_title
        self.genes_list = genes_list
        self.answer_als = answer_als
        self.synonymous_snvs = synonymous_snvs
        self.eur_selected = eur_selected
        self.custom_genes = custom_genes
        self.timestamp = timestamp

    @pyqtSlot()
    def run(self):
        try:
            file_path, summary_data = generate_report_logic(
                self.report_title, self.genes_list, self.answer_als,
                self.synonymous_snvs, self.eur_selected,
                self.custom_genes, self.timestamp
            )
            self.finished.emit(file_path, summary_data)
        except Exception as e:
            self.error.emit(str(e))

# Transformation Logic
def generate_report_logic(report_title, genes_list, answer_als, synonymous_snvs, eur_selected, custom_genes=None, timestamp=None):
    try:
        # Load genes
        logging.info(f"Fetching gene list for: {genes_list}")
        genes = get_genes(genes_list, custom_genes)

        # Load metadata
        logging.info("Fetching metadata...")
        aals_metadata = get_metadata()
        aals_samples_from_metadata = set(aals_metadata['ExternalSubjectId'][aals_metadata['Project'].str.contains('Answer ALS', na=False)])
        all_ctrls = set(aals_metadata['ExternalSubjectId'][aals_metadata['Subject Group'].str.contains('Neurological Control', na=False)])
        all_cases = set(aals_metadata['ExternalSubjectId'][~aals_metadata['Subject Group'].str.contains('Control', na=False)])

        if eur_selected:
            logging.info("Applying European ancestry filter...")
            # Since the column is in decimals (0.xx), use 0.85 instead of 85
            europeans = set(aals_metadata['ExternalSubjectId'][aals_metadata['pct_european'] >= 0.85])
            aals_samples_from_metadata = aals_samples_from_metadata.intersection(europeans)

        # Load and concatenate chunks of the variant file
        logging.info(f"Reading variant file in chunks from: {variant_file}")
        exonic_vars_df_list = []
        total_rows = 0
        for chunk in pd.read_csv(variant_file, sep='\t', compression='gzip', chunksize=1000000):
            exonic_vars_df_list.append(chunk)
            total_rows += len(chunk)
            logging.info(f"Processed chunk: {len(chunk)} rows")

        # Concatenate all chunks into a single DataFrame
        exonic_vars_df = pd.concat(exonic_vars_df_list, ignore_index=True)
        logging.info(f"Total rows loaded: {total_rows}")

        # Filter by genes and SNV types
        logging.info("Filtering exonic variants based on genes...")
        exonic_vars_df = exonic_vars_df[exonic_vars_df['Gene'].isin(genes)]

        if not synonymous_snvs:
            logging.info("Filtering out synonymous SNVs...")
            exonic_vars_df = exonic_vars_df[exonic_vars_df['ExonicFunc'] != 'synonymous_SNV']

        logging.info(f"Exonic variants after filtering: {len(exonic_vars_df)}")

        # Apply metadata filters and conditions
        anno_cols_from_report, aals_samples_from_report = get_anno_cols()
        metadata_samples = aals_samples_from_metadata.intersection(aals_samples_from_report)
        exonic_vars_df = exonic_vars_df[anno_cols_from_report + list(metadata_samples)]
        exonic_vars_df = get_vars_in_selected_samples(exonic_vars_df, anno_cols_from_report, list(metadata_samples))

        logging.info(f"Variants after selecting samples: {len(exonic_vars_df)}")

        # Merging with ALSOD gene data
        logging.info("Merging with ALSOD gene data...")
        alsod_genes = pd.read_csv(alsod_gene_file)
        alsod_genes.columns = ['Gene', 'Gene name', 'ALSoD category']
        exonic_vars_df = pd.merge(exonic_vars_df, alsod_genes.drop('Gene name', axis=1), on='Gene', how='left')

        # C9orf72 and ATXN2 expansion filters
        logging.info("Applying C9orf72 and ATXN2 expansion filters...")
        c9_expansion_samples = set(aals_metadata['ExternalSubjectId'][aals_metadata['C9 repeat size'].apply(lambda x: max(map(int, x.split('/'))) > 26 if pd.notna(x) else False)])
        atxn2_expansion_samples = set(aals_metadata['ExternalSubjectId'][aals_metadata['ATXN2 repeat size'].apply(lambda x: max(map(int, x.split('/'))) > 26 if pd.notna(x) else False)])

        # Intersect with exonic_vars_df columns to ensure valid samples
        c9_expansion_samples = c9_expansion_samples.intersection(exonic_vars_df.columns)
        atxn2_expansion_samples = atxn2_expansion_samples.intersection(exonic_vars_df.columns)

        # Filter the exonic variants based on the expansion samples
        c9_exonic_vars = exonic_vars_df[list(anno_cols_from_report) + list(c9_expansion_samples)]
        c9_exonic_vars = get_vars_in_selected_samples(c9_exonic_vars, list(anno_cols_from_report), list(c9_expansion_samples))

        atxn2_exonic_vars = exonic_vars_df[list(anno_cols_from_report) + list(atxn2_expansion_samples)]
        atxn2_exonic_vars = get_vars_in_selected_samples(atxn2_exonic_vars, list(anno_cols_from_report), list(atxn2_expansion_samples))

        logging.info(f'len(c9_expansion_samples) = {len(c9_expansion_samples)} {c9_exonic_vars.shape} | len(ATXN2_expansion_samples) = {len(atxn2_expansion_samples)} {atxn2_exonic_vars.shape}')

        # Combinations of different sheet data
        combinations = {
            'all cases vs all controls': {
                'cases': list(all_cases.intersection(metadata_samples)),
                'ctrls': list(all_ctrls.intersection(metadata_samples)),
                'data': exonic_vars_df
            },
            'C9 (filters)': {'samples': list(c9_expansion_samples), 'data': c9_exonic_vars},
            'ATXN2 (filters)': {'samples': list(atxn2_expansion_samples), 'data': atxn2_exonic_vars},
        }

        # ClinVar, Intervar, and Damaging Variants
        clinvar_exon = exonic_vars_df[exonic_vars_df['ClinVar sig (CLINSIG)'].str.contains('athogenic', na=False)]
        intervar_exon = exonic_vars_df[exonic_vars_df['ACMG variant'].str.contains('athogenic', na=False)]
        insilico_exon = exonic_vars_df[exonic_vars_df['in silico Predictions'].apply(dmg_tools) >= 6]

        combinations.update({
            'ClinVar': {'cases': list(all_cases), 'ctrls': list(all_ctrls), 'data': clinvar_exon},
            'Intervar': {'cases': list(all_cases), 'ctrls': list(all_ctrls), 'data': intervar_exon},
            'Damaging variants': {'cases': list(all_cases), 'ctrls': list(all_ctrls), 'data': insilico_exon}
        })

        # Specify sheet order, with 'READ ME' at the front
        sheet_order = ['READ ME'] + list(combinations.keys()) + ['Data dictionary']

        # Write report to Excel
        xls_path = f"./reports/{report_title.replace(' ', '_')}_{timestamp}.xlsx"
        writer = pd.ExcelWriter(xls_path, engine='xlsxwriter')

        # Write the ReadMe sheet first
        logging.info("Writing 'READ ME' sheet...")
        readme_text = make_readme(genes_list, genes, combinations, anno_cols_from_report, report_title)
        workbook = writer.book
        worksheet = workbook.add_worksheet('READ ME')
        writer.sheets['READ ME'] = worksheet
        # Write ReadMe text with formatting
        worksheet.write('A1', readme_text)

        # Write all combination sheets
        for sheet_name in combinations.keys():
            logging.info(f"Writing sheet: {sheet_name}")
            df = combinations[sheet_name]['data']
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        # Add Data Dictionary with a larger textbox
        logging.info("Writing Data Dictionary...")
        with open(data_dictionary_file, 'r', encoding='utf-8') as f:
            data_dict = f.read()
        worksheet = workbook.add_worksheet('Data dictionary')
        writer.sheets['Data dictionary'] = worksheet
        worksheet.write('A1', data_dict)

        writer.close()
        logging.info(f"Report generated successfully at {xls_path}")

        # Prepare summary data for visualization
        summary_data = {
            'total_variants': len(exonic_vars_df),
            'total_samples': len(metadata_samples),
            'num_genes': len(genes),
            'variant_types': exonic_vars_df['ExonicFunc'].value_counts().to_dict(),
            'applied_filters': {
                'report_title': report_title,
                'genes_selected': "ALS Genes" if genes_list == "ALSgenes" else ("ACMG Genes" if genes_list == "ACMGgenes" else f"Custom Genes: {custom_genes.replace(',', ', ')}"),
                'samples_selected': "AnswerALS (937 whole genomes)" if answer_als else "No AnswerALS samples selected",
                'synonymous_selected': "Included" if synonymous_snvs else "Excluded",
                'ethnicity_selected': "EUR ancestry >= 85%" if eur_selected else "All ethnicities"
            }
            # Add more summary metrics as needed
        }

        return xls_path, summary_data

    except Exception as e:
        logging.error(f"Error during report generation: {e}")
        raise

# Utility functions
def get_genes(gene_list, custom_genes=None):
    if gene_list == 'ALSgenes':
        return open(als_gene_file).read().splitlines()
    elif gene_list == 'ACMGgenes':
        return open(acmg_gene_file).read().splitlines()
    elif gene_list == 'textboxgenes':
        # Split by comma or newline and strip whitespace
        return [gene.strip() for gene in custom_genes.replace(',', '\n').splitlines() if gene.strip()]

def get_metadata():
    return pd.read_csv(metadata_file)

def get_anno_cols():
    temp_df = pd.read_csv(variant_file, compression='gzip', nrows=5, sep='\t')
    aals_samples_from_report = set([s.replace('-b38', '') for s in temp_df.columns])
    return list(temp_df.columns[:35]), aals_samples_from_report

def get_vars_in_selected_samples(vars_df, anno_cols_from_report, samples=[]):
    if not samples:
        samples = list(set(vars_df.columns).difference(set(anno_cols_from_report)))
    condition_vars = vars_df[samples].apply(lambda x: sum([1 for e in x if e != "'0/0" and e != "'./."]), axis=1)
    return vars_df[condition_vars > 0][anno_cols_from_report + samples]

def dmg_tools(cell):
    try:
        cell = cell
        if pd.isna(cell):
            return 0
        return int(cell.split(' DMG')[0])
    except:
        return 0

def make_readme(genes_list_name, genes, combinations, anno_cols_from_report, report_title):
    SF_now = datetime.datetime.now(pytz.timezone('America/Los_Angeles'))
    SF_now_formatted = SF_now.strftime("%b %d, %Y - %I:%M%p")

    readme_text = f'AnswerALS WGS data\n\nReport title: {report_title}\n\n'
    readme_text += f'Genes: {genes_list_name}, variants in {len(genes)} genes.\n\n'
    readme_text += 'No filters on frequency were applied.\n\n'
    readme_text += '** Number of samples and variants by sheet **\n\n'

    for comb, samples in combinations.items():
        if comb != 'READ ME' and comb != 'Data dictionary':
            readme_text += f'[{comb}] '
            total_samples = combinations[comb]["data"].shape[1] - len(anno_cols_from_report)
            if 'cases' in samples.keys():
                readme_text += f'{total_samples} samples ({len(samples["cases"])} cases | {len(samples["ctrls"])} controls). {combinations[comb]["data"].shape[0]} variants.\n\n'
            else:
                readme_text += f'{total_samples} samples. {combinations[comb]["data"].shape[0]} variants.\n\n'
    
    readme_text += f'\nReport created on {SF_now_formatted} PST.\n'
    readme_text += 'Authors: Julia Kaye, Leandro Lima, Stacia Wyman\n'
    readme_text += 'For more information, please contact:\n\tTerri Thompson <terri@onpointsci.com>'

    return readme_text


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Set global font for the entire application
    font = QFont("Arial", 14)  # Adjusted font size for better readability
    app.setFont(font)

    # Set the global application icon for the taskbar
    app_icon = QIcon(resource_path('./images/logo.png'))
    app.setWindowIcon(app_icon)

    if sys.platform == "darwin":
        app.setAttribute(Qt.AA_DontUseNativeMenuBar)
    
    window = VariantReportApp()
    window.show()
    sys.exit(app.exec_())
