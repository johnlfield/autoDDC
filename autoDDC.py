# Think about a structure where you specify whether you want to run a spinup or not,
# and all eq/spin/exp file names.  Perhaps prompt to delete existing .bin/.lis files in
# the working directory, and auto-archive the results with a date/time stamp.

# useful reference for interpreting values within strings: 
# http://ubuntuforums.org/showthread.php?t=786879

# overwrite = raw_input("Delete existing *.bin and *.lis files in the working directory (Y/N)? ")

eqname = raw_input("Name of the equilibrium schedule file: ")
basename = raw_input("Name of the base history schedule file: ")
expname = raw_input("Name of the experiment schedule file: ")
 
def DDCentEVI(eq,base,exp):
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

DDCentEVI(eqname,basename,expname)