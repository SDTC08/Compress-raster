# Compress Raster - QGIS Plugin

QGIS plugin to compress raster files using high-efficiency DEFLATE compression algorithms.

**Author:** Damaris Toledo  
**Email:** sdamaristc@gmail.com  
**Organization:** Escuela Peruana del Agua (EPAGUA)

---

## 🎯 Features

- ✅ Optimized DEFLATE compression (adjustable ZLEVEL 1-9)
- ✅ Individual file selection with QGIS-style interface
- ✅ Customizable output folder
- ✅ Real-time statistics panel
- ✅ Batch processing with progress bar
- ✅ Advanced parameters: PREDICTOR=2, TILED=YES, BIGTIFF, NUM_THREADS

## 📦 Installation

1. Download `compress_raster.zip`
2. In QGIS: **Plugins → Manage and Install Plugins → Install from ZIP**
3. Select the downloaded file
4. Activate the plugin in the "Installed" tab

## 🚀 Usage

1. **Select files**: Use the "..." button to choose raster files (.tif, .tiff, .img, .asc)
2. **Add to list**: Click "Add to list" (you can repeat to add more files)
3. **Output folder**: Use the "..." button to select where to save compressed files
4. **Compression level**: Adjust between 1 (fast) and 9 (maximum compression)
5. **Compress**: Click "Compress files" and wait for results

## ⚙️ Compression Parameters

```
COMPRESS=DEFLATE        # Lossless algorithm
ZLEVEL=9                # Adjustable level (default maximum)
PREDICTOR=2             # Optimization for continuous data
TILED=YES               # Improves performance
BIGTIFF=IF_SAFER        # Automatic support >4GB
NUM_THREADS=ALL_CPUS    # Multiprocessing
```

## 📊 Expected Results

- **DEMs**: 40-70% reduction
- **Thematic maps**: 50-80% reduction
- **Classifications**: 60-90% reduction
- **Orthophotos (DEFLATE)**: 10-30% reduction

## 📂 Output Files

Compressed files are saved with the suffix `_compressed.tif`:

```
DEM_original.tif → DEM_original_compressed.tif
```

## 🔧 Requirements

- QGIS 3.0 or higher
- GDAL (included with QGIS)

## 📝 License

GNU General Public License v2.0 or later

## 💬 Contact

**Damaris Toledo**  
Email: sdamaristc@gmail.com  
Organization: Escuela Peruana del Agua (EPAGUA)  
Web: https://epagua.edu.pe

## 🙏 Acknowledgments

Developed for Escuela Peruana del Agua (EPAGUA).
