### Script for refolding pulsar candidates in the GBNCC folder
### __author(s)__   Mark Poe, Kaleb Maraccini  __

### Takes .csv file name as command line option; 'python script.py spreadsheet.csv'

from collections import defaultdict
from commands import *
from glob import glob
import csv, os, sys

### Define the current and parent directories
direct = os.getcwd()
parent = os.path.abspath(os.path.join(direct, os.pardir))

### Define and separate the ID column from a csv file into a list
infile = '%s' % sys.argv[1]
columns = defaultdict(list)
with open(infile) as f:
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
filename = columns[0]
period = columns[3]
pd = columns[4]
dm = columns[5]
ran = columns[6]
p_ms = columns[2]
for id in range(len(filename)):
    dict2[filename[id]] = [grange[id],csv_list[id],period[id],pd[id],dm[id],ran[id],p_ms[id]]

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
paths = glob(direct + '/*/')
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

##################################################################################
###### Build a system to run 'rfifind' and 'prepfold' in subdirectories #########
##################################################################################

print '\n...\n'

### Change directory to corresponding C1234+56 sub-directory
for item in paths:
	curr = item
	os.chdir(curr)
	### Set environment variables
	cmd1 = ('. /users/sransom/bin/zuul_envs.sh')
# 	os.system(cmd1)
	
	### Create soft link, if already exists, move on to next one
	try:
		### Check that the filenames match the split strings and dictionary values
		for key in dict2:
			for fire in dict2[key][0]:
				for vic in vac:
					if key in item: 
						if vic in fire:	
							### Soft link
							src = os.path.join(parent,fire)
							dst = os.path.join(direct,key,vic)
							os.symlink(src,dst)
	except:
		pass
	
	### Create list of items in current subdirectory
	doodad = []
	for beer in os.listdir(item):
		doodad.append(beer)

	### Check 'Ran'	column to see if candidate has been processed already	
	for i in dict2[key][5]:
		if i is 'n':
			### Check that for all instances of the filename, they match and then run rififind, and prepfold
			for var in doodad:
				for bug in flatlist:
					for thing in vac:							
						if var in bug:
							if thing in bug:
								os.system('rfifind -o '+ var + ' -time 1.0 -timesig 3.0 ' + thing)
								os.system('prepfold -p ' + dict2[key][2] + ' -pd ' + dict2[key][3] + ' -dm ' + 
										dict2[key][4] + ' -n 128 -nsub 128 -npart 60 -fine -nosearch -noxwin ' 
										'-mask ' + var +'_rfifind.mask' + ' ' +thing)
# 								print ('rfifind -o '+ var + ' -time 1.0 -timesig 3.0 ' + thing)
# 								print ('prepfold -p ' + dict2[key][2] + '-pd ' + dict2[key][3] + ' -dm ' + 
# 											dict2[key][4] + '-n 128 -nsub 128 -npart 60 -fine -nosearch -noxwin ' 
# 											'-mask ' + var +'_rfifind.mask' + ' ' +thing) 
								for i in dict2[key][5]:
									dict2[key][5] = 'y'

	dir = os.getcwd()
	os.chdir('..')

### Copy all .png files to User home folder
os.system('cp C*/*.png /users/kmaracci/refold')
# 	os.system('C*/*.png /users/mpoe/refold')

### Update the csv to indicate if specific candidates have been refolded
with open(infile,'wb') as x:
	writer = csv.writer(x)
	writer.writerow(['Filename,ID,Period (bary),Period (s),PD,DM,Processed'])
	for key, value in dict2.items():
		writer.writerow([key, dict2[key][1],dict2[key][6],dict2[key][2],dict2[key][3],
						dict2[key][4],dict2[key][5]])

### Enter two csv filenames as options, and the second one will be a copy of the first
### For testing and troubleshooting only
# outfile = '%s' % sys.argv[2]
# f1 = open(infile)
# with open(outfile,'wb') as f:
# 	writer = csv.writer(f)
# 	with open (infile,'r') as x:
# 		reader = csv.reader(x, delimiter = ',')
# 		for row in reader:
# 			writer.writerow(row)
     	 	
print '...'
print '\n\n\nFINISHED'
