import pyqtgraph as pg
from qtpy import QtCore, QtWidgets

from imswitch.imcontrol.view import guitools as guitools
from imswitch.imcommon.model import initLogger
from .basewidgets import Widget


class ScanWidget(Widget):
    """ Widget containing scanner interface and beadscan reconstruction.
            This class uses the classes GraphFrame, MultipleScanWidget and IllumImageWidget"""

    sigSaveScanClicked = QtCore.Signal()
    sigLoadScanClicked = QtCore.Signal()
    sigRunScanClicked = QtCore.Signal()
    sigSeqTimeParChanged = QtCore.Signal()
    sigStageParChanged = QtCore.Signal()
    sigSignalParChanged = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        self.__logger = initLogger(self, instanceName='ScanWidget')
        super().__init__(*args, **kwargs)

        self.setMinimumHeight(200)

        self.scanInLiveviewWar = QtWidgets.QMessageBox()
        self.scanInLiveviewWar.setInformativeText(
            "You need to be in liveview to scan")

        self.digModWarning = QtWidgets.QMessageBox()
        self.digModWarning.setInformativeText(
            "You need to be in digital laser modulation and external "
            "frame-trigger acquisition mode")

        self.saveScanBtn = guitools.BetterPushButton('Save Scan')
        self.loadScanBtn = guitools.BetterPushButton('Load Scan')

        self.seqTimePar = QtWidgets.QLineEdit('0.02')  # ms
        self.phaseDelayPar = QtWidgets.QLineEdit('100')  # samples
        #self.extraLaserOnPar = QtWidgets.QLineEdit('10')  # samples
        self.nrFramesPar = QtWidgets.QLabel()
        self.scanDuration = 0
        self.scanDurationLabel = QtWidgets.QLabel(str(self.scanDuration))

        self.scanDims = []

        self.scanPar = {
                        'seqTime': self.seqTimePar,  # TODO: change name to dwellTime, both label and parameter?
                        'phaseDelay': self.phaseDelayPar
                        }

        self.ttlParameters = {}

        self.scanButton = guitools.BetterPushButton('Run Scan')

        self.repeatBox = QtWidgets.QCheckBox('Repeat')

        #self.graph = GraphFrame()
        #self.graph.setEnabled(False)
        #self.graph.setFixedHeight(128)

        self.scrollContainer = QtWidgets.QGridLayout()
        self.scrollContainer.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.scrollContainer)

        self.grid = QtWidgets.QGridLayout()
        self.gridContainer = QtWidgets.QWidget()
        self.gridContainer.setLayout(self.grid)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidget(self.gridContainer)
        self.scrollArea.setWidgetResizable(True)
        self.scrollContainer.addWidget(self.scrollArea)
        self.gridContainer.installEventFilter(self)

        # Connect signals
        self.saveScanBtn.clicked.connect(self.sigSaveScanClicked)
        self.loadScanBtn.clicked.connect(self.sigLoadScanClicked)
        self.scanButton.clicked.connect(self.sigRunScanClicked)
        self.seqTimePar.textChanged.connect(self.sigSeqTimeParChanged)
        self.phaseDelayPar.textChanged.connect(self.sigStageParChanged)
        #self.extraLaserOnPar.textChanged.connect(self.sigStageParChanged)  # for debugging

    def initControls(self, positionerNames, TTLDeviceNames):
        currentRow = 0
        self.scanDims = list(positionerNames)
        self.__logger.debug(positionerNames)
        self.__logger.debug(type(positionerNames))
        self.scanDims.append('None')

        # Add general buttons
        self.grid.addWidget(self.loadScanBtn, currentRow, 0)
        self.grid.addWidget(self.saveScanBtn, currentRow, 1)
        self.grid.addItem(
            QtWidgets.QSpacerItem(40, 20,
                                  QtWidgets.QSizePolicy.Expanding,
                                  QtWidgets.QSizePolicy.Minimum),
            currentRow, 2, 1, 3
        )
        self.grid.addWidget(self.repeatBox, currentRow, 5)
        self.grid.addWidget(self.scanButton, currentRow, 6)
        currentRow += 1

        # Add space item to make the grid look nicer
        self.grid.addItem(
            QtWidgets.QSpacerItem(20, 40,
                                  QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Expanding),
            currentRow, 0, 1, -1
        )
        currentRow += 1

        # Add param labels
        sizeLabel = QtWidgets.QLabel('Size (µm)')
        stepLabel = QtWidgets.QLabel('Step size (µm)')
        pixelsLabel = QtWidgets.QLabel('Pixels (#)')
        centerLabel = QtWidgets.QLabel('Center (µm)')
        scandimLabel = QtWidgets.QLabel('Scan dim')
        sizeLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        stepLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        pixelsLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        centerLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        scandimLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(sizeLabel, currentRow, 1)
        self.grid.addWidget(stepLabel, currentRow, 2)
        self.grid.addWidget(pixelsLabel, currentRow, 3)
        self.grid.addWidget(centerLabel, currentRow, 4)
        self.grid.addWidget(scandimLabel, currentRow, 6)
        currentRow += 1

        for index, positionerName in enumerate(positionerNames):
            # Scan params
            sizePar = QtWidgets.QLineEdit('5')
            self.scanPar['size' + positionerName] = sizePar
            stepSizePar = QtWidgets.QLineEdit('0.1')
            self.scanPar['stepSize' + positionerName] = stepSizePar
            numPixelsPar = QtWidgets.QLineEdit('50')
            numPixelsPar.setEnabled(False)
            self.scanPar['pixels' + positionerName] = numPixelsPar
            centerPar = QtWidgets.QLineEdit('0')
            self.scanPar['center' + positionerName] = centerPar
            self.grid.addWidget(QtWidgets.QLabel(positionerName), currentRow, 0)
            self.grid.addWidget(sizePar, currentRow, 1)
            self.grid.addWidget(stepSizePar, currentRow, 2)
            self.grid.addWidget(numPixelsPar, currentRow, 3)
            self.grid.addWidget(centerPar, currentRow, 4)

            # Scan dimension label and picker
            dimlabel = QtWidgets.QLabel(
                f'{index + 1}{guitools.ordinalSuffix(index + 1)} dimension:'
            )
            dimlabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.grid.addWidget(dimlabel, currentRow, 5)
            scanDimPar = QtWidgets.QComboBox()
            scanDimPar.addItems(self.scanDims)
            scanDimPar.setCurrentIndex(index if index < 2 else self.scanDims.index('None'))
            self.scanPar['scanDim' + str(index)] = scanDimPar
            self.grid.addWidget(scanDimPar, currentRow, 6)

            currentRow += 1

            # Connect signals
            self.scanPar['size' + positionerName].textChanged.connect(self.sigStageParChanged)
            self.scanPar['stepSize' + positionerName].textChanged.connect(self.sigStageParChanged)
            self.scanPar['pixels' + positionerName].textChanged.connect(self.sigStageParChanged)
            self.scanPar['center' + positionerName].textChanged.connect(self.sigStageParChanged)
            self.scanPar['scanDim' + str(index)].currentIndexChanged.connect(
                self.sigStageParChanged
            )

        currentRow += 1

        # Add dwell time parameter
        self.grid.addWidget(QtWidgets.QLabel('Dwell (ms):'), currentRow, 5)
        self.grid.addWidget(self.seqTimePar, currentRow, 6)

        currentRow += 1
        
        # Add detection phase delay parameter
        self.grid.addWidget(QtWidgets.QLabel('Phase delay (samples):'), currentRow, 5)
        self.grid.addWidget(self.phaseDelayPar, currentRow, 6)

        #currentRow += 1
        
        # Add detection phase delay parameter
        #self.grid.addWidget(QtWidgets.QLabel('Extra laser on (samples):'), currentRow, 5)
        #self.grid.addWidget(self.extraLaserOnPar, currentRow, 6)

        # Add space item to make the grid look nicer
        self.grid.addItem(
            QtWidgets.QSpacerItem(20, 40,
                                  QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding),
            currentRow, 0, 1, -1
        )
        currentRow += 1
        graphRow = currentRow

        # TTL param labels
        sequenceLabel = QtWidgets.QLabel('Sequence (h#,l#,...)')
        sequenceLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(sequenceLabel, currentRow, 1)
        sequenceAxisLabel = QtWidgets.QLabel('Axis')
        sequenceAxisLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.grid.addWidget(sequenceAxisLabel, currentRow, 2)
        currentRow += 1

        for deviceName in TTLDeviceNames:
            # TTL sequence param
            self.grid.addWidget(QtWidgets.QLabel(deviceName), currentRow, 0)
            self.ttlParameters['seq' + deviceName] = QtWidgets.QLineEdit('l1')
            self.grid.addWidget(self.ttlParameters['seq' + deviceName], currentRow, 1)

            # TTL sequence axis param
            ttlAxisPar = QtWidgets.QComboBox()
            ttlAxisPar.addItems(self.scanDims)
            ttlAxisPar.setCurrentIndex(self.scanDims.index('None'))
            self.ttlParameters['seqAxis' + deviceName] = ttlAxisPar
            self.grid.addWidget(ttlAxisPar, currentRow, 2)

            currentRow += 1

            # Connect signals
            self.ttlParameters['seq' + deviceName].textChanged.connect(self.sigSignalParChanged)
            self.ttlParameters['seqAxis' + deviceName].currentIndexChanged.connect(self.sigSignalParChanged)

        ## Add pulse graph
        #self.grid.addWidget(self.graph, graphRow, 3, currentRow - graphRow, 5)

    def repeatEnabled(self):
        return self.repeatBox.isChecked()

    def getScanDim(self, index):
        return self.scanPar['scanDim' + str(index)].currentText()

    def getScanSize(self, positionerName):
        return float(self.scanPar['size' + positionerName].text())

    def getScanStepSize(self, positionerName):
        return float(self.scanPar['stepSize' + positionerName].text())

    def getScanCenterPos(self, positionerName):
        return float(self.scanPar['center' + positionerName].text())

    def getTTLIncluded(self, deviceName):
        return (self.ttlParameters['seq' + deviceName].text() != '')

    def getTTLSequence(self, deviceName):
        #return list(map(lambda s: s if s else None, self.ttlParameters['seq' + deviceName].text().split(',')))
        return self.ttlParameters['seq' + deviceName].text()

    def getTTLSequenceAxis(self, deviceName):
        if self.ttlParameters['seqAxis' + deviceName].currentText() == 'None':
            return 'None'
        return self.ttlParameters['seqAxis' + deviceName].currentText()
        #for index, scanDim in enumerate(self.scanDims):
        #    if self.ttlParameters['seqAxis' + deviceName].currentText() == scanDim:
        #        return index

    def getSeqTimePar(self):
        return float(self.seqTimePar.text()) / 1000

    def getPhaseDelayPar(self):
        return float(self.phaseDelayPar.text())

    #def getExtraLaserOnPar(self):
    #    return float(self.extraLaserOnPar.text())

    def setRepeatEnabled(self, enabled):
        self.repeatBox.setChecked(enabled)

    def setScanButtonChecked(self, checked):
        self.scanButton.setEnabled(not checked)
        self.scanButton.setCheckable(checked)
        self.scanButton.setChecked(checked)

    def setScanDim(self, index, positionerName):
        scanDimPar = self.scanPar['scanDim' + str(index)]
        scanDimPar.setCurrentIndex(scanDimPar.findText(positionerName))

    def setScanSize(self, positionerName, size):
        self.scanPar['size' + positionerName].setText(str(round(size, 3)))

    def setScanStepSize(self, positionerName, stepSize):
        self.scanPar['stepSize' + positionerName].setText(str(round(stepSize, 3)))

    def setScanCenterPos(self, positionerName, centerPos):
        self.scanPar['center' + positionerName].setText(str(round(centerPos, 3)))

    def setScanPixels(self, positionerName, pixels):
        txt = str(pixels) if pixels > 1 else '-'
        self.scanPar['pixels' + positionerName].setText(txt)

    def setTTLSequences(self, deviceName, sequence):
        self.ttlParameters['seq' + deviceName].setText(
            ','.join(map(lambda s: str(s), sequence))
        )

    def unsetTTL(self, deviceName):
        self.ttlParameters['seq' + deviceName].setText('')

    def setSeqTimePar(self, seqTimePar):
        self.seqTimePar.setText(str(round(float(1000 * seqTimePar), 3)))

    def setPhaseDelayPar(self, phaseDelayPar):
        self.phaseDelayPar.setText(str(round(int(phaseDelayPar))))

    def setScanDimEnabled(self, index, enabled):
        self.scanPar['scanDim' + str(index)].setEnabled(enabled)

    def setScanSizeEnabled(self, positionerName, enabled):
        self.scanPar['size' + positionerName].setEnabled(enabled)

    def setScanStepSizeEnabled(self, positionerName, enabled):
        self.scanPar['stepSize' + positionerName].setEnabled(enabled)

    def setScanCenterPosEnabled(self, positionerName, enabled):
        self.scanPar['center' + positionerName].setEnabled(enabled)

    #def plotSignalGraph(self, x, signals, colors, unit=None):
    #    if len(x) != len(signals) or len(signals) != len(colors):
    #        raise ValueError('Arguments "areas", "signals" and "colors" must be of equal length')
    #
    #    self.graph.plot.clear()
    #    for i in range(len(x)):
    #        self.graph.plot.plot(x[i], signals[i] * (1 + i / 20), pen=pg.mkPen(colors[i]))
    #
    #    self.graph.plot.setYRange(-0.1, 1 + len(x) / 20 + 0.05)
    #    #self.graph.plot.setLabel('bottom',f'Axis steps ({unit})')
    #    self.graph.plot.setLabel('bottom','Selected sequence axis steps')

    def eventFilter(self, source, event):
        if source is self.gridContainer and event.type() == QtCore.QEvent.Resize:
            # Set correct minimum width (otherwise things can go outside the widget because of the
            # scroll area)
            width = self.gridContainer.minimumSizeHint().width() \
                    + self.scrollArea.verticalScrollBar().width()
            self.scrollArea.setMinimumWidth(width)
            self.setMinimumWidth(width)

        return False


class GraphFrame(pg.GraphicsLayoutWidget):
    """Creates the plot that plots the preview of the pulses."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot = self.addPlot(row=1, col=0)


# Copyright (C) 2020-2021 ImSwitch developers
# This file is part of ImSwitch.
#
# ImSwitch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ImSwitch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
