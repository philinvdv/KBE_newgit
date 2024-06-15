from abaqus import *
from abaqusConstants import *
from driverUtils import *
import visualization
import numpy as np
# import pandas as pd
from collections import Iterable
from caeModules import *

executeOnCaeStartup()
# This file is an Abaqus script to run an inp file

# Write a job based on an existing inp file
job = mdb.JobFromInputFile(name='wing_box_job', inputFileName='wing_box.inp')

# Submit job
job.submit()
job.waitForCompletion()

# mdb.saveAs('wing_box.cae')

# Opening ODB result file
odb = session.openOdb(name='wing_box_job', path='wing_box_job.odb')

# Change the view port for screenshots
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
    referenceRepresentation=ON)
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=300,
    height=200)
session.viewports['Viewport: 1'].view.setValues(nearPlane=33.5223,
    farPlane=57.1616, width=9.72886, height=6.32141, cameraPosition=(9.70748,
    -37.4991, 10.8646), cameraUpVector=(-0.242013, 0.483729, 0.841092),
    cameraTarget=(-0.854045, 5.82098, 1.00903), viewOffsetX=-1,
    viewOffsetY=-0.695821)

session.viewports['Viewport: 1'].setValues(displayedObject=odb)
session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(
    CONTOURS_ON_DEF, ))

session.View(name='User-1', nearPlane=24.082, farPlane=72.245, width=9.3316,
    height=8.1039, projection=PERSPECTIVE, cameraPosition=(18.433, -26.891,
    31.088), cameraUpVector=(-0.50409, 0.69915, 0.50702), cameraTarget=(
    -1.4136, 4.213, 0.13087), viewOffsetX=0, viewOffsetY=0, autoFit=ON)
session.viewports['Viewport: 1'].view.setValues(session.views['User-1'])

# Plot mises stress, save image
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='S', outputPosition=INTEGRATION_POINT, refinement=(INVARIANT,
    'Mises'), )
session.printOptions.setValues(reduceColors=False)
session.printToFile(fileName='Mises_stress_deformed_state', format=PNG,
    canvasObjects=(session.viewports['Viewport: 1'], ))

# Plot U magnitude, save image
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='U', outputPosition=NODAL, refinement=(INVARIANT,
    'Magnitude'), )
session.printToFile(fileName='U-magnitude_deformed_state', format=PNG,
    canvasObjects=(session.viewports['Viewport: 1'], ))

# U-magnitude_deformed_state_root view, save image
session.viewports['Viewport: 1'].view.setValues(session.views['Bottom'])
session.viewports['Viewport: 1'].view.fitView()

session.printToFile(fileName='U-magnitude_deformed_state_root_view',
    format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))




# choose the last frame of the analysis
o1 = session.odbs['wing_box_job.odb']
session.viewports['Viewport: 1'].setValues(displayedObject=o1)
odbName=session.viewports[session.currentViewportName].odbDisplay.name
session.odbData[odbName].setValues(activeFrames=(('analysis1', (15, )), ))

# Output mises stress into a csv file
session.fieldReportOptions.setValues(sort=ASCENDING,
    reportFormat=COMMA_SEPARATED_VALUES)
session.writeFieldReport(fileName='mises_stress.csv', append=OFF,
    sortItem='Element Label', odb=o1, step=0, frame=15,
    outputPosition=INTEGRATION_POINT, variable=(('S', INTEGRATION_POINT, ((
    INVARIANT, 'Mises'), )), ), stepFrame=SPECIFY)

# Output U3 into a csv file
session.viewports['Viewport: 1'].odbDisplay.setPrimaryVariable(
    variableLabel='U', outputPosition=NODAL, refinement=(COMPONENT, 'U3'))
session.writeFieldReport(fileName='U3.csv', append=OFF, sortItem='Node Label',
    odb=o1, step=0, frame=15, outputPosition=NODAL, variable=(('U', NODAL, ((
    COMPONENT, 'U3'), )), ), stepFrame=SPECIFY)

