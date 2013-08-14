### HEADER
print
print "This script automates a DayCent validation analysis sequence as specified in the" 
print "Windows-CSV-formatted 'runtable.csv'."
print
print "It assumes the following directory structure:" 
print "    Main directory: UNIX-exectutable DDcentEVI & DDClist100, runtable.csv"
print "    Subdirectory 'AFRI_100files': all necessary *.IN & *.100, outvars.txt"
print "    Subdirectory 'Results': repository for archived analysis results"
print "    Subdirectory for each study to be simulated containing all .sch, soils.in," 
print "         and .wth files for all sites & treatments as named in runtable.csv"
print "         (Naming conventions: .sch files- site_eq, site_base, site_treatment;" 
print "          weather files- NARR_x_y.wth; soils files- mukey.in)"
print "    Subdirectory/subdirectory: this script (autoDDC.py)"
print


### SET WORKING DIRECTORY, DEFINE OTHER DIRECTORY PATHS
import os
import time
import datetime
start = time.time()                     #start script runtimer
tstamp = datetime.datetime.now().strftime("%Y-%m-%d,%H.%M")   #timestamp for archive name
print "Timestamp:  ", tstamp
abspath = os.path.abspath(__file__)     #get absolute path where script is located
dname = os.path.dirname(abspath)        #get associated directory only
os.chdir(dname)
os.chdir('..')
os.chdir('..')                          #navigate TWO directories higher
dirmain = os.getcwd()                   #define main working directory
dirlib = dirmain + "/AFRI_100files"     #define *.100 & *.IN library directory
dirarch = dirmain + "/Results/" + tstamp
print "Main directory:  ", dirmain
print "Archive directory:  ", dirarch
print
print "If you wish to re-use the *.bin files from an existing spin-up sequence, please" 
print "specify the archive directory name (leave blank to run a new spin-up sequence):"
nospin = raw_input()                                  # If r = True, Then no spinup
dirapp = dirmain + "/Results/" + nospin     #define appended .bin directory path
print


### IMPORT LIBRARY FILES
import glob
import shutil
for file in glob.glob(os.path.join(dirlib, '*')):
    if file.endswith(".100") or file.endswith(".in") or file.endswith(".txt"):
        shutil.copy(file, dirmain)      #copy all .100/.in/.txt files to main directory
os.chdir(dirmain)
os.remove('Milan.100')                  #excluding the Milan practice site.100 file
# x = raw_input("Check for library files, and press Enter/Return to continue")


### DDCENTEVI/DDCENTLIST100 CALL
# runs either an equilibrium-base-experiment sequence, or just an experiment depending on
# the boolean value of 'spin' 
# generates a final .lis output 
def DDCentEVI(feq,fbase,fexp):          #Note: eq changed to feq within function, etc.
    import subprocess
    os.chdir(dirmain)
    if not os.path.exists(dirmain+"/"+fbase+".bin"):
        print "Running full simulation sequence of "+feq+".sch, "+fbase+".sch, and "+fexp+".sch"
        runeq = "./DDcentEVI -s %s.sch -n %s -l AFRI_100files" % (feq,feq)
        subprocess.call("%s" % (runeq), shell=True)
        runbase = "./DDcentEVI -s %s.sch -n %s -e %s -l AFRI_100files" % (fbase,fbase,feq)
        subprocess.call("%s" % (runbase), shell=True)
    else:
        print "Appending the simulation of "+fexp+".sch to "+fbase+".bin"
    runexp = "./DDcentEVI -s %s.sch -n %s -e %s -l AFRI_100files" % (fexp,fexp,fbase)
    subprocess.call("%s" % (runexp), shell=True)
    runlis = "./DDClist100 %s %s outvars.txt" % (exp,exp)
    subprocess.call("%s" % (runlis), shell=True)
    # x = raw_input("Check for DayCent execution success (.lst creation), and press Enter/Return to continue")


### READ & EXECUTE RUNTABLE.CSV BY LINE
import csv
reader = csv.reader(open('runtable.csv', 'rb'))
print "Runtable:"
treatcount = 0
for row in reader:
    print row
    treatcount += 1
  #parse runtable
    study = row[0]
    site = row[1]
    treat = row[2]
    soil = row[3]
    NARRx = row[4]
    NARRy = row[5]
  #define directory & file name variables from runtable contents
    dirstudy = dirmain + "/validation_data/" + study
    filesite100 = site+".100"
    filewth = "NARR_"+NARRx+"_"+NARRy+".wth"
    filesoilsin = soil+".in"
    eq = site+"_eq"
    fileeq = eq+".sch"
    base = site+"_base"
    filebase = base+".sch"
    filebin = base+".bin"
    exp = site+"_"+treat
    fileexp = exp+".sch"
    filelist = (filesite100, filewth, filesoilsin, fileeq, filebase, fileexp)
  #move all necessary files into main directory
    os.chdir(dirstudy)
    for file in filelist:                #move all DayCent run files to main directory
        shutil.copy(file, dirmain)
    if bool(nospin) == True:                   #if append was selected, import appropriate .bin
        if not os.path.exists(dirmain+"/"+filebin):
            os.chdir(dirapp)
            shutil.copy(filebin, dirmain)
    # x = raw_input("Check for binary file to append, and press Enter/Return to continue")
  #call DDCentEVI function
    os.chdir(dirmain)
    os.rename(filesoilsin, "soils.in")
    os.rename(filewth, site+".wth")
    print "Simulating "+study+" at "+site+", treatment "+treat
    print "    using "+filesoilsin+" and "+filewth
    DDCentEVI(eq,base,exp) 
  #misc. file cleanup
    os.chdir(dirmain)
    os.remove(filesite100)                  #delete site.100
    os.remove("soils.in")                   #delete soils.in
    for file in glob.glob(os.path.join(dirmain, '*')):
        if file.endswith(".sch") or file.endswith(".wth"):
            os.remove(file)                 #delete .sch/.wth files from main directory
print


### ARCHIVE RESULTS, WORKING DIRECTORY CLEANUP
os.chdir(dirmain)
for file in glob.glob(os.path.join(dirmain, '*')):
    if file.endswith(".100") or file.endswith(".in") or file.endswith(".txt"):
        os.remove(file)                 #delete .100/.in/.txt files from main directory
if not os.path.exists(dirarch):
    os.makedirs(dirarch)                #create archive directory if doesn't exist
for file in glob.glob(os.path.join(dirmain, '*')):
    if file.endswith(".bin") or file.endswith(".lis") or file.endswith(".out"):
        shutil.move(file, dirarch)      #archive all .bin/.lis/.out files together


### IMPORT, LABEL & CONCATENATE .LIS FILES
os.chdir(dirarch)
import numpy as np
import glob
i = 1
print
print "Analyzing model runs for treatments:"
for file in glob.glob(os.path.join(dirarch, '*')):
    if file.endswith(".lis"):                        #for each .lis file in the archive 
        base=os.path.basename(file)
        filename = os.path.splitext(base)[0]         #split off the filename       
        print filename
        npdata = np.genfromtxt(file, skip_header=3)  #import .lis data as numpy array
        listdata = npdata.tolist()                   #convert numpy array to Python list
        for row in listdata:
            row.insert(0, filename)                  #add treatment ID to each entry
            row.append(0)                            #add a placeholder for measured yield
        if i == 1:
            table = listdata                         #initialize 'table' with first .lis file
        else:
            table = table+listdata                   #concatenate files
        i += 1
print


### DELETE REDUNDENT .LIS ENTRIES, CONVERT CRMVST TO YIELD, REINDEX YEARS
redun = True
row = 0
while row < (len(table)-1):                          #loop through the table
    for i in range(3):
        if table[row][i] != table[row+1][i]:         #if the first 4 elements are identical
            redun = False                            #from this row to the next
    if redun == True:
        del table[row+1]                             #delete the next row
    row += 1
c_conc = 0.45                                        #define biomass carbon concentration
for row in range(len(table)):
    crmvst = table[row][6]                           #extract crmvst
    year = table[row][1]
    Mgha = round((crmvst/c_conc)*(1/100.0), 3)       #gC/m2 -> MgdryBM/ha unit conversion
    table[row][6] = Mgha                             #replace crmvst with yield
    year = int(year)-1                               #round and index back 1 year
    table[row][1] = year                             #replace original year with reindexed
 

### IMPORT MEASURED YIELDS, JOIN TO MODEL RESULTS
os.chdir(dirmain)
import csv
yields = csv.reader(open('yields.csv', 'rb'))        #import yields.csv
tab = [[]]                         #list to receive measurements (all years of a treatment)
for row in yields:                 #convert each row of csv file values to a list element
    tab.append(row)
del tab[0]                         #delete the initialization row
yie = [[]]                         #new list to receive separate entries for every year
for row in range(len(tab)):        #loop through each treatment in tab[]
    year = 1990
    base = 1989
    treat = tab[row][0]                     #extract the treatment name
    while year <= 2013:                     #loop through every year w/in that treatment
        meas = float(tab[row][year-base])   #extract the associated yield measurement as a float
        if meas != 0.0:                     #if biomass was recorded that year    
            entry = [treat, year, meas, 0]  #create a treatment-year-yield-modeled(placeholder) list
            yie.append(entry)               #append to re-formatted 'measured' yields array
        year += 1
del yie[0]                                  #delete the initialization row
for measu in range(len(yie)):               #for each entry in 'measured' yields array
    for mod in range(len(table)):           #loop through every table entry
        if yie[measu][0]==table[mod][0] and yie[measu][1]==table[mod][1]:     #if treat+year match
            yie[measu][3] = table[mod][6]   #extract modeled yield, write to the placeholder       
for j in range(10):         ### cheated here; 10 is an arbitrary # of loops cause I didn't have logic figured out...
    i = 0
    while i < len(yie):                             
        if yie[i][3] == 0:
            del yie[i]                      #get rid of entries where no modeled data available
        i += 1
print "Comparison points:"
print "  (all yields in dry Mg/ha)"  
print "[treatment, year, measured yield, modeled yield]:"
for row in yie:
    print row
print


### remaining piece #3 add capability to save a results file


### ANALYZE & PLOT RESULTS
import matplotlib.pyplot as plt
meas =[[]]
mod = [[]]
lab = [[]]
for i in range(len(yie)):
    meas.append(yie[i][2])
    mod.append(yie[i][3])
    lab.append(yie[i][0])
del meas[0]
del mod[0]
del lab[0]
plt.plot([0,20], [0,20])
plt.plot(meas, mod, 'ro')
###turn on point labeling by un-commenting below
#for i in range(len(yie)):
#    plt.annotate(lab[i], xy = (meas[i], mod[i]), fontsize=7)
plt.xlabel('Measured switchgrass yield (dry Mg/ha)')
plt.ylabel('Modeled switchgrass yield (dry Mg/ha)')
plt.show()


### RUN SUMMARY
sec = round((time.time() - start), 2)
secpertreat = round(sec/treatcount, 2)
min = round(sec/60.0, 2)
sec = str(sec)
secpertreat = str(secpertreat)
min = str(min)
treatcount = str(treatcount)
if bool(nospin) == True:
    text = "appending *.bin files from archive "+tstamp+"."
else:
    text = "including full spin-ups."
print "Analysis complete."
print "It took "+min+" minutes total to run the "+treatcount+" treatments ("+secpertreat+" sec/treatment),"
print text
print