# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CompressRasterDialog
                                 A QGIS plugin
 Tool to compress raster files
                             -------------------
        begin                : 2024
        copyright            : (C) 2024 by Damaris Toledo
        email                : sdamaristc@gmail.com
 ***************************************************************************/
"""

import os
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox
from qgis.core import QgsMessageLog, Qgis
from osgeo import gdal

# Load UI file
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'compress_raster_dialog_base.ui'))


class WorkerThread(QThread):
    """Thread for background compression processing"""
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    status = pyqtSignal(str)
    
    def __init__(self, files, output_folder, zlevel):
        QThread.__init__(self)
        self.files = files
        self.output_folder = output_folder
        self.zlevel = zlevel
        self.results = []
        
    def run(self):
        """Execute compression"""
        total = len(self.files)
        
        for i, file_path in enumerate(self.files):
            filename = os.path.basename(file_path)
            self.status.emit(f"Processing {i+1} of {total}: {filename}")
            
            try:
                # Open raster with GDAL
                src_ds = gdal.Open(file_path)
                if src_ds is None:
                    raise Exception("Could not open file")
                
                # Create output filename
                base_name = os.path.splitext(filename)[0]
                output_file = os.path.join(self.output_folder, f"{base_name}_compressed.tif")
                
                # Compression options
                options = [
                    'COMPRESS=DEFLATE',
                    f'ZLEVEL={self.zlevel}',
                    'PREDICTOR=2',
                    'TILED=YES',
                    'BIGTIFF=IF_SAFER',
                    'NUM_THREADS=ALL_CPUS'
                ]
                
                # Copy with compression
                gdal.Translate(output_file, src_ds, 
                              creationOptions=options)
                
                # Close dataset
                src_ds = None
                
                # Calculate sizes
                original_size = os.path.getsize(file_path) / (1024 * 1024)
                final_size = os.path.getsize(output_file) / (1024 * 1024)
                reduction = ((original_size - final_size) / original_size) * 100
                saved = original_size - final_size
                
                result = {
                    'file': filename,
                    'original_size': original_size,
                    'final_size': final_size,
                    'reduction': reduction,
                    'saved': saved,
                    'success': True,
                    'message': 'Successfully compressed'
                }
                
            except Exception as e:
                result = {
                    'file': filename,
                    'success': False,
                    'message': f'Error: {str(e)}'
                }
            
            self.results.append(result)
            self.progress.emit(int((i + 1) / total * 100))
        
        self.finished.emit(self.results)


class CompressRasterDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(CompressRasterDialog, self).__init__(parent)
        self.setupUi(self)
        
        # Variables
        self.selected_files = []
        self.output_folder = None
        self.worker = None
        
        # Connect signals
        self.btn_select_files.clicked.connect(self.select_files)
        self.btn_add.clicked.connect(self.add_files)
        self.btn_output_folder.clicked.connect(self.select_output_folder)
        self.btn_clear.clicked.connect(self.clear_list)
        self.btn_compress.clicked.connect(self.compress_files)
        
        # Disable compress button initially
        self.btn_compress.setEnabled(False)
        
    def select_files(self):
        """Select raster files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select raster files",
            "",
            "Raster Files (*.tif *.tiff *.img *.asc);;All files (*.*)"
        )
        
        if files:
            # Display in text field
            if len(files) == 1:
                self.txt_files_input.setText(files[0])
            else:
                self.txt_files_input.setText(f"{len(files)} files selected")
            
            # Store temporarily for adding
            self.temp_files = files
            
    def add_files(self):
        """Add files from widget to list"""
        if hasattr(self, 'temp_files') and self.temp_files:
            # Add files to list (avoid duplicates)
            for file in self.temp_files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
            
            self.update_file_list()
            self.check_ready_to_compress()
            
            # Clear temp field
            self.txt_files_input.clear()
            self.temp_files = []
            
    def select_output_folder(self):
        """Select output folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select output folder",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.output_folder = folder
            self.txt_output_folder.setText(folder)
            self.check_ready_to_compress()
            
    def clear_list(self):
        """Clear file list"""
        self.selected_files = []
        self.update_file_list()
        self.check_ready_to_compress()
        
    def update_file_list(self):
        """Update file list in interface"""
        self.list_files.clear()
        
        total_size = 0
        for file in self.selected_files:
            name = os.path.basename(file)
            size = os.path.getsize(file) / (1024 * 1024)  # MB
            total_size += size
            
            item_text = f"{name} ({size:.2f} MB)"
            self.list_files.addItem(item_text)
        
        # Update summary label
        if self.selected_files:
            self.lbl_files.setText(
                f"{len(self.selected_files)} file(s) - Total size: {total_size:.2f} MB"
            )
        else:
            self.lbl_files.setText("No files selected")
            
    def check_ready_to_compress(self):
        """Check if compress button can be enabled"""
        ready = (len(self.selected_files) > 0 and 
                self.output_folder is not None)
        self.btn_compress.setEnabled(ready)
        
    def compress_files(self):
        """Start file compression"""
        if not self.selected_files or not self.output_folder:
            return
        
        # Disable buttons
        self.btn_compress.setEnabled(False)
        self.btn_select_files.setEnabled(False)
        self.btn_add.setEnabled(False)
        self.btn_output_folder.setEnabled(False)
        self.btn_clear.setEnabled(False)
        
        # Clear results area
        self.txt_log.clear()
        self.txt_log.append("Starting compression...\n")
        
        # Get compression level
        zlevel = self.spin_zlevel.value()
        
        # Create and configure worker thread
        self.worker = WorkerThread(
            self.selected_files,
            self.output_folder,
            zlevel
        )
        
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.compression_finished)
        
        # Start worker
        self.worker.start()
        
    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        
    def update_status(self, message):
        """Update current status"""
        self.lbl_status.setText(message)
        
    def compression_finished(self, results):
        """Process compression results"""
        # Enable buttons
        self.btn_compress.setEnabled(True)
        self.btn_select_files.setEnabled(True)
        self.btn_add.setEnabled(True)
        self.btn_output_folder.setEnabled(True)
        self.btn_clear.setEnabled(True)
        
        # Show results
        self.txt_log.append("\n" + "="*60)
        self.txt_log.append("COMPRESSION RESULTS")
        self.txt_log.append("="*60 + "\n")
        
        # Calculate totals
        successful = sum(1 for r in results if r['success'])
        
        if successful > 0:
            total_original = sum(r['original_size'] for r in results if r['success'])
            total_final = sum(r['final_size'] for r in results if r['success'])
            total_reduction = ((total_original - total_final) / total_original) * 100
            total_saved = total_original - total_final
            
            # General summary
            self.txt_log.append(f"Files processed: {successful} of {len(results)}")
            self.txt_log.append(f"Total original size: {total_original:.2f} MB")
            self.txt_log.append(f"Total final size: {total_final:.2f} MB")
            self.txt_log.append(f"Average reduction: {total_reduction:.1f}%")
            self.txt_log.append(f"Total saved: {total_saved:.2f} MB\n")
            self.txt_log.append("-"*60 + "\n")
            
            # Update statistics in interface
            self.update_statistics(successful, len(results), 
                                 total_original, total_final,
                                 total_reduction, total_saved)
        
        # Detail per file
        self.txt_log.append("Detail per file:\n")
        for i, r in enumerate(results, 1):
            if r['success']:
                self.txt_log.append(
                    f"{i}. {r['file']}\n"
                    f"   {r['original_size']:.2f} MB → {r['final_size']:.2f} MB "
                    f"(-{r['reduction']:.1f}%) | Saved: {r['saved']:.2f} MB\n"
                )
            else:
                self.txt_log.append(
                    f"{i}. {r['file']}\n"
                    f"   {r['message']}\n"
                )
        
        self.txt_log.append("="*60)
        self.txt_log.append("COMPRESSION COMPLETED")
        self.txt_log.append("="*60)
        
        self.lbl_status.setText("Compression completed")
        self.progress_bar.setValue(100)
        
        # Show message
        QMessageBox.information(
            self,
            "Compression completed",
            f"Successfully processed {successful} of {len(results)} files.\n"
            f"Total saved: {total_saved:.2f} MB ({total_reduction:.1f}%)"
        )
        
    def update_statistics(self, successful, total, orig, final, reduction, saved):
        """Update statistics panel"""
        self.lbl_stat_files.setText(f"{successful} / {total}")
        self.lbl_stat_original.setText(f"{orig:.2f} MB")
        self.lbl_stat_final.setText(f"{final:.2f} MB")
        self.lbl_stat_reduction.setText(f"{reduction:.1f}%")
        self.lbl_stat_saved.setText(f"{saved:.2f} MB")
