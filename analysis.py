import os
dir = '/Users/johnfield/Desktop/Switchgrass/Results/2013-08-13,21.59'
os.chdir(dir)


### IMPORT, LABEL & CONCATENATE .LIS FILES
import numpy as np
import glob
i = 1
print "Analyzing the data in:"
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


### DELETE REDUNDENT ENTRIES, CONVERT CRMVST TO YIELD, REINDEX YEARS
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
    

### IMPORT YIELDS, JOIN TO MODEL RESULTS
os.chdir('/Users/johnfield/Desktop/Switchgrass')
import csv
reader = csv.reader(open('yields.csv', 'rb'))        #import yields.csv
for row in reader:
    print reader
### can't get csv data to import correctly; stopping for the night


### remaining piece #1- transpose yields.csv into a format consistent with this concatenated data table
# yie = [[]]
# for row in range(len(yields)):
#     year = 1990
#     treat = yields[entry][0]
#     while year <= 2013:
#         entry = [treat, year]
#         row.append(entry)
#         year += 1
# print yie

### remaining piece #2- loop within a loop to match up measured & modeled, append measured to modeled where necessary
# for entry in range(len(yie)):                     #for each yield entry....
#     row = 0
#     while row < len(yie):                         #loop through every table entry
#         if table[row][1] == table[row+1][i]:            #if treatment, year match
#             #abc
#         row += 1

### remaining piece #3 add capability to save a results file

### remaining piece #4 add plotting (& plot saving capability)

### remaining piece #5 merge into existing working automation routine