### Script for refolding pulsar candidates in the GBNCC folder
### __author(s): Mark Poe, Kaleb Maraccini __

#### Import relevant modules for the script
from collections import defaultdict
from commands import *
from glob import glob
import csv, os, sys

### Define and separate the ID column from a csv file into a list
columns = defaultdict(list)
with open('refold_test.csv') as f:
    reader = csv.reader(f)
    reader.next()
    for row in reader:
       for (i,v) in enumerate(row):
            columns[i].append(v)

### Iterate over the ID list and create searchable strings "GBNCC(..ID..)"
csv_list = columns[1]
str1 = '*/*GBNCC'
str2 = '*'
new_csv_list = [str1 + x + str2 for x in csv_list]

##################################################################################
### Create list, a dictionary, and output files from parent directory using ID's ###
##################################################################################

### Begin operations in parent directory
last_dir = ''
dir = r'//lustre/cv/projects/GBNCC/'
os.chdir(dir)

### Create a list of the .fits filetypes and output the .fits filenames (choose 'print')
l = []
for item in new_csv_list:
    filenames = getoutput('ls -r' +' '+ item)
    l.append(filenames)

### Create a dictionary ---> "filename(from csv)":"filename(corresponding .fits file)"
dict1 = {}
dict2 = {}
period = columns[3]
pd = columns[4]
dm = columns[5]
filename = columns[0]
for id in range(len(filename)):
    dict1[filename[id]] = l[id]
    dict2[filename[id]] = [l[id],csv_list[id],period[id],pd[id],dm[id]]

### End operations in parent directory
dir = os.getcwd()
os.chdir('..')
last_dir = os.getcwd()

##################################################################################
### Build subdirectories with csv filenames and parse strings for rfi command ####
##################################################################################

### Create subdirectories for each corresponding "C1234+56" filename
try:
	basedir = "/lustre/cv/projects/GBNCC/refold/"
	for id in filename:
		os.mkdir(os.path.join(basedir,id))
except:
	pass

### Create a list of the "C1234+56" subdirectories that are in the current directory
paths = glob('/lustre/cv/projects/GBNCC/refold/*/')
paths = [p[:-1] for p in paths]
	
### Define new variable for rfifind string input 
vox = []
vac = []
for str in l:
	c = str.split('/')
	d = c[1].split('.')
	e = d[0].split('_0001')
	f = e[0].split('_2bit')
	jag = f[0]
	grr = e[0]
	if '_2bit' in e[0]:
		v = jag
	else:
		v = grr
	vox.append(v)
	vac.append(c[1])	

##################################################################################
###### Build a system to run 'rfifind' and 'prepfold' in subdirectories #########
##################################################################################

### Perform soft link, and rfifind in the corresponding subdirectories
for item in paths:
	curr = item
	os.chdir(curr)
	cmd1 = ('/users/sransom/bin/zuul_envs.sh')
	os.system(cmd1) # env variables for GBNCC shell
	try:
		for key in dict1:
			for vic in vac:
				if key in item: 
					if vic in dict1[key]:	
						src = os.path.join('/lustre/cv/projects/GBNCC/',dict1[key])
						dst = os.path.join('/lustre/cv/projects/GBNCC/refold/',key,vic)
						os.symlink(src,dst)
	except:
		pass
		for var in vox:
			for thing in vac:
				if thing in src:
					if var in src:
						os.system('rfifind -o '+ var + ' -time 1.0 -timesig 3.0 ' + thing)
						#print ('rfifind -o '+ var + ' -time 1.0 -timesig 3.0 ' + thing)

		for thing in vac:
			for var in vox:
				if thing in src:
					if var in src:					
						os.system('prepfold -p ' + dict2[key][2] + ' -pd ' + dict2[key][3] + ' -dm ' + 
								dict2[key][4] + ' -n 128 -nsub 128 -npart 60 -fine -nosearch -noxwin ' 
								'-mask ' + var + '_rfifind.mask' + ' ' + thing)
	dir = os.getcwd()
	os.chdir('..')
print 'done'
