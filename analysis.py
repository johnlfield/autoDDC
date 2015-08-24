import os
dir = '/Users/johnfield/Desktop/Switchgrass/Results/2013-08-14,10.06'
os.chdir(dir)

###Experimenting with pull request
###Experimenting some more
### IMPORT, LABEL & CONCATENATE .LIS FILES
import numpy as np
import glob
i = 1
print
print "Analyzing model runs for treatments:"
for file in glob.glob(os.path.join(dir, '*')):
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
os.chdir('/Users/johnfield/Desktop/Switchgrass')
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
