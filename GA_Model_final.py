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
import sys
import math
import numpy as np
import random
import shutil
import pickle

# For now , we are solving for the beam with minimum weight for a given load (elastic) that guarantees a certain deflection 

#Change work directory
path = r"D:\Adam\Documents\5. LSBU\Year 5\Individual Research Project\05. Abaqus\Project model"
# path = r"C:\Users\pinhosl3\Documents\Adam_test\GA"
os.chdir(path)






# #Generate folers for model
BaseDir = os.getcwd()
Foldername = 1

while os.path.exists(BaseDir+"/"+str(Foldername))==True:
    Foldername = Foldername + 1

os.mkdir(BaseDir+"/"+str(Foldername))
os.chdir(BaseDir+"/"+str(Foldername))


# Allows us to see coordinates of geometry
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)

def PrintToScreen(Message):
    print >> sys.__stdout__, '%s' % Message


# Section Dimensions - particular section
Top_flange_width = 126.0 #mm
Bottom_flange_width = 126.0 #mm
Web_height = 332.0 #mm
Top_flange_thickness = 10.7 #mm
Bottom_flange_thickness = 10.7 #mm
Web_thickness = 6.6 #mm
Model_web_height = Web_height + Top_flange_thickness/2.0 + Bottom_flange_thickness/2.0
Length = 6000.0 #mm
# Loading
Load = 90.0 #kN
# Mesh - change later
Mesh_size = 25.0 #mm

# Volume/weight
Area_Top_flange = Top_flange_width * Top_flange_thickness
Area_Bottom_flange = Bottom_flange_width * Bottom_flange_thickness
Area_Web = (Web_height - Top_flange_thickness/2.0 - Bottom_flange_thickness/2.0) * Web_thickness
Total_Section_Area = Area_Top_flange + Area_Bottom_flange + Area_Web
Volume_No_openings = Total_Section_Area * Length
PrintToScreen(Volume_No_openings)





# Volume_deformation_no_holes = 29749320 #mm3
# Allowable_displacement = L/200.0 (BS EN 1990 1-1 Table NA.2)
Allowable_displacement = Length/200.0

# We are going to optimise only the Number_of_openings and the two radii of the elipses
# We are also trying to reduce weight/volume while staying within the deflection constraint
n_range = [2, 18, 4]
r1_range = [5.0, 500.0, 8] # this is in length
r2_range = [5.0, Web_height*0.48, 8] # this is in height 

Population_size = 200
Generations = 50
Elitism_size = 2
Tournament_size = 2

variables = [n_range, r1_range, r2_range]

for i in variables:
    step = (i[1]-i[0])/(2**i[2]-1)
    i.append(step)
    
PrintToScreen(variables)

PrintToScreen('New Run[write "N"]? Or Continue Previous Run[write "C"]?')
GA_status = input('New Run[write "N"]? Or Continue Previous Run[write "C"]?')
if str(GA_status) == "N":
    GA_status = "New"
elif str(GA_status) == "C":
    GA_status = "Continue"


if GA_status == "Continue":
    Round = 1
    while os.path.isdir("%s/Round%s" % (path, Round + 1)):
        Round = Round + 1
        PrintToScreen(Round)
    os.chdir("%s/Round%s" % (path, Round))
    for dirs in os.listdir("%s/Round%s" % (path, Round)):
        if dirs.startswith("[") and os.path.isfile("%s/Round%s/%s/FitnessData.txt" % (path, Round, dirs)) == False:
            shutil.rmtree("%s/Round%s/%s" % (path, Round, dirs))
            break


def CreateInitialPop(variables, Population_size):
    count = 0 
    InitPop = []
    Chromossome_Lenght = 0
    for i in variables:
        Chromossome_Lenght = Chromossome_Lenght + i[2]
    while count < Population_size:
        Chromossome = ''
        for i in range(Chromossome_Lenght):
            Chromossome = Chromossome + str(random.choice([0,1]))        
        if Chromossome not in InitPop:
            InitPop.append([Chromossome])
            count = count + 1
        else:
            print("------REPEATED-------")
    
    return InitPop


def ChromossomeToData(Chromossome, variables):
    var_data = []
    start = 0
    for i in variables:
        var_binary = Chromossome[0][start:start+i[2]]
        var_decimal = i[0] + int(str(var_binary), 2)*i[3]
        var_data.append(round(var_decimal,1))
        start = start + i[2]
    return var_data


def CreateBeamModel(variables):

    #Opening Parameters
    Number_of_openings = int(variables[0])
    Ellipse_raidus_1 = variables[1] #mm
    Ellipse_raidus_2 = variables[2] #mm
    if Ellipse_raidus_2 > Web_height/2.0:
        return 100 * Volume_No_openings
        # sys.exit("error, the opening is too large for the height of the beam")
    First_opening_offset = Web_height + Ellipse_raidus_1/2.0 #mm
    Aux = Length - 2.0*First_opening_offset
    Opening_spacing = Aux/(Number_of_openings-1)
    if Opening_spacing < Ellipse_raidus_1 * 2.0:
        return 100 * Volume_No_openings
        # sys.exit("error, the number of openings are too large") 
        

    
    # if Volume > Volume_No_openings
        # return 999.99
# Area of Ellipse
    Area_Ellipse = math.pi * Ellipse_raidus_1 * Ellipse_raidus_2
    
    # Volume Reduction
    Volume_Reduction = Area_Ellipse * Number_of_openings * Web_thickness
    
    Final_Volume = Volume_No_openings - Volume_Reduction

        # Material Properties
    Steel_youngs_modulus = 210000 #Mpa
    Steel_posion_ratio = 0.3
    # Steel_Yield_stregnth = 355 #Mpa

    
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
    mdb.models['Model-1'].parts['Part-1'].BaseShellExtrude(depth=Length, sketch=
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
    # mdb.models['Model-1'].materials['Steel'].Plastic(table=((Steel_Yield_stregnth, 0.0), ))

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
        
    Cuts = [mdb.models['Model-1'].rootAssembly.instances['Part-2-1']]
    for j in range(Number_of_openings-1):
        Cuts = Cuts + [mdb.models['Model-1'].rootAssembly.instances['Part-2-1-lin-%s-1' % (j+2)]]

    mdb.models['Model-1'].rootAssembly.InstanceFromBooleanCut(cuttingInstances=Cuts, 
        instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['Part-1-1'], 
        name='Part-3', originalInstances=DELETE)
        
    # Makes instance independent
    mdb.models['Model-1'].rootAssembly.makeIndependent(instances=(
        mdb.models['Model-1'].rootAssembly.instances['Part-3-1'], ))
    # Creates Partition
    mdb.models['Model-1'].rootAssembly.makeIndependent(instances=(
        mdb.models['Model-1'].rootAssembly.instances['Part-3-1'], ))
    mdb.models['Model-1'].rootAssembly.PartitionEdgeByPoint(edge=
        mdb.models['Model-1'].rootAssembly.instances['Part-3-1'].edges.findAt((0.0, 
        Model_web_height, Length/2.0), ), point=
        mdb.models['Model-1'].rootAssembly.instances['Part-3-1'].InterestingPoint(
        mdb.models['Model-1'].rootAssembly.instances['Part-3-1'].edges.findAt((0.0, 
        Model_web_height, Length/2.0), ), MIDDLE))
    # This creates the step
    mdb.models['Model-1'].StaticStep(initialInc=0.5, maxInc=0.5, name='Step-1', 
        nlgeom=ON, previous='Initial')	

    # This Adds the boundary conditions

    #Load
    mdb.models['Model-1'].ConcentratedForce(cf2=-Load*1000, createStepName='Step-1', 
        distributionType=UNIFORM, field='', localCsys=None, name='Load-1', region=
        Region(vertices=mdb.models['Model-1'].rootAssembly.instances['Part-3-1'].vertices.findAt(((0.0, Model_web_height, Length/2.0), ), )))
        
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


    # def PostProcessing():
    CurrentDir = os.getcwd()
    odb = session.openOdb(CurrentDir + '/Job-1.odb')
    NrOfSteps = len(odb.steps['Step-1'].frames)

    displacements = []

    for i in range(NrOfSteps):
        central_disp = odb.steps['Step-1'].frames[i].fieldOutputs['U'].values[2].data[1]*-1
        displacements.append(central_disp)
        
    Forces = []

    for i in range(NrOfSteps):
        applied_force = odb.steps['Step-1'].frames[i].fieldOutputs['CF'].values[2].data[1]*-1/1000
        Forces.append(applied_force)

    opFile = CurrentDir+'/'+'DatainExcel.csv'
     
    try:
        opFileU = open(opFile,'w')
        opFileU.write("%10s, %10s\n"%('Disp', 'Force'))
    except IOError:
        print('cannot open opFILE')
        exit(0)
     
    for i in range(NrOfSteps):
        displacement = displacements[i]
        force = Forces[i]
     
        opFileU.write("%10f, %10f\n" % (displacement, force))
        
    opFileU.close()

# Creates .PNG of results
    fig, ax = plt.subplots()
    ax.plot(displacements, Forces, color='r', label='U2')
    plt.legend()
    ax.set(xlabel='Displacements [mm]', ylabel='Applied Load [kN]',
        Title='Force Displacement Curve')
    ax.grid()

    fig.savefig("MAX_DISPLACEMENT.PNG")
    plt.close(fig)

    Disps = odb.steps['Step-1'].frames[2].fieldOutputs['U'].getSubset(position = NODAL).bulkDataBlocks[0].data
    MaxDisps = np.max(np.abs(Disps),axis=0)
    MaxU2 = MaxDisps[1]

    odb.close()
    print(MaxU2)
    
    if MaxU2 < Allowable_displacement:
        PrintToScreen(Final_Volume)
        return Final_Volume
    else:
        PrintToScreen(Final_Volume)
        PrintToScreen("tototo")
        return Final_Volume * (MaxU2/Allowable_displacement + 0.1) 


	

def Tournament(OldPop, PlayersNumber):
    ww = np.random.randint(0,len(OldPop))
    winner = OldPop[ww][0]
    counter = 0
    while counter < PlayersNumber - 1:
        cc = np.random.randint(0,len(OldPop))
        challenger = OldPop[cc][0]
        # Remember to verify that the Fitness is the last value
        
        if OldPop[ww][-1] < OldPop[cc][-1]:
            continue
        else:
            ww = cc
            winner = challenger
        counter = counter + 1
    return winner
    
    
def NewPopulation(OldPop, select, Tournament_size, Current_Round, Generations):
    Newpop = []
    counter = select
    OldPop_sorted = sorted(OldPop,key=lambda x: x[-1])
    # This does elitism selection
    for i in range(select):
        Newpop.append([OldPop_sorted[i][0]])
    # This does tournament selection before crossover
    while counter < len(OldPop):
        father = Tournament(OldPop, Tournament_size)
        mother = Tournament(OldPop, Tournament_size)
        # while mother == father:
            # mother = Tournament(OldPop, fitness, 3)
        child1 = ''
        child2 = ''
        # This does crossover of genes: 70% chance of occuring
        if np.random.uniform(0, 1) <= 0.7:
            for i in range(len(OldPop[0][0])):    
                child1 = child1 + str(np.random.choice([father[i],mother[i]]))
                child2 = child2 + str(np.random.choice([father[i],mother[i]]))
        else:
            child1 = father
            child2 = mother
        counter = counter + 2
        # This does mutation of genes
        child2 = MutateChromossome(child2, 0.1)
        child1 = MutateChromossome(child1, 0.1)
        # child1 = MutateChromossome(child1, 0.1+0.8*(Current_Round/float(Generations)))
        # child2 = MutateChromossome(child2, 0.1+0.8*(Current_Round/float(Generations)))
        Newpop.append([child1])
        Newpop.append([child2])
    return Newpop


def MutateChromossome(Chromossome, Probability):
    if np.random.uniform(0, 1) <= Probability:
        Random_Gene = np.random.randint(0,len(Chromossome))
        if Chromossome[Random_Gene] == '0':
            Chromossome = Chromossome[0:Random_Gene] + '1' + Chromossome[Random_Gene+1:]
        else:
            Chromossome = Chromossome[0:Random_Gene] + '0' + Chromossome[Random_Gene+1:]
    return Chromossome


def CreateFolder(name):
    if not os.path.exists("%s" % name):
        os.makedirs("%s" % name)
    os.chdir("%s" % name)
    

def GeneticAlgorithm(variables, Generations, Population_size, Elitism_size, Tournament_size, Round):
    if Round == 1:
        Process = []
        os.chdir("%s/Round%s" % (path,Round))
        Population_binary = pickle.load(open("Population_binary_list", 'rb'))
        SaveAnalysisbinary = pickle.load(open("SaveAnalysisbinary", 'rb'))
    elif Round == 0:
        Process = []
        SaveAnalysisbinary = dict()
        Population_binary = CreateInitialPop(variables, Population_size)
        Round = 1
    else:
        os.chdir(path)
        Process = pickle.load(open("Process_list", 'rb'))
        os.chdir("%s/Round%s" % (path,Round))
        Population_binary = pickle.load(open("Population_binary_list", 'rb'))
        SaveAnalysisbinary = pickle.load(open("SaveAnalysisbinary", 'rb'))
    for i in range(Generations-Round+1):
        os.chdir(path)
        CreateFolder("Round%s" % (i+Round))
        PrintToScreen('-------ROUND %s-------' % (i+Round))
        os.chdir("%s/Round%s" % (path,i+Round))
        pickle.dump(Population_binary, open("Population_binary_list", 'wb'))
        if len(Population_binary[0])==1:
            for j in range(Population_size):
                Population_binary[j].append(ChromossomeToData(Population_binary[j], variables))
        for Chromossome in Population_binary:
            if str(Chromossome[0]) in SaveAnalysisbinary:
                PrintToScreen("Saving analysis")
                #print("Retrieving results from previous analysis")
                Fitness = SaveAnalysisbinary[str(Chromossome[0])][-1]
                Chromossome.append(Fitness)
                os.chdir("%s/Round%s" % (path,i+Round))
            else:
                #print("New binary")
                PrintToScreen("New binary")
                CreateFolder("%s" % (Chromossome[1]))
                os.chdir("%s/Round%s/%s" % (path,i+Round,Chromossome[1]))
                PrintToScreen(Chromossome)
                Fitness = CreateBeamModel(Chromossome[1])
                SaveAnalysisbinary[str(Chromossome[0])] = [Chromossome[1], (i+Round), Fitness]
                Chromossome.append(Fitness)
                os.chdir("%s/Round%s" % (path,i+Round))
                pickle.dump(SaveAnalysisbinary, open("SaveAnalysisbinary", 'wb'))
        os.chdir(path)
        MinFitness = float('inf')
        SumFitness = 0
        for Chromossome in Population_binary:
            SumFitness = SumFitness + Chromossome[-1]
            MinFitness = min(Chromossome[-1], MinFitness)
        Process.append([i+Round, MinFitness, SumFitness/Population_size])
        PrintData("%s/Round%s" % (path,i+Round), 'Process', "Round\tMinFitness\tAverageFitness", Process)
        PrintData("%s/Round%s" % (path,i+Round), 'Population_binary', "GeneticCode\tVariables\tFitness", Population_binary)
        PrintFinalData("%s/Round%s" % (path,i+Round), 'AllIndividuals', "GeneticCode\tVariables\tRound\tFitness", SaveAnalysisbinary)
        pickle.dump(Process, open("Process_list", 'wb'))
        if i+Round == Generations-1:
            continue
        else:
            Population_binary = NewPopulation(Population_binary, Elitism_size, Tournament_size, i+1, Generations)
    
    PrintData("%s/Round%s" % (path,i+Round), 'Process', "Round\tMinFitness\tAverageFitness", Process)
    PrintFinalData("%s/Round%s" % (path,i+Round), 'AllIndividuals', "GeneticCode\tVariables\tRound\tFitness", SaveAnalysisbinary)
    #print('GA is completed')
    PrintToScreen('GA is completed')
    

def DeleteRounds(path):
    os.chdir(path)
    for dirs in os.listdir(path):
        if dirs.startswith("Round"):
            shutil.rmtree("%s/%s" % (path,dirs))


def PrintData(Folder, Filename, Title, Data):
    #This will depend on the application in mind
    opFile = Folder+"/"+Filename+'.txt'
    
    try:
        opFileU = open(opFile,'w')
        opFileU.write("%10s\n" % Title)
    except IOError:
        print('cannot open', opFile)
        exit(0)

    for line in Data:
        for item in line:
            opFileU.write(str(item))
            opFileU.write("\t")
        opFileU.write("\n")
    opFileU.close()


def PrintFinalData(Folder, Filename, Title, Data):
    #This will depend on the application in mind
    opFile = Folder+"/"+Filename+'.txt'
    
    try:
        opFileU = open(opFile,'w')
        opFileU.write("%10s\n" % Title)
    except IOError:
        print('cannot open', opFile)
        exit(0)

    GenCodes = list(Data.keys())
    Fitnesses = list(Data.values())
    for i in range(len(Data)):
        opFileU.write(GenCodes[i])
        opFileU.write("\t")
        opFileU.write(str(Fitnesses[i]))
        # opFileU.write(Chromossome[str(Chromossome[0])])
        opFileU.write("\n")
    opFileU.close()

    
if GA_status == "New":
    DeleteRounds("%s" % path)
    Round = 0
    GeneticAlgorithm(variables, Generations, Population_size, Elitism_size, Tournament_size, Round)
    
elif GA_status == "Continue":
    GeneticAlgorithm(variables, Generations, Population_size, Elitism_size, Tournament_size, Round)

"""
models = []

models.append([126.0, 126.0, 332.0, 10.7, 10.7, 6.6, 6000.0, 100.0, 75.0, 15, 500.0, 25]) # Section geometry suit UB 356x127x39

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
    """