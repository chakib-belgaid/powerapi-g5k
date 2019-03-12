from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import pymongo 
from datetime import datetime
import math 
import pandas as pd
from urllib.parse import urlparse, parse_qs
from powerapi.formula import RAPLFormulaHWPCReportHandler, FormulaState
from powerapi.report import HWPCReport


# SERVERAADR='172.16.45.8'
SERVERAADR='mongobase'
SERVERPORT=27017
client = pymongo.MongoClient(SERVERAADR,SERVERPORT )

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world! ss ')

    def do_POST(self):

        self.send_response(200)
        query=urlparse(self.path)
        self.end_headers()
        path=query.path.split('/')
        self._database=path[1]
        self._machinename=path[2]
        self._machine=testCase(self._machinename,database=self._database,serveraddr=SERVERAADR,serverport=SERVERPORT)
        queries=parse_qs(query.query)
        self._values=process({key :queries[key][0] for key  in queries})
        print( "start processing ")
        self.handlevalues()

    def handlevalues(self) : 

        db=client[self._database]
        recap=self._machine.getrecap(self._values)
        # print(recap)
        db["recap"+self._machinename].insert_one(recap)
        # print("#------------#")
        # print ('machine name : '+self._machinename)
        # print('database : '+ self._database)
        # print(recap)

        


def process(x):
    """convert the time stamps from int to datetame """
    x['beginexecution']=datetime.utcfromtimestamp(int(x['beginexecution']))
    x['begin']=datetime.utcfromtimestamp(int(x['begin']))
    x['end']=datetime.utcfromtimestamp(int(x['end']))
    x['beginwarmup']=datetime.utcfromtimestamp(int(x['beginwarmup']))
    return x


class testCase(object): 
    """in general its just the name of the machine where we launched the test """
    def __init__ (self , testname,database='rapls2',serveraddr='172.16.45.8',serverport=27017): 
        self._client = pymongo.MongoClient(serveraddr, serverport)
        self._db=self._client[database]
        self._testname=testname 
        self._sensors=self._db['sensor'+self._testname]
        self._formula_id = (None,)
        self._state = FormulaState(None, None, None, self._formula_id)
        self._handler = RAPLFormulaHWPCReportHandler(None)
        
    def gettimetamps(self,containername): 
        containerdata=list(self._sensors.find({'target':containername},projection=['timestamp']))
        begintime= containerdata[0]['timestamp']
        endtime=containerdata[-1]['timestamp']
        return begintime , endtime 

    def _process_power(self,row,socket,event):
        hwpc_report = HWPCReport.deserialize(row)
        for i in self._handler._process_report(hwpc_report, self._state) : 
            if i.metadata['socket']== socket and i.metadata['event']==event : 
                return i.power
        return -1 
    
    def _get_headers(self,row):
        hwpc_report = HWPCReport.deserialize(row)
        x=self._handler._process_report(hwpc_report,self._state)
        return [(i.metadata['socket'],i.metadata['event']) for i in x ]
    
    def getpowersFromInterval(self,begin,end): 
        x=list(self._sensors.find({'target':'all','timestamp' :{'$gte':begin,'$lte':end}}))
        conso= pd.DataFrame(x)
        if len(x) <= 0 : 
            return conso
        
        headers=self._get_headers(x[0])
        for i in headers: 
            socket,event=i 
            title="{}_{}".format(event.split('_')[-1],socket)
            conso[title]=conso.T.apply(lambda row: self._process_power(row,socket,event))

        return conso.drop(["_id","groups","sensor","target"],axis=1)

    
    def getpowers(self,containername): 
        #get the power consumption of the system  between begin and end 
        begin , end = self.gettimetamps(containername) 
        x=list(self._sensors.find({'target':'all','timestamp' :{'$gte':begin,'$lte':end}}))
        conso= pd.DataFrame(x)

        headers=self._get_headers(x[0])
        for i in headers: 
            socket,event=i 
            title="{}_{}".format(event.split('_')[-1],socket)
            conso[title]=conso.T.apply(lambda row: self._process_power(row,socket,event))

        return conso.drop(["_id","groups","sensor","target"],axis=1)
   
    def getenergy(self,containername):
        powers =self.getpowers(containername)
        return powers.sum()
    
    def getrecap(self,target):
        warmupPowers = self.getpowersFromInterval(target['beginwarmup'],target['beginexecution'])
        executionPowers = self.getpowersFromInterval(target['beginexecution'],target['end'])
        
#         meausres = self._db['recap'+self._testname].find(projection={'_id': False,'id':False})
        res=target
        res['warmup time']= (target['beginexecution']-target['beginwarmup']).total_seconds() 
        res['execution time']= (target['end']-target['beginexecution'] ).total_seconds()
        warmupEnergies=warmupPowers.sum() 
        executionEnergies=executionPowers.sum() 
        for i in warmupEnergies.keys(): 
            res['warmup_'+ i]=warmupEnergies[i]
        for i in executionEnergies.keys():
            res['execution_'+ i]=executionEnergies[i]     
        return res

httpd = HTTPServer(('0.0.0.0', 4443), SimpleHTTPRequestHandler)

httpd.serve_forever()
