from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import pymongo 
from datetime import datetime
import math 
import pandas as pd
from urllib.parse import urlparse, parse_qs

client = pymongo.MongoClient('mongobase', 27017)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world! ss ')

    def do_POST(self):

        # content_length = int(self.headers['Content-Length'])
        # body = self.rfile.read(content_length)
        self.send_response(200)
        # print('yolo')

        query=urlparse(self.path)
        print(query)
        self.end_headers()
        path=query.path.split('/')
        self._database=path[1]
        self._machinename=path[2]
        queries=parse_qs(query.query)
        self._values={key :queries[key][0] for key  in queries}
        print(self._values)


        self.handlevalues()

    def handlevalues(self) : 

        db=client[self._database]
        db['testcases'+self._machinename].insert_one(self._values)
        self._sensors=db['sensor'+self._machinename]
        recap=self.getrecap(self._values)
        db["recap"+self._machinename].insert_one(recap)

        print("#------------#")
        print ('machine name : '+self._machinename)
        print('database : '+ self._database)
        print(recap)

        





    def getpowers(self,times): 
        x=list(self._sensors.find({'target':'system','timestamp' :{'$gte':times['begin']  ,'$lte':times['end']}},projection=['rapl','timestamp']))
        conso= pd.DataFrame(x)
        sonde=next(iter(x[0]['rapl']['0']))
        conso['power']=conso['rapl'].apply(lambda row :math.ldexp( row['0'][sonde]  ['RAPL_ENERGY_PKG'],-32))
        warmup=conso[(conso["timestamp"]<=times["execution"]) & (conso  ["timestamp"]>times["warmup"] )]
        execution = conso[(conso["timestamp"]>times["execution"]) ]
        return warmup.loc[:,['timestamp','power']],execution.loc[:,['timestamp',    'power']],




    def getrecap(self,target):
        """require a row from the database and not a times object"""
        times=gettimes(target)
        warmuppowers,executionpowers=self.getpowers(times)
        return {'name': target['name'] 
                ,'warmup time': (int(target['execution'])-int(target['warmup'])) 
                ,'warmup energy': getenergy(warmuppowers)
                ,'execution time': (int(target['end'])-int(target['execution']) )
                ,'execution energy': getenergy(executionpowers),
                'id':target['id'],
               
               }


def gettimes(x):
    """convert the time stamps from int to datetame """
    l={}
    l['execution']=datetime.utcfromtimestamp(int(x['execution']))
    l['begin']=datetime.utcfromtimestamp(int(x['begin']))
    l['end']=datetime.utcfromtimestamp(int(x['end']))
    l['warmup']=datetime.utcfromtimestamp(int(x['warmup']))
    return l

def getenergy(powers):
    return powers['power'].sum()


httpd = HTTPServer(('0.0.0.0', 4443), SimpleHTTPRequestHandler)

httpd.serve_forever()
