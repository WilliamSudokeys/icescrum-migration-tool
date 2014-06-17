# -*- coding:Utf-8 -*-
#
#	Code to import features and stories from a csv file
#	Have a look to the Readme.txt file before using it
#	Author : william@sudokeys.com
#	Date : 06/2014
#

import csv
import MySQLdb

class StoriesReader:
	
	FEATURE_COL=0
	STORY_COL=1
	DESC_COL=3
	
	"""Parse a CSV Features and Stories file to extract them"""
	def __init__(self,fileToRead):
		self.dicoStoryDescription={}
		self.inputStream=csv.reader(fileToRead)
		
	def parseFile(self):
		if not len(self.dicoStoryDescription):
			print "Parsing file..."
			for line in self.inputStream:
				if line[StoriesReader.FEATURE_COL] not in ("","Feature","Features"):
					self.dicoStoryDescription[line[StoriesReader.FEATURE_COL],line[StoriesReader.STORY_COL]]=(line[StoriesReader.DESC_COL])
			return self.dicoStoryDescription
		else:
			print "Not parsing file, because already done"
		
		
	def printFeatures(self):
		if not len(self.dicoStoryDescription):
			self.parseFile()
		sortedList = self.dicoStoryDescription.keys()
		sortedList.sort()
		for k in sortedList:
			print "|Feature || Story| : |%s || %s| " % (k[0],k[1])



class MySqlAccess:
	
	""" Provide a MySQL access"""
	def __init__(self,host="projet.sudokeys.com",db_name="icescrum",pwd="37pefhx",un="root",port=3307):
		print("Initializing database connection...")
		self.DB_HOST=host
		self.DB_NAME=db_name
		self.DB_PW=pwd
		self.DB_UN=un
		self.DB_PORT=port
		self.DB_CONN=""
		self.DB_CUR=""

	def connect(self):
		print "Connecting database %s ..." % (self.DB_NAME)
		self.DB_CONN=MySQLdb.connect(host=self.DB_HOST,user=self.DB_UN,passwd=self.DB_PW,db=self.DB_NAME,port=self.DB_PORT)
	
	def execute_select(self,request):
		if not self.DB_CONN:
			self.connect()
		print "Executing [%s] " % (request)
		if not self.DB_CUR and self.DB_CONN:
			self.DB_CUR=self.DB_CONN.cursor()
		self.DB_CUR.execute(request)
		return self.DB_CUR.fetchall()
	
	def execute_insert(self,request):
		if not self.DB_CONN:
			self.connect()
		print "Executing [%s] " % (request)
		if not self.DB_CUR and self.DB_CONN:
			self.DB_CUR=self.DB_CONN.cursor()
		ret=self.DB_CUR.execute(request)
#		self.DB_CONN.commit()
		return ret
		
	def close(self):
		print "Closing link to db"
		if self.DB_CUR:
			self.DB_CUR.close()
		
class Icescrum:
	
	"""Write data (features and stories to icescrum data base"""
	#Special icescrum user (to own imported features)
	IMPORT_USER_ID=40
	
	def __init__(self, dblink):
		print "Initializing icescrum..."
		self.DB_LINK=dblink
		self.AVAILABLES_PROJETCS=[]
		self.PROJ_REF=None
	
	def printProjects(self):
		ret = self.DB_LINK.execute_select("""SELECT id,name,pkey FROM icescrum.icescrum2_product;""")
		for i in range(0,len(ret)):
			print ret[i]
			self.AVAILABLES_PROJETCS.append(ret[i][0])
	
	def setProject(self,ref):
		if long(ref) in self.AVAILABLES_PROJETCS:
			self.PROJ_REF=ref
		else:
			print "Project not found !"
			
	def writeFeatures(self, reader):
		if not self.PROJ_REF:
			print "No project to update !"
			return
		print "Reading last feature index..."
		ret = self.DB_LINK.execute_select("""SELECT uid FROM icescrum.icescrum2_feature WHERE backlog_id=%s ORDER BY uid DESC;""" % self.PROJ_REF)
		lastFeatureUid=1
		lastStoryUid=1
		if ret:
			lastFeatureUid = int(ret[0][0])+1
			print "next feature uid : %s" % (lastFeatureUid)
			
		print "Reading last story index"
		ret = self.DB_LINK.execute_select("""SELECT uid FROM icescrum.icescrum2_story WHERE backlog_id=%s ORDER BY uid DESC;""" % self.PROJ_REF)
		if ret:
			lastStoryUid = int(ret[0][0])+1
			print "next story uid : %s" % (lastStoryUid)
			
		print "Writing features and stories to icescrum..."
		if not reader:
			"No StoriesReader instanciate"
			return
		reader.parseFile();
		sortedList = reader.dicoStoryDescription.keys()
		sortedList.sort()
		lastWriteFeature=""
		lastInsertedId=0
		for k in sortedList:
			if(lastWriteFeature!=k[0]):
				req = "INSERT INTO icescrum.icescrum2_feature(name,uid,backlog_id,version,color,creation_date,date_created,last_updated,rank,type,value) VALUES(\"%s\",%s,%s,0,\"blue\",NOW(),NOW(),NOW(),%s,0,0)" % (k[0],lastFeatureUid,self.PROJ_REF,lastFeatureUid)
				ret = self.DB_LINK.execute_insert(req)
				ret = self.DB_LINK.execute_select("""SELECT LAST_INSERT_ID()""")
				if ret:
					lastInsertedId = int(ret[0][0])
					print "last inserted id : %s" % (lastInsertedId)
					
				lastFeatureUid = lastFeatureUid + 1
			lastWriteFeature=k[0]
			req = """INSERT INTO icescrum.icescrum2_story(name,uid,description,feature_id,backlog_id,version,creator_id,creation_date,date_created,execution_frequency,last_updated,rank,state,type,value) VALUES(\"%s\",%s,\"%s\",%s,%s,0,%s,NOW(),NOW(),1,NOW(),%s,1,0,0)""" % (k[1],lastStoryUid,reader.dicoStoryDescription[(k[0],k[1])],lastInsertedId,self.PROJ_REF,Icescrum.IMPORT_USER_ID,lastStoryUid)
			ret = self.DB_LINK.execute_insert(req)
			lastStoryUid = lastStoryUid + 1
		

if __name__=="__main__":
	
	try:
		link = MySqlAccess(host="projet.sudokeys.com",db_name="icescrum",pwd="37pefhx",un="root",port=3307)
		icescum = Icescrum(link)
		icescum.printProjects()
		
		try:
			ref=raw_input("Type the number of the project to import in : ")
		except Exception as ex:
			print "Error reading project number : ", ex
		else:
			icescum.setProject(ref)	
		
		#fileToParse="/Users/William/Documents/workspace_python/Icescrum/fileToParseSimple.csv"
		fileToParse="./fileToParse.csv"
		reader=None
		try:
			print "Opening %s" % fileToParse
			fileStream=open(fileToParse)
		except:
			print "Error opening file %s " % fileToParse
		else:
			reader=StoriesReader(fileStream)
			reader.printFeatures()
			fileStream.close()
		
		try:
			ok=raw_input("Would you like to continue ? [y/n] ")
		except Exception as ex:
			print "Error reading your choice : ", ex
		else:
			if ok in ("y","Y") and reader:
				icescum.writeFeatures(reader)
	except Exception as ex:
		print "Error : ",ex
	finally:
		if link:
			link.close()
