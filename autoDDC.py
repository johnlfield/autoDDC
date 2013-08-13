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
dirarch = dirmain + "/Results/" + tstamp
print "Main directory:  ", dirmain
print "Archive directory:  ", dirarch
print

### IMPORT LIBRARY FILES
import glob
import shutil
for file in glob.glob(os.path.join(dirlib, '*')):
    if file.endswith(".100") or file.endswith(".in") or file.endswith(".txt"):
        shutil.copy(file, dirmain)      #copy all .100/.in/.txt files to main directory
os.chdir(dirmain)
os.remove('Milan.100')                  #excluding the Milan practice site.100 file

### READ RUNTABLE.CSV FILE BY LINE
import csv
reader = csv.reader(open('runtable.csv', 'rb'))
print "Runtable:"
for row in reader:
    print row
print

### DDCENTEVI/DDCENTLIST100 CALL
# runs an equilibrium-base-experiment sequence, and generates a final .lis output
# using 
print "If you wish to re-use the *.bin files from an existing spin-up sequence, please" 
print "specify the archive directory name (leave blank to run a new spin-up sequence):"
spin = raw_input()                                  # If r = True, Then no spinup
def DDCentEVI(eq,base,exp,spinup):
    print eq, base, exp
    import subprocess
    runeq = "./DDcentEVI -s %s.sch -n %s -l AFRI_100files" % (eq,eq)
    runbase = "./DDcentEVI -s %s.sch -n %s -e %s -l AFRI_100files" % (base,base,eq)
    runexp = "./DDcentEVI -s %s.sch -n %s -e %s -l AFRI_100files" % (exp,exp,base)
    runlis = "./DDClist100 %s %s outvars.txt" % (exp,exp)
    subprocess.call("%s" % (runeq), shell=True)
    subprocess.call("%s" % (runbase), shell=True)
    subprocess.call("%s" % (runexp), shell=True)
    subprocess.call("%s" % (runlis), shell=True)

# DDCentEVI(eqname,basename,expname,spin)

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