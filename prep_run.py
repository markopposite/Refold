### Script for refolding pulsar candidates in the GBNCC folder
### __author(s): Mark Poe, Kaleb Maraccini __

### Takes .csv file name as command line option; 'python script.py spreadsheet.csv'

from collections import defaultdict
from commands import *
from glob import glob
import csv, os, sys

### Define the current and parent directories
direct = os.getcwd()
parent = os.path.abspath(os.path.join(direct, os.pardir))
# print parent
# print direct

### Define and separate the ID column from a csv file into a list
columns = defaultdict(list)
with open('%s' % sys.argv[1]) as f:
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
######### Create lists and a dictionary from parent directory using ID's #########
##################################################################################

### Begin operations in parent directory
last_dir = ''
dir = parent
os.chdir(dir)

### Create a list of the .fits filetypes and output the .fits filenames (choose 'print')
l = []
for item in new_csv_list:
    filenames = getoutput('ls -r' +' '+ item)
    l.append(filenames)

### Handle any items in l that have two instances, and place them in a list within l
grange = []
for jangle in l:
	if isinstance(jangle, basestring):
		jerk = jangle.split('\n')
		grange.append(jerk)

### All items from l including sublist items are in flatlist separately
flatlist = []
for sublist in grange:
	for item in sublist:
		flatlist.append(item)

### Create a dictionary ---> {(filename(from csv)):(.fits,id,period,pd,dm)}
dict2 = {}
period = columns[3]
pd = columns[4]
dm = columns[5]
filename = columns[0]
for id in range(len(filename)):
    dict2[filename[id]] = [grange[id],csv_list[id],period[id],pd[id],dm[id]]
# print dict2

### End operations in parent directory
dir = os.getcwd()
os.chdir('..')
last_dir = os.getcwd()

##################################################################################
### Build subdirectories with csv filenames and parse strings for command line ###
##################################################################################

### Create subdirectories for each corresponding "C1234+56" filename
try:
	basedir = direct
	for id in filename:
		os.mkdir(os.path.join(basedir,id))
except:
	pass

### Create a list of the "C1234+56" subdirectories that are in the current directory
paths = glob(direct +'/*/')
paths = [p[:-1] for p in paths]
	
### Split strings appropriately for use in rfifind and prepfold commands
vox = []
vac = []
for quarrel in grange:
	for str in quarrel:
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
# print vox
# print vac

##################################################################################
####### Build a system to run 'rfifind' and 'prepfold' in subdirectories #########
##################################################################################

### Change directory to corresponding C1234+56 sub-directory
for item in paths:
	curr = item
	os.chdir(curr)
	### Set environment variables
	cmd1 = ('. /users/sransom/bin/zuul_envs.sh')
	os.system(cmd1) # env variables for GBNCC shell
	
	### Create soft link, if already exists, move on to next one
	### Check that the filenames match the split strings and dictionary values
	try:
		for key in dict2:
			for fire in dict2[key][0]:
				for vic in vac:
					if key in item: 
						if vic in fire:	
							### Soft link
							src = os.path.join(parent,fire)
							dst = os.path.join(direct,key,vic)
							print src
							print dst
							os.symlink(src,dst)
	except:
		pass

	### Create list of items in current subdirectory
	doodad = []
	for beer in os.listdir(item):
		doodad.append(beer)
	
	### Check that for all instances of the filename, they match and run rififind
	for var in doodad:
		for bug in flatlist:
			if var in bug:
				for thing in vac:
					if thing in bug:
						if var in bug:
							os.system('rfifind -o '+ var + ' -time 1.0 -timesig 3.0 ' + thing)
# 							print ('rfifind -o '+ var + ' -time 1.0 -timesig 3.0 ' + thing)

	### Check that for all instances of the filename, they match and run prepfold
	for var in doodad:
		for bug in flatlist:
			if var in bug:
				for thing in vac:
					if thing in bug:
						if var in bug:
							os.system('prepfold -p ' + dict2[key][2] + '-pd ' + dict2[key][3] + ' -dm ' + 
									dict2[key][4] + '-n 128 -nsub 128 -npart 60 -fine -nosearch -noxwin ' 
									'-mask ' + var +'_rfifind.mask' + ' ' +thing)
# 							print ('prepfold -p ' + dict2[key][2] + '-pd ' + dict2[key][3] + ' -dm ' + 
# 									dict2[key][4] + '-n 128 -nsub 128 -npart 60 -fine -nosearch -noxwin ' 
# 									'-mask ' + var +'_rfifind.mask' + ' ' +thing) 
	dir = os.getcwd()
	os.chdir('..')



print '\n\n\nFINISHED'
