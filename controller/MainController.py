# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 15:08:33 2020

@author: _Xavi
"""
from . import controllers
from .CommunicationChannel import CommunicationChannel
from .MasterController import MasterController
from .presets import Preset


class MainController:
    def __init__(self, setupInfo, mainView):
        self.__setupInfo = setupInfo
        self.__mainView = mainView

        defaultPreset = Preset.getDefault(self.__mainView.presetDir)

        # Connect view signals
        self.__mainView.loadPresetButton.pressed.connect(self.loadPreset)
        self.__mainView.closing.connect(self.closeEvent)

        # Init communication channel and master controller
        self.__commChannel = CommunicationChannel(self)
        __masterController = MasterController(self.__setupInfo, self.__commChannel)

        # List of Controllers for the GUI Widgets
        self.__factory = controllers.WidgetControllerFactory(
            self.__setupInfo, defaultPreset, self.__commChannel, __masterController
        )

        self.imageController = self.__factory.createController(controllers.ImageController, self.__mainView.imageWidget)
        self.positionerController = self.__factory.createController(controllers.PositionerController, self.__mainView.positionerWidget)
        self.scanController = self.__factory.createController(controllers.ScanController, self.__mainView.scanWidget)
        self.laserController = self.__factory.createController(controllers.LaserController, self.__mainView.laserWidgets)
        self.recorderController = self.__factory.createController(controllers.RecorderController, self.__mainView.recordingWidget)
        self.viewController = self.__factory.createController(controllers.ViewController, self.__mainView.viewWidget)
        self.settingsController = self.__factory.createController(controllers.SettingsController, self.__mainView.settingsWidget)

        if self.__setupInfo.availableWidgets.BeadRecWidget:
            self.beadController = self.__factory.createController(controllers.BeadController, self.__mainView.beadRecWidget)

        if self.__setupInfo.availableWidgets.ULensesWidget:
            self.uLensesController = self.__factory.createController(controllers.ULensesController, self.__mainView.ulensesWidget)

        if self.__setupInfo.availableWidgets.AlignWidgetXY:
            self.alignXYController = self.__factory.createController(controllers.AlignXYController, self.__mainView.alignWidgetXY)

        if self.__setupInfo.availableWidgets.AlignWidgetAverage:
            self.alignAverageController = self.__factory.createController(controllers.AlignAverageController, self.__mainView.alignWidgetAverage)

        if self.__setupInfo.availableWidgets.AlignmentLineWidget:
            self.alignmentLineController = self.__factory.createController(controllers.AlignmentLineController, self.__mainView.alignmentLineWidget)

        if self.__setupInfo.availableWidgets.FFTWidget:
            self.fftController = self.__factory.createController(controllers.FFTController, self.__mainView.fftWidget)

        self.__mainView.setDetectorRelatedDocksVisible(
            __masterController.detectorsManager.hasDetectors()
        )

        # Check widget compatibility
        __masterController.scanManager._parameterCompatibility(self.scanController.parameterDict)

    def loadPreset(self):
        self.__factory.loadPresetForAllCreatedControllers(
            self.__mainView.presetDir, self.__mainView.presetsMenu.currentText()
        )

    def closeEvent(self):
        self.__factory.closeAllCreatedControllers()
