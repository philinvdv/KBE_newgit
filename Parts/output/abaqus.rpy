# -*- coding: mbcs -*-
#
# Abaqus/CAE Release 2023 replay file
# Internal Version: 2022_09_28-20.11.55 183150
# Run by matan on Sat Jun 15 18:29:14 2024
#

# from driverUtils import executeOnCaeGraphicsStartup
# executeOnCaeGraphicsStartup()
#: Executing "onCaeGraphicsStartup()" in the site directory ...
from abaqus import *
from abaqusConstants import *
session.Viewport(name='Viewport: 1', origin=(0.895833, 0.893519), 
    width=131.867, height=88.637)
session.viewports['Viewport: 1'].makeCurrent()
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
execfile('ODBinterpreter.py', __main__.__dict__)
#: Model: C:/Users/matan/OneDrive - Delft University of Technology/Bureaublad/Matan Neumark/TUDelft Master Aerospace Engineering/Year 1/Q3/AE4204 Knowledge based engineering/Assignment/KBE_newnewgit/Parts/output/wing_box_job.odb
#: Number of Assemblies:         1
#: Number of Assembly instances: 0
#: Number of Part instances:     13
#: Number of Meshes:             13
#: Number of Element Sets:       120
#: Number of Node Sets:          125
#: Number of Steps:              1
print 'RT script done'
#: RT script done
