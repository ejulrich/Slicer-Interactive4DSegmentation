import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

#
# Segment4D
#

class Segment4D(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Segment4D" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Segmentation"]
    self.parent.dependencies = []
    self.parent.contributors = ["Ethan Ulrich (University of Iowa)"]
    self.parent.helpText = """TODO"""
    self.parent.acknowledgementText = """TODO""" # replace with organization, grant and thanks.

#
# Segment4DWidget
#

class Segment4DWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Format Scene Area
    #
    loadGroupBox = ctk.ctkCollapsibleGroupBox()
    loadGroupBox.setTitle('Sequence Data')
    self.layout.addWidget(loadGroupBox)
    loadGroupBoxLayout = qt.QFormLayout(loadGroupBox)
    
    self.volumeSequenceComboBox = slicer.qMRMLNodeComboBox()
    self.volumeSequenceComboBox.nodeTypes = ( ("vtkMRMLSequenceNode"), "" )
    self.volumeSequenceComboBox.setMRMLScene( slicer.mrmlScene )
    self.volumeSequenceComboBox.noneEnabled = False
    loadGroupBoxLayout.addRow('Volume Sequence: ',self.volumeSequenceComboBox)
    
    self.transformSequenceComboBox = slicer.qMRMLNodeComboBox()
    self.transformSequenceComboBox.nodeTypes = ( ("vtkMRMLSequenceNode"), "" )
    self.transformSequenceComboBox.selectNodeUponCreation = False
    self.transformSequenceComboBox.setMRMLScene( slicer.mrmlScene )
    self.transformSequenceComboBox.noneEnabled = True
    loadGroupBoxLayout.addRow('Transform Sequence: ',self.transformSequenceComboBox)
    
    self.labelSequenceComboBox = slicer.qMRMLNodeComboBox()
    self.labelSequenceComboBox.nodeTypes = ( ("vtkMRMLSequenceNode"), "" )
    self.labelSequenceComboBox.selectNodeUponCreation = False
    self.labelSequenceComboBox.setMRMLScene( slicer.mrmlScene )
    self.labelSequenceComboBox.noneEnabled = True
    loadGroupBoxLayout.addRow('Label Sequence: ',self.labelSequenceComboBox)
    
    sliceButtonsLayout = qt.QHBoxLayout()
    loadGroupBoxLayout.addRow('Slice Views: ',sliceButtonsLayout)
    self.axialCheckbox = qt.QCheckBox('Axial')
    self.axialCheckbox.checked = True
    sliceButtonsLayout.addWidget(self.axialCheckbox)
    self.sagittalCheckBox = qt.QCheckBox('Sagittal')
    self.sagittalCheckBox.checked = True
    sliceButtonsLayout.addWidget(self.sagittalCheckBox)
    self.coronalCheckBox = qt.QCheckBox('Coronal')
    self.coronalCheckBox.checked = False
    sliceButtonsLayout.addWidget(self.coronalCheckBox)
    
    formatSceneButton = qt.QPushButton('Format Scene')
    loadGroupBoxLayout.addRow('',formatSceneButton)
    
    #
    # Editor Widget
    #
    editorWidget = slicer.modules.editor.widgetRepresentation().self()
    self.labelEditor = editorWidget.editLabelMapsFrame
    self.layout.addWidget(self.labelEditor)
    self.labelEditor.collapsed = False
    
    
    # add vertical spacer
    self.layout.addStretch(1)
    
    #
    # Format Scene Widget
    #
    self.formatSceneWidget = slicer.qMRMLWidget()
    self.formatSceneWidget.setWindowTitle('Format Scene View')
    self.formatSceneWidgetLayout = qt.QGridLayout(self.formatSceneWidget)
    nodeSelectionRegion = qt.QGroupBox()
    self.formatSceneWidgetLayout.addWidget(nodeSelectionRegion,1,1,4,1)
    nodeSelectionRegion.setTitle('Data Selection')
    nodeSelectionLayout = qt.QVBoxLayout(nodeSelectionRegion)
    volumeSelectionLabel = qt.QLabel('Volume Data')
    nodeSelectionLayout.addWidget(volumeSelectionLabel)
    volumeSelectionList = slicer.qMRMLListWidget()
    nodeSelectionLayout.addWidget(volumeSelectionList)
    
    transformSelectionLabel = qt.QLabel('Transforms')
    nodeSelectionLayout.addWidget(transformSelectionLabel)
    transformSelectionList = slicer.qMRMLListWidget()
    nodeSelectionLayout.addWidget(transformSelectionList)
    
    addToSceneArrow = ctk.ctkPushButton()
    self.formatSceneWidgetLayout.addWidget(addToSceneArrow,2,2,1,1)
    removeFromSceneArrow = ctk.ctkPushButton()
    self.formatSceneWidgetLayout.addWidget(removeFromSceneArrow,3,2,1,1)
    
    organizeSceneRegion = qt.QGroupBox()
    self.formatSceneWidgetLayout.addWidget(organizeSceneRegion,1,3,4,5)
    organizeSceneRegion.setTitle('Scene Format')
    self.organizeSceneRegionLayout = qt.QGridLayout(organizeSceneRegion)
    self.backgroundSceneButtons = []
    backgroundVolumeBox = qt.QPushButton('Background')
    backgroundVolumeBox.setCheckable(True)
    #backgroundVolumeBox.connect('toggled(bool)',self.testClick)
    
    self.organizeSceneRegionLayout.addWidget(backgroundVolumeBox,1,1,1,1)
    self.backgroundSceneButtons.append(backgroundVolumeBox)
    
    self.foregroundSceneButtons = []
    foregroundVolumeBox = qt.QPushButton('Foreground')
    foregroundVolumeBox.setCheckable(True)
    self.organizeSceneRegionLayout.addWidget(foregroundVolumeBox,2,1,1,1)
    #foregroundVolumeBox.connect('toggled(bool)',self.testClick)
    backgroundVolumeBox.connect('clicked()',lambda i=1: self.backgroundButtonClicked(i))
    foregroundVolumeBox.connect('clicked()',lambda i=1: self.foregroundButtonClicked(i))
    
    self.backgroundSceneButtons.append(backgroundVolumeBox)
    self.foregroundSceneButtons.append(foregroundVolumeBox)
    #self.backgroundSceneButtons[0].connect('clicked(bool)', self.backgroundButtonClicked(1))
    #self.foregroundSceneButtons[0].connect('clicked(bool)', self.foregroundButtonClicked(1))
    
    self.addColumnButton = qt.QPushButton('+Add')
    self.organizeSceneRegionLayout.addWidget(self.addColumnButton,1,2,1,1)
    self.sceneColumns = 1
    
    loadFormattedSceneButton = qt.QPushButton('Load Scene')
    self.formatSceneWidgetLayout.addWidget(loadFormattedSceneButton,5,8,1,1)
    

    # connections
    formatSceneButton.connect('clicked(bool)', self.onFormatSceneButtonClicked)
    self.addColumnButton.connect('clicked(bool)', self.onAddColumn)
    #self.formatSceneWidget.connect(')
    
    # change view layout
    #layoutManager = slicer.app.layoutManager()
    #layoutManager.setLayout(33) # 3x3 layout

  def cleanup(self):
    for b in self.backgroundSceneButtons:
      b.disconnect('clicked(bool)')
    for b in self.foregroundSceneButtons:
      b.disconnect('clicked(bool)')
    self.backgroundSceneButtons = []
    self.foregroundSceneButtons = []

  def onFormatSceneButtonClicked(self):
    numRows = 0
    for checkBox in [self.axialCheckbox, self.sagittalCheckBox, self.coronalCheckBox]:
      if checkBox.checked:
        numRows += 1
    volumeSequenceNode = self.volumeSequenceComboBox.currentNode()
    numColumns = volumeSequenceNode.GetNumberOfDataNodes()

    # TODO support all possible views
    layoutManager = slicer.app.layoutManager()
    if [numRows,numColumns]==[1,1]:
      layoutManager.setLayout(6) # Red Slice view only
    elif [numRows,numColumns]==[1,2]:
      layoutManager.setLayout(29)
    elif [numRows,numColumns]==[2,2]:
      layoutManager.setLayout(27)
    elif [numRows,numColumns]==[2,3]:
      layoutManager.setLayout(21)
    elif [numRows,numColumns]==[2,4]:
      layoutManager.setLayout(31)
    elif [numRows,numColumns]==[3,3]:
      layoutManager.setLayout(33)
    elif [numRows,numColumns]==[3,4]:
      layoutManager.setLayout(30)
    else:
      slicer.util.errorDisplay(str(numRows)+'x'+str(numColumns)+' currently not implemented')

  def onLoadSceneButtonClicked(self):
    self.formatSceneWidget.show()

  def onAddColumn(self):
    self.sceneColumns += 1
    colIdx = self.sceneColumns
    self.organizeSceneRegionLayout.addWidget(self.addColumnButton,1,1+colIdx,1,1)
    
    backgroundVolumeBox = qt.QPushButton('Background')
    self.organizeSceneRegionLayout.addWidget(backgroundVolumeBox,1,colIdx,1,1)
    backgroundVolumeBox.setCheckable(True)
    #backgroundVolumeBox.connect('toggled(bool)',self.testClick)
    backgroundVolumeBox.connect('clicked()',lambda i=colIdx: self.backgroundButtonClicked(i))
    self.backgroundSceneButtons.append(backgroundVolumeBox)
  #self.backgroundSceneButtons[self.sceneColumns-1].connect('clicked(bool)',self.backgroundButtonClicked(self.sceneColumns))

    foregroundVolumeBox = qt.QPushButton('Foreground')
    self.organizeSceneRegionLayout.addWidget(foregroundVolumeBox,2,colIdx,1,1)
    foregroundVolumeBox.setCheckable(True)
    #foregroundVolumeBox.connect('toggled(bool)',self.testClick)
    foregroundVolumeBox.connect('clicked()',lambda i=colIdx: self.foregroundButtonClicked(i))
    self.foregroundSceneButtons.append(foregroundVolumeBox)
  #self.foregroundSceneButtons[self.sceneColumns-1].connect('clicked(bool)',self.foregroundButtonClicked(self.sceneColumns))
    
    removeButton = qt.QPushButton('Remove')
    self.organizeSceneRegionLayout.addWidget(removeButton,3,colIdx,1,1)

  def backgroundButtonClicked(self,colNum):
    print 'backgroundButtonClicked('+str(colNum)+')'
    for b in self.backgroundSceneButtons:
      idx = self.backgroundSceneButtons.index(b)+1
      if idx == colNum:
        b.disconnect('clicked()')
      else:
        b.disconnect('clicked()')
        b.checked = False
        b.connect('clicked()',lambda i=idx: self.backgroundButtonClicked(i))
    for b in self.foregroundSceneButtons:
      idx = self.foregroundSceneButtons.index(b)+1
      b.disconnect('clicked()')
      b.checked = False
      b.connect('clicked()',lambda i=idx: self.foregroundButtonClicked(i))
    #slicer.util.errorDisplay('yes')

  def foregroundButtonClicked(self,colNum):
    print 'foregroundButtonClicked('+str(colNum)+')'
    for b in self.foregroundSceneButtons:
      idx = self.foregroundSceneButtons.index(b)+1
      if idx == colNum:
        b.disconnect('clicked()')
      else:
        b.disconnect('clicked()')
        b.checked = False
        b.connect('clicked()',lambda i=idx: self.foregroundButtonClicked(i))
    for b in self.backgroundSceneButtons:
      idx = self.backgroundSceneButtons.index(b)+1
      b.disconnect('clicked()')
      b.checked = False
      b.connect('clicked()',lambda i=idx: self.backgroundButtonClicked(i))

  def testClick(self):
    #slicer.util.errorDisplay('testClick')
    idx = 0
    bChecked = False
    fChecked = False
    for b in self.backgroundSceneButtons:
      if b.checked:
        idx = self.backgroundSceneButtons.index(b)+1
        bChecked = True
      else:
        b.disconnect('toggled(bool)')
        b.checked = False
        b.connect('toggled(bool)',self.testClick)


#
# Segment4DLogic
#

class Segment4DLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def hasImageData(self,volumeNode):
    """This is an example logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      logging.debug('hasImageData failed: no volume node')
      return False
    if volumeNode.GetImageData() is None:
      logging.debug('hasImageData failed: no image data in volume node')
      return False
    return True

  def isValidInputOutputData(self, inputVolumeNode, outputVolumeNode):
    """Validates if the output is not the same as input
    """
    if not inputVolumeNode:
      logging.debug('isValidInputOutputData failed: no input volume node defined')
      return False
    if not outputVolumeNode:
      logging.debug('isValidInputOutputData failed: no output volume node defined')
      return False
    if inputVolumeNode.GetID()==outputVolumeNode.GetID():
      logging.debug('isValidInputOutputData failed: input and output volume is the same. Create a new volume for output to avoid this error.')
      return False
    return True

  def takeScreenshot(self,name,description,type=-1):
    # show the message even if not taking a screen shot
    slicer.util.delayDisplay('Take screenshot: '+description+'.\nResult is available in the Annotations module.', 3000)

    lm = slicer.app.layoutManager()
    # switch on the type to get the requested window
    widget = 0
    if type == slicer.qMRMLScreenShotDialog.FullLayout:
      # full layout
      widget = lm.viewport()
    elif type == slicer.qMRMLScreenShotDialog.ThreeD:
      # just the 3D window
      widget = lm.threeDWidget(0).threeDView()
    elif type == slicer.qMRMLScreenShotDialog.Red:
      # red slice window
      widget = lm.sliceWidget("Red")
    elif type == slicer.qMRMLScreenShotDialog.Yellow:
      # yellow slice window
      widget = lm.sliceWidget("Yellow")
    elif type == slicer.qMRMLScreenShotDialog.Green:
      # green slice window
      widget = lm.sliceWidget("Green")
    else:
      # default to using the full window
      widget = slicer.util.mainWindow()
      # reset the type so that the node is set correctly
      type = slicer.qMRMLScreenShotDialog.FullLayout

    # grab and convert to vtk image data
    qpixMap = qt.QPixmap().grabWidget(widget)
    qimage = qpixMap.toImage()
    imageData = vtk.vtkImageData()
    slicer.qMRMLUtils().qImageToVtkImageData(qimage,imageData)

    annotationLogic = slicer.modules.annotations.logic()
    annotationLogic.CreateSnapShot(name, description, type, 1, imageData)

  def run(self, inputVolume, outputVolume, imageThreshold, enableScreenshots=0):
    """
    Run the actual algorithm
    """

    if not self.isValidInputOutputData(inputVolume, outputVolume):
      slicer.util.errorDisplay('Input volume is the same as output volume. Choose a different output volume.')
      return False

    logging.info('Processing started')

    # Compute the thresholded output volume using the Threshold Scalar Volume CLI module
    cliParams = {'InputVolume': inputVolume.GetID(), 'OutputVolume': outputVolume.GetID(), 'ThresholdValue' : imageThreshold, 'ThresholdType' : 'Above'}
    cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True)

    # Capture screenshot
    if enableScreenshots:
      self.takeScreenshot('Segment4DTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class Segment4DTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_Segment4D1()

  def test_Segment4D1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data
    #
    import urllib
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        logging.info('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        logging.info('Loading %s...' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = Segment4DLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
