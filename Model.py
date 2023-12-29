# -*- coding: mbcs -*-
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import os
import matplotlib.pyplot as plt

#Change work directory
os.chdir(r"D:\Adam\Documents\5. LSBU\Year 5\Individual Research Project\05. Abaqus\Project model")

# #Generate folers for model
BaseDir = os.getcwd()
Foldername = 1

while os.path.exists(BaseDir+"/"+str(Foldername))==True:
    Foldername = Foldername + 1

os.mkdir(BaseDir+"/"+str(Foldername))
os.chdir(BaseDir+"/"+str(Foldername))

# Allows us to see coordinates of geometry
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)



def CreateBeamModel(variables):


	# Section Dimensions
	Top_flange_width = variables[0] #mm
	Bottom_flange_width = variables[1] #mm
	Web_height = variables[2] #mm
	Top_flange_thickness = variables[3] #mm
	Bottom_flange_thickness = variables[4] #mm
	Web_thickness = variables[5] #mm
	Length = variables[6] #mm

	#Opening Parameters
	Ellipse_raidus_1 = variables[7] #mm
	Ellipse_raidus_2 = variables[8] #mm
	First_opening_offset = variables[9] #mm
	Opening_spacing = variables[10] #mm
	Number_of_openings = variables[11]
	
	# Loading
	Load = variables[12] #KN

	# Mesh
	Mesh_size = variables[13]
	
		# Material Properties
	Steel_youngs_modulus = 210000 #mpa
	Steel_posion_ratio = 0.3
	Steel_Yield_stregnth = 355 #pa
	
	Model_web_height = Web_height + Top_flange_thickness/2.0 + Bottom_flange_thickness/2.0
	
	
	# Create new model
	Mdb()

	# This creates the beam

	mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
	mdb.models['Model-1'].sketches['__profile__'].Line(point1=(0.0, 0.0), point2=(
		200.0, 0.0))
	mdb.models['Model-1'].sketches['__profile__'].HorizontalConstraint(
		addUndoState=False, entity=
		mdb.models['Model-1'].sketches['__profile__'].geometry[2])
	del mdb.models['Model-1'].sketches['__profile__']
	mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
	mdb.models['Model-1'].sketches['__profile__'].Line(point1=(0.0, 0.0), point2=(
		Bottom_flange_width/2.0, 0.0))
	mdb.models['Model-1'].sketches['__profile__'].HorizontalConstraint(
		addUndoState=False, entity=
		mdb.models['Model-1'].sketches['__profile__'].geometry[2])
	mdb.models['Model-1'].sketches['__profile__'].Line(point1=(0.0, 0.0), point2=(
		-Bottom_flange_width/2.0, 0.0))
	mdb.models['Model-1'].sketches['__profile__'].HorizontalConstraint(
		addUndoState=False, entity=
		mdb.models['Model-1'].sketches['__profile__'].geometry[3])
	mdb.models['Model-1'].sketches['__profile__'].ParallelConstraint(addUndoState=
		False, entity1=mdb.models['Model-1'].sketches['__profile__'].geometry[2], 
		entity2=mdb.models['Model-1'].sketches['__profile__'].geometry[3])
	mdb.models['Model-1'].sketches['__profile__'].Line(point1=(0.0, 0.0), point2=(
		0.0, Model_web_height))
	mdb.models['Model-1'].sketches['__profile__'].VerticalConstraint(addUndoState=
		False, entity=mdb.models['Model-1'].sketches['__profile__'].geometry[4])
	mdb.models['Model-1'].sketches['__profile__'].PerpendicularConstraint(
		addUndoState=False, entity1=
		mdb.models['Model-1'].sketches['__profile__'].geometry[2], entity2=
		mdb.models['Model-1'].sketches['__profile__'].geometry[4])
	mdb.models['Model-1'].sketches['__profile__'].Line(point1=(0.0, Model_web_height), point2=
		(Top_flange_width/2.0, Model_web_height))
	mdb.models['Model-1'].sketches['__profile__'].HorizontalConstraint(
		addUndoState=False, entity=
		mdb.models['Model-1'].sketches['__profile__'].geometry[5])
	mdb.models['Model-1'].sketches['__profile__'].PerpendicularConstraint(
		addUndoState=False, entity1=
		mdb.models['Model-1'].sketches['__profile__'].geometry[4], entity2=
		mdb.models['Model-1'].sketches['__profile__'].geometry[5])
	mdb.models['Model-1'].sketches['__profile__'].Line(point1=(0.0, Model_web_height), point2=
		(-Top_flange_width/2.0, Model_web_height))
	mdb.models['Model-1'].sketches['__profile__'].HorizontalConstraint(
		addUndoState=False, entity=
		mdb.models['Model-1'].sketches['__profile__'].geometry[6])
	mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Part-1', type=
		DEFORMABLE_BODY)
	mdb.models['Model-1'].parts['Part-1'].BaseShellExtrude(depth=6000.0, sketch=
		mdb.models['Model-1'].sketches['__profile__'])
	del mdb.models['Model-1'].sketches['__profile__']

	# This creates the Ellipse opening gemorty

	mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
	mdb.models['Model-1'].sketches['__profile__'].EllipseByCenterPerimeter(
		axisPoint1=(Ellipse_raidus_1, 0.0), axisPoint2=(0.0, -Ellipse_raidus_2), center=(0.0, 0.0))
	mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Part-2', type=
		DEFORMABLE_BODY)
	mdb.models['Model-1'].parts['Part-2'].BaseShell(sketch=
		mdb.models['Model-1'].sketches['__profile__'])
	del mdb.models['Model-1'].sketches['__profile__']

	# This Creates Material Properties

	mdb.models['Model-1'].Material(name='Steel')
	mdb.models['Model-1'].materials['Steel'].Elastic(table=((Steel_youngs_modulus, Steel_posion_ratio), ))
	mdb.models['Model-1'].materials['Steel'].Plastic(table=((Steel_Yield_stregnth, 0.0), ))

	# This creates the 3 sections with different thicknesses
	# Top Flange
	mdb.models['Model-1'].HomogeneousShellSection(idealization=NO_IDEALIZATION, 
		integrationRule=SIMPSON, material='Steel', name='Section-1', 
		nodalThicknessField='', numIntPts=5, poissonDefinition=DEFAULT, 
		preIntegrate=OFF, temperature=GRADIENT, thickness= Top_flange_thickness, thicknessField='', 
		thicknessModulus=None, thicknessType=UNIFORM, useDensity=OFF)
	# Web
	mdb.models['Model-1'].HomogeneousShellSection(idealization=NO_IDEALIZATION, 
		integrationRule=SIMPSON, material='Steel', name='Section-2', 
		nodalThicknessField='', numIntPts=5, poissonDefinition=DEFAULT, 
		preIntegrate=OFF, temperature=GRADIENT, thickness= Web_thickness, thicknessField='', 
		thicknessModulus=None, thicknessType=UNIFORM, useDensity=OFF)
	# Bottom Flange
	mdb.models['Model-1'].HomogeneousShellSection(idealization=NO_IDEALIZATION, 
		integrationRule=SIMPSON, material='Steel', name='Section-3', 
		nodalThicknessField='', numIntPts=5, poissonDefinition=DEFAULT, 
		preIntegrate=OFF, temperature=GRADIENT, thickness= Bottom_flange_thickness, thicknessField='', 
		thicknessModulus=None, thicknessType=UNIFORM, useDensity=OFF)
		
	# This assigns the sections to each plate
		
	mdb.models['Model-1'].parts['Part-1'].SectionAssignment(offset=0.0, 
		offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
		faces=mdb.models['Model-1'].parts['Part-1'].faces.getSequenceFromMask(
		mask=('[#11 ]', ), )), sectionName='Section-1', thicknessAssignment=
		FROM_SECTION)
	mdb.models['Model-1'].parts['Part-1'].SectionAssignment(offset=0.0, 
		offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
		faces=mdb.models['Model-1'].parts['Part-1'].faces.getSequenceFromMask(
		mask=('[#2 ]', ), )), sectionName='Section-2', thicknessAssignment=
		FROM_SECTION)
	mdb.models['Model-1'].parts['Part-1'].SectionAssignment(offset=0.0, 
		offsetField='', offsetType=MIDDLE_SURFACE, region=Region(
		faces=mdb.models['Model-1'].parts['Part-1'].faces.getSequenceFromMask(
		mask=('[#c ]', ), )), sectionName='Section-3', thicknessAssignment=
		FROM_SECTION)
		
	# This creates the Asembly and instance


	# This creates the instance for Part-3
	mdb.models['Model-1'].rootAssembly.DatumCsysByDefault(CARTESIAN)
	mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='Part-1-1', 
		part=mdb.models['Model-1'].parts['Part-1'])
	mdb.models['Model-1'].rootAssembly.Instance(dependent=ON, name='Part-2-1', 
		part=mdb.models['Model-1'].parts['Part-2'])
	# This moves the ellipse to be inline with the beam (rotates 90 degrees)
	mdb.models['Model-1'].rootAssembly.instances['Part-2-1'].translate(vector=(
		96.0, 0.0, 0.0))
	mdb.models['Model-1'].rootAssembly.rotate(angle=90.0, axisDirection=(0.0, 10.0, 
		0.0), axisPoint=(0.0, 0.0, 0.0), instanceList=('Part-2-1', ))
	mdb.models['Model-1'].rootAssembly.translate(instanceList=('Part-2-1', ), 
		vector=(0.0, Model_web_height/2.0, 96.0))
	# This places the frist opening by creating a datum point and translating part-2 to that new point
	mdb.models['Model-1'].rootAssembly.DatumPointByOffset(point=
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1'].InterestingPoint(
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1'].edges[0], CENTER), 
		vector=(0.0, 0.0, First_opening_offset))
	mdb.models['Model-1'].rootAssembly.translate(instanceList=('Part-2-1', ), 
		vector=(0.0, 0.0, First_opening_offset))
	# This creates a Linear Pattern and cuts Part-1 from Part-2 to create Part-3
	mdb.models['Model-1'].rootAssembly.LinearInstancePattern(direction1=(0.0, 0.0, 
		1.0), direction2=(0.0, 1.0, 0.0), instanceList=('Part-2-1', ), number1=Number_of_openings, 
		number2=1, spacing1=Opening_spacing, spacing2=5.0)
	mdb.models['Model-1'].rootAssembly.InstanceFromBooleanCut(cuttingInstances=(
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-2-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-3-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-4-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-5-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-6-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-7-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-8-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-9-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-10-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-11-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-12-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-13-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-14-1'], 
		mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-15-1']), 
		instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['Part-1-1'], 
		name='Part-3', originalInstances=DELETE)
	# Makes instance independent
	mdb.models['Model-1'].rootAssembly.makeIndependent(instances=(
		mdb.models['Model-1'].rootAssembly.instances['Part-3-1'], ))
	# Creates Partition
	mdb.models['Model-1'].rootAssembly.PartitionEdgeByParam(edges=
		mdb.models['Model-1'].rootAssembly.instances['Part-3-1'].edges.getSequenceFromMask(
		('[#40000 ]', ), ), parameter=0.5)	
	# This creates the step
	mdb.models['Model-1'].StaticStep(initialInc=0.01, maxInc=0.01, name='Step-1', 
		nlgeom=ON, previous='Initial')	

	# This Adds the boundary conditions

	#Load
	mdb.models['Model-1'].ConcentratedForce(cf2=-Load, createStepName='Step-1', 
		distributionType=UNIFORM, field='', localCsys=None, name='Load-1', region=
		Region(
		vertices=mdb.models['Model-1'].rootAssembly.instances['Part-3-1'].vertices.findAt(
		((0.0, Model_web_height, Length/2.0), ), )))
		
	#Support 1
	mdb.models['Model-1'].DisplacementBC(amplitude=UNSET, createStepName='Step-1', 
		distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=
		'BC-1', region=Region(
		edges=mdb.models['Model-1'].rootAssembly.instances['Part-3-1'].edges.findAt(
		((-Bottom_flange_width/8.0, 0.0, Length), ), ((Bottom_flange_width/8.0, 0.0, Length), ), )), u1=0.0, u2=0.0, u3=
		0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET)
	# support 2
	mdb.models['Model-1'].DisplacementBC(amplitude=UNSET, createStepName='Step-1', 
		distributionType=UNIFORM, fieldName='', fixed=OFF, localCsys=None, name=
		'BC-2', region=Region(
		edges=mdb.models['Model-1'].rootAssembly.instances['Part-3-1'].edges.findAt(
		((-Bottom_flange_width/8.0, 0.0, 0.0), ), ((Bottom_flange_width/8.0, 0.0, 0.0), ), )), u1=0.0, u2=0.0, u3=UNSET, 
		ur1=UNSET, ur2=UNSET, ur3=UNSET)
	#This creates the Mesh

	mdb.models['Model-1'].rootAssembly.seedPartInstance(deviationFactor=0.1, 
		minSizeFactor=0.1, regions=(
		mdb.models['Model-1'].rootAssembly.instances['Part-3-1'], ), size= Mesh_size)
	mdb.models['Model-1'].rootAssembly.generateMesh(regions=(
		mdb.models['Model-1'].rootAssembly.instances['Part-3-1'], ))
		
	# This creates the Job

	mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, 
		explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, 
		memory=90, memoryUnits=PERCENTAGE, model='Model-1', modelPrint=OFF, 
		multiprocessingMode=DEFAULT, name='Job-1', nodalOutputPrecision=SINGLE, 
		numCpus=1, numGPUs=0, queue=None, resultsFormat=ODB, scratch='', type=
		ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
		
	#This submits the job

	mdb.jobs['Job-1'].submit(consistencyChecking=OFF)

	#To wait for job completion

	mdb.jobs['Job-1'].waitForCompletion()
	print("SS I-beam model finished running")

def PostProcessing():
	CurrentDir = os.getcwd()
	odb = session.openOdb(CurrentDir + '/Job-1.odb')
	NrOfSteps = len(odb.steps['Step-1'].frames)
	
	displacements = []
	
	for i in range(NrOfSteps):
		central_disp = odb.steps['Step-1'].frames[i].fieldOutputs['U'].values[0].data[1]*-1
		displacements.append(central_disp)
		print(central_disp)
		print(displacements)
		
	Forces = []
	
	for i in range(NrOfSteps):
		applied_force = odb.steps['Step-1'].frames[i].fieldOutputs['CF'].values[2].data[1]*-1
		Forces.append(applied_force)

	
	fig, ax = plt.subplots()
	ax.plot(displacements, Forces, color='r', label='U2')
	plt.legend()
	ax.set(xlabel='Displacements [mm]', ylabel='Applied Load [kN]',
		Title='Force Displacement Curve')
	ax.grid()
	
	fig.savefig("MAX_DISPLACEMENT.PNG")
	plt.close(fig)
	
"""
# Section Dimensions
Top_flange_width = variables[0] #mm
Bottom_flange_width = variables[1] #mm
Web_height = variables[2] #mm
Top_flange_thickness = variables[3] #mm
Bottom_flange_thickness = variables[4] #mm
Web_thickness = variables[5] #mm
Length = variables[6] #mm

#Opening Parameters
Ellipse_raidus_1 = variables[7] #mm
Ellipse_raidus_2 = variables[8] #mm
First_opening_offset = variables[9] #mm
Opening_spacing = variables[10] #mm
Number_of_openings = variables[11]

# Loading
Load = variables[12] #KN

# Mesh
Mesh_size = variables[13]
"""


models = []

models.append([180.0, 100.0, 190.0, 18.0, 20.0, 19.0, 6000.0, 100.0, 50.0, 200.0, 400.0, 15, 5000.0, 100.0])
models.append([180.0, 100.0, 190.0, 18.0, 20.0, 19.0, 7000.0, 100.0, 50.0, 200.0, 400.0, 15, 5000.0, 100.0])



for i in models:
    ModelName = str(i[0])
    for j in i[1:]:
        ModelName = ModelName + "_" + str(j)
    NameFolder = BaseDir+ "/" +str(Foldername) + "/" + ModelName
    print(NameFolder)
    os.mkdir(NameFolder)
    os.chdir(NameFolder)
    CreateBeamModel(i)
    PostProcessing()