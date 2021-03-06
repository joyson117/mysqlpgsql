import re
import sys

filepath = sys.argv[1]
f = open(filepath,'r')

# a dictionary mapping MySQL datatypes to corresponding PostgreSQL datatypes
type_dict = {
'INTEGER':'MEDIUMINT',
'SERIAL':'MEDIUMINT AUTO_INCREMENT',
'REAL':'FLOAT',
'CHARACTER':'VARCHAR(100)',
'DOUBLE PRECISION':'DOUBLE',
'BYTEA':'BLOB',
'BOOLEAN':'BOOL',
'TIMESTAMP':'TIMESTAMP',
'TIME':'TIME'
}

# method to replace MySQL datatype with PostgreSQL datatype
def replaceDatatype(datatype):
	for key,value in type_dict.items():
		if(datatype.upper().startswith(key)):
			if(datatype.endswith(",")):
				return value + ","
			else:
				return value
	return datatype
		

flagtable=False; #inside create table
flaginsert=False; #inside insert into

# going line by line
pg=""
for line in f:
	if(line.startswith("--") or line.startswith("/*") or line.startswith("DROP TABLE") or line.startswith("LOCK") or line.startswith("UNLOCK")): #these lines are useless
		continue
	
	line = re.sub(r'//*.*/*/',"",line)
	line = line.strip()

	if(line.startswith("CREATE TABLE")):
		line = line.replace(".","_")
		flagtable = True
		pg = pg + "\n" + line
		continue
		
	if(line.startswith("PRIMARY KEY")):
		pg = pg + "\n" + line
		continue
	if(flagtable and (line.startswith("CONSTRAINT") or line.startswith("KEY"))):
		if(line.endswith(",")):pg=pg+","
		continue	
	if(line.startswith(")") and flagtable):
		flagtable = False;
		pg = pg + "\n"+ ");"
		continue
		
	if(flagtable):
		tokens = line.split(" ",2)
		columnname = tokens[0]
		datatype = tokens[1]
		
		try:
			constraint = tokens[2]
		except IndexError:
				constraint = '' 
		
		datatype = str(replaceDatatype(datatype))
		line = columnname + " " + datatype + " " + constraint
		pg = pg + "\n" + line
		continue
		
	
	if(line.startswith("COPY")):
		line = line.replace("COPY","INSERT INTO").replace("FROM stdin;","")
		line = line.replace(".","_")
		insertinto = line
		flaginsert = True
		continue
	
	if(flaginsert and line.startswith("\.")):
		
		flaginsert = False;
		pg = pg + "\n"
		continue
	
	if(flaginsert):
		tokens = line.split()
		pg = pg + "\n" +insertinto + ""
		line = "values("
		for t in tokens:
			if t.isnumeric() :
				line = line + t + ","
			else :
				line = line + "'" + t + "',"
		
		line = line + ");"
		line = line.replace(",)",")")
		pg = pg + "\n" + line;
		continue		
			


print(pg)
