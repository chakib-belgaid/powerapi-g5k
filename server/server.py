from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import pymongo 
from datetime import datetime
import math 
import pandas as pd
import numpy as np
from urllib.parse import urlparse, parse_qs
from powerapi.formula import RAPLFormulaHWPCReportHandler, FormulaState
from powerapi.report import HWPCReport
import logging

# SERVERAADR='172.16.45.8'
SERVERAADR='mongobase'
SERVERPORT=27017
client = pymongo.MongoClient(SERVERAADR,SERVERPORT )
logger=logging.getLogger("server")

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world! ss ')

    def do_POST(self):
        
        query=urlparse(self.path)
        path=query.path.split('/')
        self._database=path[1]
        self._machinename=path[2]
        self._machine=testCase(self._machinename,database=self._database,serveraddr=SERVERAADR,serverport=SERVERPORT)
        queries=parse_qs(query.query)
        self._values=process({key :queries[key][0] for key  in queries})

        logger.info( "start processing ")
        logger.info(self._values)
        self.handlevalues()
        self.send_response(200)
        self.end_headers()

    def handlevalues(self) : 

        db=client[self._database]
        recap=self._machine.getrecap(self._values)
        logger.info(recap)
        db["recap"+self._machinename].insert_one(recap)
        logger.info("#------------#")
        # print ('machine name : '+self._machinename)
        # logger.info('database : '+ self._database)
        # logger.info(recap)

        


def process(x):
    """convert the time stamps from int to datetame """
    x['beginexecution']=datetime.utcfromtimestamp(float(x['beginexecution'].replace("_",".")))
    # x['begin']=datetime.utcfromtimestamp(float(x['begin'].replace("_",".")))
    # x['end']=datetime.utcfromtimestamp(float(x['end'].replace("_",".")))
    x['beginwarmup']=datetime.utcfromtimestamp(float(x['beginwarmup'].replace("_",".")))
    return x


class testCase(object): 
    """in general its just the name of the machine where we launched the test """
    def __init__ (self , testname,database='rapls2',serveraddr='172.16.45.8',serverport=27017): 
        self._client = pymongo.MongoClient(serveraddr, serverport)
        self._db=self._client[database]
        self._testname=testname 
        self._rapl=self._db['rapl'+self._testname]
        self._snmp=self._db['snmp'+self._testname]
        self._rapl.create_index([('timestamp',pymongo.ASCENDING)])
        self._formula_id = (None,)
        self._state = FormulaState(None, None, None, self._formula_id)
        self._handler = RAPLFormulaHWPCReportHandler(None)
        
    def gettimetamps(self,containername): 
        containerdata=list(self._rapl.find({'target':containername},projection=['timestamp']))
        begintime= containerdata[0]['timestamp']
        endtime=containerdata[-1]['timestamp']
        return begintime , endtime , len(containerdata)
    
    def _get_snmp(self,row): 
        x= self._snmp.find_one({'timestamp':math.floor(row['timestamp'].timestamp())})
        return x['power'] if x else 0

    def _process_power(self,row,socket,event):
        hwpc_report = HWPCReport.deserialize(row)
#         if event=='SNMP': 
#             return self._get_snmp(row)
        for i in self._handler._process_report(hwpc_report, self._state) : 
            if i.metadata['socket']== socket and i.metadata['event']==event : 
                return i.power
        return -1 
    
    
    def _get_headers(self,row):
        hwpc_report = HWPCReport.deserialize(row)
        x=self._handler._process_report(hwpc_report,self._state)
        l=[(i.metadata['socket'],i.metadata['event']) for i in x ]
#         if self._snmp.count()>0 :
#             l.append(('all','SNMP'))
        return l
    
    def getpowers(self,containername): 
        #get the power consumption of the system  between begin and end 
        begin , end,number = self.gettimetamps(containername) 
        return self.getpowersFromInterval(begin,end)

        
    def getpowersFromInterval(self,begin,end): 
        #get the power consumption of the system  between begin and end 
        x=list(self._rapl.find({'target':'all','timestamp' :{'$gte':begin,'$lte':end}})) 
        conso= pd.DataFrame(x)
        if len(x) <=0 : 
            return pd.DataFrame([{"powers_error":None }])
        headers=self._get_headers(x[0])
        for i in headers: 
            socket,event=i 
            title="powers_{}_{}".format(event.split('_')[-1],socket)
            conso[title]=conso.T.apply(lambda row: self._process_power(row,socket,event))

        return conso.drop(["_id","groups","sensor","target"],axis=1)
   
    def getenergy(self,containername):
        powers =self.getpowers(containername)
        powers=powers.loc[:,[ i for i in powers.columns if 'powers_' in i ]]
        return powers.apply(np.trapz)    
    
    def getenergyfromInterval(self,begin,end):
        powers =self.getpowersFromInterval(begin,end)
        powers=powers.loc[:,[ i for i in powers.columns if 'powers_' in i ]]
        return powers.apply(np.trapz)
       
   
    def getrecap(self,target):
        target["begin"] , target["end"],number = self.gettimetamps(target["target"])
        if target["begin"] > target["beginexecution"] : 
            target['beginwarmup']=target['beginexecution']=target["begin"]
        # warmupPowers = self.getpowersFromInterval(target['beginwarmup'],target['beginexecution'])
        # executionPowers = self.getpowersFromInterval(target['beginexecution'],target['end'])
        
#         meausres = self._db['recap'+self._testname].find(projection={'_id': False,'id':False})
        res=target
        res["executions number"]=number
        res['warmup time']= (target['beginexecution']-target['beginwarmup']).total_seconds() 
        res['execution time']= (target['end']-target['beginexecution'] ).total_seconds()
        warmupEnergies=self.getenergyfromInterval(target['beginwarmup'],target['beginexecution']) 
        executionEnergies=self.getenergyfromInterval(target['beginexecution'],target['end'])
        for i in warmupEnergies.keys(): 
            res['warmup_'+ i]=warmupEnergies[i]
        for i in executionEnergies.keys():
            res['execution_'+ i]=executionEnergies[i]     
        return res

httpd = ThreadingHTTPServer(('0.0.0.0', 4443), SimpleHTTPRequestHandler)

httpd.serve_forever()
