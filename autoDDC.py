### HEADER
print
print "This script automates a DayCent validation analysis sequence as specified in the" 
print "Windows-CSV-formatted 'runtable.csv'."
print
print "It assumes the following directory structure:" 
print "    Main directory: UNIX-exectutable DDcentEVI & DDClist100, runtable.csv"
print "    Subdirectory 'AFRI_100files': all necessary *.in & *.100, outvars.txt"
print "    Subdirectory 'Results': repository for archived analysis results"
print "    Subdirectory 'Validation_data: repository of directories for each study" 
print "         to be simulated containing all .sch, soils.in, and .wth files for" 
print "         all sites & treatments as named in runtable.csv"
print "         (Naming conventions: .sch files- site_eq, site_base, site_treatment;" 
print "           weather files- NARR_x_y.wth; soils files- mukey.in)"
print "    Subdirectory/subdirectory: this script (autoDDC.py)"
print

### SET WORKING DIRECTORY, DEFINE OTHER DIRECTORY PATHS
import os
import time
import datetime
tstamp = datetime.datetime.now().strftime("%Y-%m-%d,%H.%M")   #timestamp for archive name
print "Timestamp:  ", tstamp
abspath = os.path.abspath(__file__)     #get absolute path where script is located
dname = os.path.dirname(abspath)        #get associated directory only
os.chdir(dname)
os.chdir('..')
os.chdir('..')                          #navigate TWO directories higher
dirmain = os.getcwd()                   #define main working directory
dirlib = dirmain + "/AFRI_100files"     #define *.100 & *.IN library directory
dirarch = dirmain + "/Results/" + tstamp    #define archive directory
print "Please type a description for this analysis run to be use in plot titles"
print "and output file headers:"
descr = raw_input()                     #record test 'description'
print
print "Main directory:  ", dirmain
print "Archive directory:  ", dirarch
print
print "If you wish to re-use the *.bin files from an existing spin-up sequence, please" 
print "specify the archive directory name (leave blank to run a new spin-up sequence):"
nospin = raw_input()                        # If nospin = True, then no spinup
dirapp = dirmain + "/Results/" + nospin     #define appended .bin directory path
start = time.time()                         #start analysis run timer
print

### IMPORT NON .100 LIBRARY FILES
#note that we don't have to import .100 files, since we have specified a path
#for those in the DDCentEVI call
import glob
import shutil
for file in glob.glob(os.path.join(dirlib, '*')):
    if file.endswith(".in") or file.endswith(".txt"):
        shutil.copy(file, dirmain)    #copy all .in/.txt files to main directory

### DDCENTEVI/DDCENTLIST100 CALL
#if base.bin is found in the main/working directory, spinup sequence is skipped
#ensures that spinup isn't re-run for every treatment using it separately
def DDCentEVI(geq,gbase,gexp):   #'g' prefix added to parameters to avoid conflict with external variables
    import subprocess
    if not os.path.exists(dirmain+"/"+gbase+".bin"):     #if base.bin not found, run spinup
        print "Running full simulation sequence of "+geq+".sch, "+gbase+".sch, and "+gexp+".sch"
        runeq = "./DDcentEVI -s %s.sch -n %s -l AFRI_100files" % (geq,geq)  
        subprocess.call("%s" % (runeq), shell=True)      #execute DDcentEVI in Darwin for equilibrium
        runbase = "./DDcentEVI -s %s.sch -n %s -e %s -l AFRI_100files" % (gbase,gbase,geq)
        subprocess.call("%s" % (runbase), shell=True)    #execute DDcentEVI in Darwin for base
    else:
        print "Appending the simulation of "+gexp+".sch to "+gbase+".bin"
    runexp = "./DDcentEVI -s %s.sch -n %s -e %s -l AFRI_100files" % (gexp,gexp,gbase)
    subprocess.call("%s" % (runexp), shell=True)
    runlis = "./DDClist100 %s %s outvars.txt" % (exp,exp)
    subprocess.call("%s" % (runlis), shell=True)         #execute DDClist100 on experiment .bin output

### READ & EXECUTE RUNTABLE.CSV BY LINE
import csv
reader = csv.reader(open('runtable.csv', 'rb'))   #import runtable.csv as a list of lines
print "Runtable:"
treatcount = 0
for row in reader:
    print row
    treatcount += 1   #count the number of treatments read for runtime calcs
  #parse runtable
    study = row[0]
    site = row[1]
    treat = row[2]
    soil = row[3]
    NARRx = row[4]
    NARRy = row[5]
  #define directory & file name variables from runtable contents
  #naming convention: fsite = full file name derived from site variable
    dirstudy = dirmain+"/Validation_data/"+study
    fsite = site+".100"
    fwth = "NARR_"+NARRx+"_"+NARRy+".wth"
    fsoil = soil+".in"
    eq = site+"_eq"
    feq = eq+".sch"
    base = site+"_base"
    fbase = base+".sch"
    fbin = base+".bin"
    exp = site+"_"+treat
    fexp = exp+".sch"
    flist = (fsite, fwth, fsoil, feq, fbase, fexp)
  #move all necessary files into main directory
    os.chdir(dirstudy)
    for f in flist:                #move all DayCent run files to main directory
        shutil.copy(f, dirmain)
    if bool(nospin) == True:       #if append was selected, import appropriate .bin
        if not os.path.exists(dirmain+"/"+fbin):
            os.chdir(dirapp)
            shutil.copy(fbin, dirmain)
  #call DDCentEVI function
    os.chdir(dirmain)
    os.rename(fsoil, "soils.in")
    os.rename(fwth, site+".wth")
    print "Simulating "+study+" at "+site+", treatment "+treat
    print "    using "+fsoil+" and "+fwth
    DDCentEVI(eq,base,exp)         #call the previously-defined DDCENTEVI function
  #misc. file cleanup
    os.remove(fsite)               #delete site.100
    os.remove("soils.in")          #delete soils.in
    for f in glob.glob(os.path.join(dirmain, '*')):
        if f.endswith(".sch") or f.endswith(".wth"):
            os.remove(f)           #delete .sch/.wth files from main directory

### ARCHIVE RESULTS, WORKING DIRECTORY CLEANUP
for file in glob.glob(os.path.join(dirmain, '*')):
    if file.endswith(".in") or file.endswith(".txt"):
        os.remove(file)            #delete remaining .in/.txt files from main directory
if not os.path.exists(dirarch):
    os.makedirs(dirarch)           #create archive directory if doesn't exist
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
#decompose final datatable yie[]
treat = [[]]
year = [[]]
meas =[[]]
mod = [[]]
for i in range(len(yie)):
    treat.append(yie[i][0])
    year.append(yie[i][1])
    meas.append(yie[i][2])
    mod.append(yie[i][3])
del meas[0]
del mod[0]
del treat[0]
#generate datatable of averages across years for each treatment
treatuniq = set(treat)            #list unique treatments by converting to set
treatset = list(treatuniq)        #convert back to list format
measavgs = [[]]
modavgs = [[]]
for treat in treatset:            #for every unique treatment
    measset = [[]]
    modset = [[]]
    for i in range(len(yie)):     #loop through yie[] and list matching meas, mod results
        if yie[i][0] == treat:
            measset.append(yie[i][2])
            modset.append(yie[i][3])
    del measset[0]
    del modset[0]
    measavg = np.mean(measset)   #average across those lists
    modavg = np.mean(modset)
    measavgs.append(measavg)
    modavgs.append(modavg)
del measavgs[0]
del modavgs[0]
#compute annual, treatment-averaged RMSE values
def rmse(listmeas,listmod):
    sqerr = 0
    for i in range(len(listmeas)):
        sqerr += (listmod[i]-listmeas[i])**2
    return (sqerr/float(len(listmeas)))**0.5
RMSEannual = rmse(meas,mod)
RMSEavg = rmse(measavgs,modavgs)
#plot treatment averages
import matplotlib.pyplot as plt
plt.plot([0,25], [0,25])       
plt.plot(measavgs, modavgs, 'ro')
###turn on point labeling by un-commenting below
#for i in range(len(yie)):
#    plt.annotate(treatset[i], xy = (measavgs[i], modavgs[i]), fontsize=7)
plt.title(descr+", treatment averages")
plt.xlabel('Measured switchgrass yield (dry Mg/ha)')
plt.ylabel('Modeled switchgrass yield (dry Mg/ha)')
plt.text(2, 21, "RMSE = "+str(round(RMSEavg,3))+" Mg/ha")
os.chdir(dirarch)
plt.show()
sec = round((time.time() - start), 2)
plt.savefig('Mod-v-meas(averaged).png')
plt.close()
#plot individual years
plt.plot([0,25], [0,25])       
plt.plot(meas, mod, 'ro')
###turn on point labeling by un-commenting below
#for i in range(len(yie)):
#    plt.annotate(treat[i], xy = (meas[i], mod[i]), fontsize=7)
plt.title(descr+", annual results")
plt.xlabel('Measured switchgrass yield (dry Mg/ha)')
plt.ylabel('Modeled switchgrass yield (dry Mg/ha)')
plt.text(2, 21, "RMSE = "+str(round(RMSEannual,3))+" Mg/ha")
os.chdir(dirarch)
plt.show()
plt.savefig('Mod-v-meas(annual).png')

### RUN SUMMARY
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