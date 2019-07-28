### start server ###
# source venv/bin/activate
# python3 server.py

from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
# Extract image features
import glob
import cv2
from rgbhistogram import RGBHistogram
import numpy as np
from searchalgo import Searcher
# to dump our index to disk
# python 2.x
#import cPickle
# python 3.x
import _pickle as cPickle

db_connect = create_engine('sqlite:///chinook.db')
app = Flask(__name__)
api = Api(app)

class Employees(Resource):
    def get(self):
        conn = db_connect.connect() # connect to database
        query = conn.execute("select * from employees") # This line performs query and returns json result
        #self.send_header("Access-Control-Allow-Origin", "*");
        #self.send_header("Access-Control-Expose-Headers", "Access-Control-Allow-Origin");
        #self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, DELETE");
        #self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
        return {"employees": "123"}
        #return {'employees': [i[0] for i in query.cursor.fetchall()]} # Fetches first column that is Employee ID

class Tracks(Resource):
    def get(self):
        #postData = self.form
        #json = str(postData['param'].value)
        conn = db_connect.connect()
        query = conn.execute("select trackid, name, composer, unitprice from tracks;")
        #result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        #return jsonify(result)
        return jsonify({"employees": request.args.get('code')})

class Employees_Name(Resource):
    def get(self, employee_id):
        conn = db_connect.connect()
        query = conn.execute("select * from employees where EmployeeId =%d "  %int(employee_id))
        result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
        return jsonify(result)

class getFeatures(Resource):
    def get(self, filename):
        imagePath = glob.glob("/Users/speedkevin/python/search-engine/dataset/"+filename)
        imagePath = ''.join(imagePath)
        k = imagePath[imagePath.rfind("/") + 1:]
        image = cv2.imread(imagePath)
        # initialize the index dictionary to store our our quantifed
        # images, with the 'key' of the dictionary being the image
        # filename and the 'value' our computed features
        index = {}
        # initialize our image descriptor -- a 3D RGB histogram with
        # 8 bins per channel
        desc = RGBHistogram([8, 8, 8])
        features = desc.describe(image)
        index[k] = features
        features = [str(f) for f in features]
        return jsonify(features)
        #return jsonify(",".join(features))

class getProb(Resource):
    def get(self, filename, feature):
        feature = feature.split(',')
        queryFeatures = np.array(feature, np.float32)
        # load the index and initialize our searcher
        index = cPickle.loads(open("/Users/speedkevin/python/search-engine/stored-index/output.txt", "rb").read())
        # init search algorithm
        searcher = Searcher(index)
        #index = {filename: queryFeatures}
        ###### Run similarity algorithm ######
        results = searcher.search(queryFeatures)
        ranking = ""
        N = 10
        for j in range(0, N):
        	print(j)
        	print(results[j])
        	# grab the result (we are using row-major order) and
        	# load the result image
        	#(score, imageName) = results[j]
        	if j<N-1:
        	    ranking = ranking + results[j][1] + ","
        	else:
        	    ranking = ranking + results[j][1]
        return jsonify(ranking)
        #return jsonify(index.items())

api.add_resource(Employees, '/employees') # Route_1
api.add_resource(Tracks, '/tracks') # Route_2
api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3
api.add_resource(getFeatures, '/getFeatures/<filename>')
api.add_resource(getProb, '/getProb/<filename>/<feature>')

# app.send_header("Access-Control-Allow-Origin", "*");
# app.send_header("Access-Control-Expose-Headers", "Access-Control-Allow-Origin");
# app.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");

if __name__ == '__main__':
     app.run(port='5002')
