# Fix chinese encoding
#encoding:utf-8

### start server ###
# source venv/bin/activate
# python3 server.py
import os
from flask import Flask, request, redirect, url_for, flash
from flask import send_from_directory, render_template
from flask_restful import Resource, Api
#from flask_images import resized_img_src
#from sqlalchemy import create_engine
# Link to db
from pymongo import MongoClient
from json import dumps
from flask_jsonpify import jsonify
# Extract image features
import glob
import numpy as np
from rgbhistogram import RGBHistogram
from searchalgo import Searcher
# OpenCV 2
import cv2
# to dump our index to disk
# python 2.x
#import cPickle
# python 3.x
import _pickle as cPickle
# pip3 install pillow, instead pip3 install PIL
from PIL import Image

# Database
#db_connect = create_engine('sqlite:///chinook.db')
client = MongoClient("mongodb://dejavu:855$Peed172@ds119476.mlab.com:19476/dejavu")
db = client.dejavu

PEOPLE_FOLDER = os.path.join('dataset', 'theone')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
#app.secret_key = 'monkey'
#images = Images(app)
api = Api(app)

# Config testing
# HOST = '169.254.89.26'
# PORT = '5002'
# Config production
HOST = '127.0.0.1'
PORT = '8000'

PATH_DATASET_SELF_ORIGIN = './dataset/self-origin/'
PATH_DATASET_SELF = './dataset/self/'
PATH_DATASET_THEONE_ORIGIN = './dataset/theone-origin/'
PATH_DATASET_THEONE = './dataset/theone/'
DATASET_OUTPUT_FILE = './dataset/output.csv'
THEONE_PHOTO_NUM = len([name for name in os.listdir(PATH_DATASET_THEONE) if os.path.isfile(os.path.join(PATH_DATASET_THEONE, name))])-2


# Upload files
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MESSAGE'] = ''

from bson.objectid import ObjectId
def update_pointer_path(db, path):
	db.paths.update_one({
	  '_id': ObjectId("5a6bc711f36d286a1cb478d3")
	},{
	  '$set': {
	    'path': path
	  }
	}, upsert=False)

def find_path():
	# Create all dirs already
	# Path to be created
	SELF_DIR_POINTER = db.paths.find_one({"_id": ObjectId("5a6bc711f36d286a1cb478d3")})
	for key, value in SELF_DIR_POINTER.items():
		if key == 'path':
			SELF_DIR_POINTER = value
			print("SELF_DIR_POINTER")
			print(SELF_DIR_POINTER)
	#SELF_DIR_POINTER = "./dataset/self/10/10/10"
	#if not os.path.exists(SELF_DIR_POINTER):
		#os.mkdir(SELF_DIR_POINTER)
	SELF_IMG_NUM = len([name for name in os.listdir(SELF_DIR_POINTER) if os.path.isfile(os.path.join(SELF_DIR_POINTER, name))])
	print("SELF_IMG_NUM")
	print(SELF_IMG_NUM)

	if SELF_IMG_NUM == 20:
		# Parse DIR_POINTER, A/B/C
		DIR_ARRAY = SELF_DIR_POINTER.split("/")
		DIR_A = int(DIR_ARRAY[0])
		DIR_B = int(DIR_ARRAY[1])
		DIR_C = int(DIR_ARRAY[2])
		if DIR_C == 99:
			if DIR_B == 99:
				if DIR_A == 99:
					# Save image to 99/99/99. Update pointer. Save image path.
					SELF_DIR_POINTER = "99/99/99/"
					update_pointer_path(db, SELF_DIR_POINTER)
					print("99/99/99")
					print(SELF_DIR_POINTER)
				else:
					# Save image to A+1/00/00. Update pointer. Save image path.
					SELF_DIR_POINTER = str(DIR_A+1) + "/10/10/"
					update_pointer_path(db, SELF_DIR_POINTER)
					print("A+1/10/10")
					print(SELF_DIR_POINTER)
			else:
				# Save image to A/B+1/00. Update pointer. Save image path.
				SELF_DIR_POINTER = str(DIR_A) + "/" + str(DIR_B+1) + "/10/"
				update_pointer_path(db, SELF_DIR_POINTER)
				print("A/B+1/10")
				print(SELF_DIR_POINTER)
		else:
			# Save image to A/B/C+1. Update pointer. Save image path.
			SELF_DIR_POINTER = str(DIR_A) + "/" + str(DIR_B) + "/" + str(DIR_C+1) + "/"
			update_pointer_path(db, SELF_DIR_POINTER)
			print("A/B/C+1")
			print(SELF_DIR_POINTER)
	else:
		# Save image to SELF_IMG_PATH. Update pointer. Save image path.
		print("SELF_DIR_POINTER")
		print(SELF_DIR_POINTER)

find_path()

@app.route("/")
def hello():
	return render_template('index.html')

@app.route('/img/<dest>/<filename>', methods=['GET', 'POST'])
def img(filename, dest):
    if request.method == 'GET':
        #full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return render_template('image.html', image_name = filename, dest = dest)
        #return send_from_directory('dataset/theone', filename)

@app.route('/show/<filename>/<dest>')
def send_image(filename, dest):
    return send_from_directory("dataset/" + dest, filename)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/<dest>/<token>', methods=['GET', 'POST'])
def upload_file(dest, token):
    if request.method == 'POST':
        #print(token)
        # check if the post request has the file part
        if 'file' not in request.files:
            print(request.files)
            app.config['MESSAGE'] = '檔案格式不符，請上傳格式為png/jpg/jpeg/gif格式的圖片。'
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            app.config['MESSAGE'] = '請選擇圖片。'
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print(request.form['x'])
            print(request.form['y'])
            print(request.form['width'])
            print(request.form['height'])
            print(request.form['rotate'])
            print(request.form['scaleX'])
            print(request.form['scaleY'])
            x = request.form['x']
            y = request.form['y']
            width = request.form['width']
            height = request.form['height']
            rotate = request.form['rotate']
            scaleX = request.form['scaleX']
            scaleY = request.form['scaleY']
            naturalWidth = request.form['naturalWidth']
            naturalHeight = request.form['naturalHeight']
            #print(request.files['file'])
            #print(file.filename)

            # filename = secure_filename(file.filename)
            #filename = file.filename
            #print(filename)
            #print(request.url)
            #cursor = db.users.find()
            #print(cursor)
            #for document in cursor:
            #    print(document)
            if db.users.find({"line_userid": token}).count() == 0:
                #print("1111")
                app.config['MESSAGE'] = '認證失敗。'
                return redirect(request.url)
            else:
                # Change file name as unique image name of all db
                filename = token
                # Save file
                if dest == 'self':
                    file.save(os.path.join(PATH_DATASET_SELF_ORIGIN, filename))
                    db.users.update_one(
                        {"line_userid": token},
                        {
                            "$set": {
                                "self.picture": filename
                            }
                        }
                    )
                else:
                    file.save(os.path.join(PATH_DATASET_THEONE_ORIGIN, filename))
                    db.users.update_one(
                        {"line_userid": token},
                        {
                            "$set": {
                                "theone.picture": filename
                            }
                        }
                    )
                # Get features
                # features = getFeatures(filename)
                # Update db

                # Update init state

                # Crop image
                #imagePath = glob.glob(PATH_DATASET_SELF + filename)
                #imagePath = ''.join(imagePath)
                #img = cv2.imread(imagePath)
                #crop_img = img[int(x):int(y), int(width):int(height)]
                #print(type(crop_img))
                #print(type(file))
                if dest == 'self':
                    img = Image.open(PATH_DATASET_SELF_ORIGIN + filename)
                else:
                    img = Image.open(PATH_DATASET_THEONE_ORIGIN + filename)
                print(img)
                print("int(rotate): ")
                print((int(rotate)+360)%360)
                # image orientation start with 0 in Python, but rotate depends on phone. We need to normalize image
                normalized_rotate = (int(rotate)+360)%360
                if normalized_rotate == 0:
                    box = (float(x), float(y), float(x)+float(width), float(y)+float(height))
                # crop if 90
                if normalized_rotate == 90:
                    box = (float(y), float(naturalHeight)-float(x)-float(width), float(y)+float(height), float(naturalHeight)-float(x))
                # crop if 180
                if normalized_rotate == 180:
                    box = (float(naturalWidth)-float(x)-float(width), float(naturalHeight)-float(y)-float(height), float(naturalWidth)-float(x), float(naturalHeight)-float(y))
                # crop if 270
                if normalized_rotate == 270:
                    box = (float(naturalWidth)-float(y)-float(height), float(x), float(naturalWidth)-float(y), float(x)+float(width))
                print(box)
                # then crop
                crop = img.crop(box)
                print(crop)
                # rotate to normal orientation as phone
                crop = crop.rotate(-int(rotate))
				# Save upload photo
                if dest == 'self':
                    crop.save(PATH_DATASET_SELF + filename, 'png')
                else:
                    crop.save(PATH_DATASET_THEONE + filename, 'png')
                #cv2.imshow("cropped", crop_img)
                #file = crop_img
                #file.save(os.path.join(PATH_DATASET_SELF, filename))


                #flash('Upload success')
                app.config['MESSAGE'] = '上傳成功。'
                return redirect(request.url)
                #return redirect(url_for('uploaded_file', filename=filename))
        else:
            app.config['MESSAGE'] = '檔案格式不符，請上傳格式為png/jpg/jpeg/gif格式的圖片。'
            return redirect(request.url)
    else:
        return render_template('upload.html', dest=dest, token=token)

class getTheOneFeatures(Resource):
    def get(self, filename):
        print("filename::")
        print(filename)
        #imagePath = glob.glob("/Users/speedkevin/python/search-engine/dataset/"+filename)
        imagePath = glob.glob(PATH_DATASET_THEONE + filename)
        print("imagePath::")
        print(imagePath)
        imagePath = ''.join(imagePath)
        print("imagePath::")
        print(imagePath)
        k = imagePath[imagePath.rfind("/") + 1:]
        print("k::")
        print(k)
        image = cv2.imread(imagePath)
        print("image::")
        print(image)
        # initialize the index dictionary to store our our quantifed
        # images, with the 'key' of the dictionary being the image
        # filename and the 'value' our computed features
        index = {}
        # initialize our image descriptor -- a 3D RGB histogram with
        # 8 bins per channel
        desc = RGBHistogram([8, 8, 8])
        # 7 bins per channel
        # desc = RGBHistogram([1, 1, 1])
        features = desc.describe(image)
        index[k] = features
        features = [str(f) for f in features]
        return jsonify(features)
        #return jsonify(",".join(features))

class getProb(Resource):
    def get(self, filename, feature):
        print("filename::")
        print(filename)
        print("feature::")
        print(feature)
        feature = feature.split(',')
        print("feature after split::")
        print(feature)
        queryFeatures = np.array(feature, np.float32)
        # , load the index and initialize our searcher ‚
        #print("open(DATASET_OUTPUT_FILE, rb).read()::")
        #print(open(DATASET_OUTPUT_FILE, "rb").read())
        #index = cPickle.loads(open(DATASET_OUTPUT_FILE, "rb").read())
        index = DATASET_OUTPUT_FILE;
        print("index::")
        print(index)
        # init search algorithm
        searcher = Searcher(index)
        print("searcher::")
        print(searcher)
        #index = {filename: queryFeatures}
        ###### Run similarity algorithm ######
        results = searcher.search(queryFeatures)
        print("results::")
        print(results)
        ranking = ""
        # path joining version for other paths
        print("THEONE_PHOTO_NUM::")
        print(THEONE_PHOTO_NUM)
        for j in range(0, THEONE_PHOTO_NUM):
        	print(j)
        	print(results[j])
        	# grab the result (we are using row-major order) and
        	# load the result image
        	#(score, imageName) = results[j]
        	if j<THEONE_PHOTO_NUM-1:
        	    ranking = ranking + results[j][1] + ","
        	else:
        	    ranking = ranking + results[j][1]
        return jsonify(ranking)
        #return jsonify(index.items())

api.add_resource(getTheOneFeatures, '/getTheOneFeatures/<filename>')
api.add_resource(getProb, '/getProb/<filename>/<feature>')

# app.send_header("Access-Control-Allow-Origin", "*");
# app.send_header("Access-Control-Expose-Headers", "Access-Control-Allow-Origin");
# app.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");

if __name__ == '__main__':
    port = int(os.environ.get('PORT', PORT))
    app.run(host=HOST, port=port)
