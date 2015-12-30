import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import dicom

#
# Load4D
#

class Load4D(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Load4D" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Informatics"]
    self.parent.dependencies = []
    self.parent.contributors = ["Ethan Ulrich (University of Iowa)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """TODO"""
    self.parent.acknowledgementText = """TODO""" # replace with organization, grant and thanks.

#
# Load4DWidget
#

class Load4DWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...
    
    #
    # Data Area
    #
    dataGroupBox = ctk.ctkCollapsibleGroupBox()
    dataGroupBox.setTitle('Data')
    self.layout.addWidget(dataGroupBox)
    
    dataGridLayout = qt.QGridLayout(dataGroupBox)
    self.dirButton = ctk.ctkDirectoryButton()
    dirButtonLabel = qt.QLabel('DICOM Directory: ')
    dataGridLayout.addWidget(dirButtonLabel,1,1,1,1)
    dataGridLayout.addWidget(self.dirButton,1,2,1,3)
    self.dirButton.setMaximumWidth(500)
    orLabel = qt.QLabel('        - or - ')
    dataGridLayout.addWidget(orLabel,2,1,1,1)
    collectionsComboBoxLabel = qt.QLabel('TCIA Collection: ')
    dataGridLayout.addWidget(collectionsComboBoxLabel,3,1,1,1)
    
    try:
      m = slicer.modules.tciabrowser
      self.tciaWidget = m.createNewWidgetRepresentation()
      self.tcia = slicer.modules.TCIABrowserWidget
      self.connectTCIAButton = qt.QPushButton('Connect')
      self.connectTCIAButton.toolTip = "Connect to TCIA Server."
      dataGridLayout.addWidget(self.connectTCIAButton,3,2,1,1)
      self.collectionsComboBox = qt.QComboBox()
      dataGridLayout.addWidget(self.collectionsComboBox,3,3,1,2)
      # connections
      self.connectTCIAButton.connect('clicked(bool)', self.getTCIACollectionValues)
      # TODO disable scrolling event for collectionsComboBox
      self.collectionsComboBox.connect('currentIndexChanged(QString)',self.onTCIACollectionChanged)
    except AttributeError:
      # TODO add button to open Extensions Manager
      noConnectionLabel = qt.QLabel('TCIA Browser not installed.')
      dataGridLayout.addWidget(noConnectionLabel,3,2,1,1)

    #
    # Patient Table Area
    #
    patientGroupBox = ctk.ctkCollapsibleGroupBox()
    patientGroupBox.setTitle('Patient Selection')
    self.layout.addWidget(patientGroupBox)
    #patientGroupBoxLayout = qt.QVBoxLayout(patientGroupBox)
    patientGroupBoxLayout = qt.QGridLayout(patientGroupBox)
    
    self.patientsTable = qt.QTableWidget()
    self.patientsTableHeaderLabels = ['ID','Name','BirthDate',
        'Sex','Modalities']
    self.patientsTable.setColumnCount(5)
    self.patientsTable.sortingEnabled = True
    self.patientsTable.setHorizontalHeaderLabels(self.patientsTableHeaderLabels)
    self.patientsTableHeader = self.patientsTable.horizontalHeader()
    self.patientsTableHeader.setStretchLastSection(True)
    #patientGroupBoxLayout.addWidget(self.patientsTable)
    patientGroupBoxLayout.addWidget(self.patientsTable,1,1,1,5)
    abstractItemView =qt.QAbstractItemView()
    self.patientsTable.setSelectionBehavior(abstractItemView.SelectRows) 
    
    self.examinePatientButton = qt.QPushButton('Examine')
    self.examinePatientButton.setEnabled(False)
    patientGroupBoxLayout.addWidget(self.examinePatientButton,2,4,1,2)
    
    #
    # Other Connections
    #
    self.dirButton.connect('directoryChanged(const QString &)',self.onDICOMDirectoryChanged)
    

  def cleanup(self):
    self.tciaWidget.delete()

  def onDICOMDirectoryChanged(self):
    print 'onDICOMDirectoryChanged()'
    self.patientsTable.clear()
    self.patientsTable.setHorizontalHeaderLabels(self.patientsTableHeaderLabels)
    self.examinePatientButton.disconnect('clicked(bool)')
    self.examinePatientButton.setText('Examine Patient')
    self.examinePatientButton.connect('clicked(bool)', self.onExaminePatient)
    # recursively read directory TODO make this much faster
    self.patientFiles = {}
    for directory, subdir, f in os.walk(self.dirButton.directory):
      for filename in f:
        if filename[-4:]=='.dcm':
          filePath = os.path.join(directory,filename)
          dcmFile = dicom.read_file(filePath)
          patient = str(dcmFile.PatientID)
          modality = str(dcmFile.Modality)
          if patient not in self.patientFiles.keys():
            self.patientFiles[patient] = {}
            self.patientFiles[patient]['Modalities'] = []
          if modality not in self.patientFiles[patient]:
            self.patientFiles[patient][modality] = []
            self.patientFiles[patient]['Modalities'].append(modality)
          self.patientFiles[patient][modality].append(filePath)
          self.patientFiles[patient]['PatientName'] = str(dcmFile.PatientName)
          self.patientFiles[patient]['PatientBirthDate'] = str(dcmFile.PatientBirthDate)
          self.patientFiles[patient]['PatientSex'] = str(dcmFile.PatientSex)
          try:
            self.patientFiles[patient]['EthnicGroup'] = str(dcmFile.EthnicGroup)
          except AttributeError:
            pass
    
    # populate the table
    count = 0
    patients = self.patientFiles.keys()
    self.patientsTable.setRowCount(len(patients))
    for patient in patients:
      self.patientsTable.setItem(count,0,qt.QTableWidgetItem(patient))
      self.patientsTable.setItem(count,1,qt.QTableWidgetItem(self.patientFiles[patient]['PatientName']))
      self.patientsTable.setItem(count,2,qt.QTableWidgetItem(self.patientFiles[patient]['PatientBirthDate']))
      self.patientsTable.setItem(count,3,qt.QTableWidgetItem(self.patientFiles[patient]['PatientSex']))
      modalities = self.patientFiles[patient]['Modalities']
      modalities.sort()
      self.patientsTable.setItem(count,4,qt.QTableWidgetItem(','.join(modalities)))
      count += 1
    
    self.patientsTable.resizeColumnsToContents()
    self.patientsTableHeader.setStretchLastSection(True)
    self.patientsTableHeader.setSortIndicator(0,0) # order by patient name
             
    print patients
    self.examinePatientButton.enabled = True
  
  def getTCIACollectionValues(self):
    self.examinePatientButton.enabled = False
    self.connectTCIAButton.enabled = False
    self.collectionsComboBox.disconnect('currentIndexChanged(QString)')
    self.collectionsComboBox.clear()
    self.collectionsComboBox.connect('currentIndexChanged(QString)',self.onTCIACollectionChanged)
    self.tcia.getCollectionValues()
    self.tcia.browserWidget.hide()
    for collection in xrange(0,self.tcia.collectionSelector.count):
      self.collectionsComboBox.addItem(self.tcia.collectionSelector.itemText(collection))
    
  def onTCIACollectionChanged(self,item):
    print 'onTCIACollectionChanged()'
    self.examinePatientButton.disconnect('clicked(bool)')
    self.examinePatientButton.setText("Download && Examine Patient")
    self.examinePatientButton.connect('clicked(bool)', self.onDownloadAndExaminePatient)
    # TODO call methods from TCIA browser
    self.examinePatientButton.enabled = True
    
  def onExaminePatient(self):
    # TODO
    pass
    
  def onDownloadAndExaminePatient(self):
    # TODO
    pass
    
  


#
# Load4DLogic
#

class Load4DLogic(ScriptedLoadableModuleLogic):
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
      self.takeScreenshot('Load4DTest-Start','MyScreenshot',-1)

    logging.info('Processing completed')

    return True


class Load4DTest(ScriptedLoadableModuleTest):
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
    self.test_Load4D1()

  def test_Load4D1(self):
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
    logic = Load4DLogic()
    self.assertIsNotNone( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')
