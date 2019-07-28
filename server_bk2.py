### start server ###
# source venv/bin/activate
# python3 server.py
import os
from flask import Flask, request, redirect, url_for, flash
from flask import send_from_directory, render_template
from flask_restful import Resource, Api
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
# Django
# from django.shortcuts import render_to_response
from PIL import Image

# Database
#db_connect = create_engine('sqlite:///chinook.db')
client = MongoClient("mongodb://dejavu:855$Peed172@ds119476.mlab.com:19476/dejavu")
db = client.dejavu

app = Flask(__name__)
api = Api(app)

# Config
PORT = '5002'
PATH_DATASET_SELF_ORIGIN = './dataset/self-origin/'
PATH_DATASET_SELF = './dataset/self/'
PATH_DATASET_THEONE_ORIGIN = './dataset/theone-origin/'
PATH_DATASET_THEONE = './dataset/theone/'
DATASET_OUTPUT_FILE = './dataset/output.txt'

# Upload files
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['MESSAGE'] = ''

#@app.route('/upload/<dest>/<token>')
#def hello(token):
#    return render_template('upload-self.html', token=token, dest=dest)

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

@app.route('/upload-self/<token>', methods=['GET', 'POST'])
def upload_file2(token):
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
                file.save(os.path.join(PATH_DATASET_SELF_ORIGIN, filename))
                # Get features
                # features = getFeatures(filename)
                # Update db
                db.users.update_one(
                    {"line_userid": token},
                    {
                        "$set": {
                            "self.picture": filename
                        }
                    }
                )
                # Update init state

                # Crop image
                #imagePath = glob.glob(PATH_DATASET_SELF + filename)
                #imagePath = ''.join(imagePath)
                #img = cv2.imread(imagePath)
                #crop_img = img[int(x):int(y), int(width):int(height)]
                #print(type(crop_img))
                #print(type(file))
                img = Image.open(PATH_DATASET_SELF_ORIGIN + filename)
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
                crop.save(PATH_DATASET_SELF + filename, 'png')
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
        if app.config['MESSAGE']:
            html = '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File 請上傳格式為png/jpg/jpeg/gif格式的圖片。</h1>
            <form method=post enctype=multipart/form-data>
              <p><input type=file name=file required>
                 <input type=submit value=Upload>
            </form>
            ''' + app.config['MESSAGE']
            app.config['MESSAGE'] = ''
            return html
        else:
            return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File 請上傳格式為png/jpg/jpeg/gif格式的圖片。</h1>
            <form method=post enctype=multipart/form-data>
              <p><input type=file name=file required>
                 <input type=submit value=Upload>
            </form>
            '''

@app.route('/upload-theone/<token>', methods=['GET', 'POST'])
def upload_theone(token):
    if request.method == 'POST':
        #print(token)
        # check if the post request has the file part
        if 'file' not in request.files:
            app.config['MESSAGE'] = '檔案格式不符，請上傳格式為png/jpg/jpeg/gif格式的圖片。'
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            app.config['MESSAGE'] = '請選擇圖片。'
            return redirect(request.url)
        if file and allowed_file(file.filename):
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
                file.save(os.path.join(PATH_DATASET_THEONE, filename))
                # Get features
                # features = getFeatures(filename)
                # Update db
                db.users.update_one(
                    {"line_userid": token},
                    {
                        "$set": {
                            "theone.picture": filename
                        }
                    }
                )
                #print("After update")

                #flash('Upload success')
                app.config['MESSAGE'] = '上傳成功。'
                return redirect(request.url)
                #return redirect(url_for('uploaded_file', filename=filename))
        else:
            app.config['MESSAGE'] = '檔案格式不符，請上傳格式為png/jpg/jpeg/gif格式的圖片。'
            return redirect(request.url)
    else:
        if app.config['MESSAGE']:
            html = '''
            <!doctype html>
            <title>Upload new File 請上傳格式為png/jpg/jpeg/gif格式的圖片</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
              <p><input type=file name=file>
                 <input type=submit value=Upload>
            </form>
            ''' + app.config['MESSAGE']
            app.config['MESSAGE'] = ''
            return html
        else:
            return '''
            <!doctype html>
            <title>Upload new File 請上傳格式為png/jpg/jpeg/gif格式的圖片</title>
            <h1>Upload new File</h1>
            <form method=post enctype=multipart/form-data>
              <p><input type=file name=file>
                 <input type=submit value=Upload>
            </form>
            '''

class getTheOneFeatures(Resource):
    def get(self, filename):
        print(filename)
        #imagePath = glob.glob("/Users/speedkevin/python/search-engine/dataset/"+filename)
        imagePath = glob.glob(PATH_DATASET_SELF + filename)
        print(imagePath)
        imagePath = ''.join(imagePath)
        print(imagePath)
        k = imagePath[imagePath.rfind("/") + 1:]
        print(k)
        image = cv2.imread(imagePath)
        print(image)
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
        index = cPickle.loads(open(DATASET_OUTPUT_FILE, "rb").read())
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

api.add_resource(getTheOneFeatures, '/getTheOneFeatures/<filename>')
api.add_resource(getProb, '/getProb/<filename>/<feature>')

# app.send_header("Access-Control-Allow-Origin", "*");
# app.send_header("Access-Control-Expose-Headers", "Access-Control-Allow-Origin");
# app.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");

if __name__ == '__main__':
    port = int(os.environ.get('PORT', PORT))
    app.run(host='169.254.185.16', port=port)
