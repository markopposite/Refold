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

msg =  """	
#####################################################################################
########################## Library of optional arguments ############################
#####################################################################################

### Arguments can be between 2 and 4 total, examples include:

user$ 'python script.py sheet.csv' 
# Will prompt to overwrite original sheet

user$ 'python script.py sheet.csv newsheet.csv'
# Will create a new spreadsheet w/ y/n column updated

user$ 'python script.py sheet.csv Users/name/directoryfor_png/'
# Will propmt to overwrite csv, or create a new one, and copy png's to a specified folder

user$ 'python script.py sheet.csv newsheet.csv Users/name/directoryfor_png/'
# No prompts, create updated spreadsheet, and copy png's to specified folder 

#####################################################################################
#####################################################################################
"""	

### Determine if a useable number of arguments were given
if len(sys.argv) <= 1:
	print 'Inadequate number of arguments were given, here are the possible options: '
	print msg
	exit()
elif len(sys.argv) >= 5:
	print msg	
	exit()

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
# vox = []
vac = []
for quarrel in grange:
	for str in quarrel:
		c = str.split('/')
		for i in c:
			if i.endswith('.fits'):
				vac.append(c[1])
vac_1 = []
for i in vac:
  if i not in vac_1:
    vac_1.append(i)



# print "VOX (parsed strings for rfifind)PARSED STRING FOR RFI FIND"
# print vox[:3]

##################################################################################
###### Build a system to run 'rfifind' and 'prepfold' in subdirectories #########
##################################################################################

print '\n...\n'
### print y/n column from infile
# print columns[6]

### Change directory to corresponding C1234+56 sub-directory
for item in paths:
	curr = item
	os.chdir(curr)
	### Set environment variables
	cmd1 = ('. /users/sransom/bin/zuul_envs.sh')
	os.system(cmd1)
	
	for key in dict2:
		if key in item:
			if dict2[key][5] is 'y':
				continue
			elif dict2[key][5] is 'n':
			### Create soft link, if already exists, move on to next one
				try:
					### Check that the filenames match the split strings and dictionary values
# 						for key in dict2:
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

					### Check if 'Processed' column is Y/N
				# 	if i in columns[6] is 'n':

					###Check that for all instances of the filename, they match and then run prepfold
					for var in doodad:
						for bug in vac_1:
							if var in bug:
								j = bug.split('.')
								g = j[0].split('_0001')
								h = g[0].split('_2bit')
# 									print h[0]
# 								print bug
								os.system('rfifind -o '+ h[0] + ' -time 1.0 -timesig 3.0 ' + bug)
								os.system('prepfold -p ' + dict2[key][2] + '-pd ' + dict2[key][3] + ' -dm ' + 
											dict2[key][4] + '-n 128 -nsub 128 -npart 60 -fine -nosearch -noxwin '
											'-mask ' + h[0] +'_rfifind.mask' + ' ' +bug) 
# 								print ('rfifind -o '+ h[0] + ' -time 1.0 -timesig 3.0 ' + bug)
# 								print ('prepfold -p ' + dict2[key][2] + '-pd ' + dict2[key][3] + ' -dm ' + 
# 										dict2[key][4] + '-n 128 -nsub 128 -npart 60 -fine -nosearch -noxwin ' 
# 										'-mask ' + h[0] +'_rfifind.mask' + ' ' +bug) 
								
								
								
								for i in dict2[key][5]:
									dict2[key][5] = 'y'
								continue

	dir = os.getcwd()
	os.chdir('..')

#####################################################################################
########################## Library of optional arguments ############################
#####################################################################################

if len(sys.argv) == 2:
	checkit = raw_input('overwrite csv file? y/n: ')
	if checkit is 'y':
		csv_file = sys.argv[1]
	elif checkit is 'n':
		namefile = raw_input('create a .csv filename (include ".csv"): ')
		os.system('touch '+namefile)
		csv_file = namefile
	else:	
		exit()
# 	os.system('cp C*/*.png /users/kmaracci/refold')			

elif len(sys.argv) > 2 and '.csv' in sys.argv[2]:
	csv_file = sys.argv[2]
# 	os.system('cp C*/*.png /users/kmaracci/refold')

elif len(sys.argv) > 2 and '/' in sys.argv[2]:
	csv_file = sys.argv[1]
	os.system('cp C*/*.png %s' % (sys.argv[3]))
	checkit = raw_input('overwrite csv file? y/n: ')
	if checkit is 'y':
		csv_file = sys.argv[1]
	elif checkit is 'n':
		namefile = raw_input('create a .csv filename (include ".csv"): ')
		os.system('touch '+namefile)
		csv_file = namefile
	else:	
		exit()

elif len(sys.argv) > 3 and '/' in sys.argv[3]:
	csv_file = sys.argv[2]
	os.system('cp C*/*.png %s' % (sys.argv[3]))

else:
	print 'Error: incorrect syntax or number of arguments'
# print csv_file

#######################################
#### 'Processed' y/n column update ####
#######################################

### update csv file to indicate if candidates are procesed
with open(csv_file,'wb') as x:
	writer = csv.writer(x)
	writer.writerow(['Filename,ID,Period (bary),Period (s),PD,DM,Processed'])
	for key, value in dict2.items():
		writer.writerow([key, dict2[key][1],dict2[key][6],dict2[key][2],dict2[key][3],
						dict2[key][4],dict2[key][5]])
     	 	
print '\n...'
print '\n\n\nFINISHED'

