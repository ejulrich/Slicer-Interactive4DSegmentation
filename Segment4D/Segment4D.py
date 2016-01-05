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
    loadGroupBox.setTitle('Load Data')
    self.layout.addWidget(loadGroupBox)
    loadGroupBoxLayout = qt.QVBoxLayout(loadGroupBox)
    loadSceneButton = qt.QPushButton('Format Scene')
    loadGroupBoxLayout.addWidget(loadSceneButton)
    
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
    self.formatSceneWidgetLayout.addWidget(organizeSceneRegion,1,3,4,3)
    organizeSceneRegion.setTitle('Scene Format')
    self.organizeSceneRegionLayout = qt.QGridLayout(organizeSceneRegion)
    backgroundVolumeLabel = qt.QLabel('Background')
    self.organizeSceneRegionLayout.addWidget(backgroundVolumeLabel,1,1,1,1)
    backgroundVolumeBox = slicer.qMRMLListWidget()
    self.organizeSceneRegionLayout.addWidget(backgroundVolumeBox,2,1,1,1)
    foregroundVolumeLabel = qt.QLabel('Foreground')
    self.organizeSceneRegionLayout.addWidget(foregroundVolumeLabel,3,1,1,1)
    foregroundVolumeBox = slicer.qMRMLListWidget()
    self.organizeSceneRegionLayout.addWidget(foregroundVolumeBox,4,1,1,1)
    
    self.addColumnButton = qt.QPushButton('+Add')
    self.organizeSceneRegionLayout.addWidget(self.addColumnButton,2,2,1,1)
    
    loadFormattedSceneButton = qt.QPushButton('Load Scene')
    self.formatSceneWidgetLayout.addWidget(loadFormattedSceneButton,5,5,1,1)
    
    

    # connections
    loadSceneButton.connect('clicked(bool)', self.onLoadSceneButtonClicked)
    #self.formatSceneWidget.connect(')
    
    # change view layout
    #layoutManager = slicer.app.layoutManager()
    #layoutManager.setLayout(33) # 3x3 layout

  def cleanup(self):
    pass

  def onLoadSceneButtonClicked(self):
    self.formatSceneWidget.show()

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
