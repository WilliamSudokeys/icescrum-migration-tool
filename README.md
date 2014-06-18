icescrum-migration-tool
=======================

Icescrum migration tool

This program parse the CSV file to extract features, stories and stories description.
The purpose is to write them in Icescrum MySQL DB.

In order to work, a project must already exists on Icescrum. (PROJ_REF)
The "Import CSV" user must exists on Icescrum and must be added to the project.
This user is considered to have the ID 40. (IMPORT_USER_ID)
The file to import must be : 
 - in CSV format (separator : ',', delimiter '"')
 - encoded in the same charset as icescrum database (latin-1 (ISO8859-1))
 - called "fileToParse.csv"
 - in root directory of this script
 