# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CompressRaster
                                 A QGIS plugin
 Tool to compress raster files
                              -------------------
        begin                : 2024
        git sha              : $Format:%H$
        copyright            : (C) 2024 by Damaris Toledo
        email                : sdamaristc@gmail.com
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
import os.path
from .compress_raster_dialog import CompressRasterDialog


class CompressRaster:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr(u'&Compress Raster')
        self.toolbar = self.iface.addToolBar(u'CompressRaster')
        self.toolbar.setObjectName(u'CompressRaster')
        self.first_start = None

    def tr(self, message):
        """Get the translation for a string using Qt translation API."""
        return QCoreApplication.translate('CompressRaster', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar."""

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'Compress Raster'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.first_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Compress Raster'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        if self.first_start == True:
            self.first_start = False
            self.dlg = CompressRasterDialog()

        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            pass
