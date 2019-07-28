from rgbhistogram import RGBHistogram
# parse arguments
import argparse
# to dump our index to disk
# python 2.x
# import cPickle
# python 3.x
import _pickle as cPickle
# to get the paths of the images we are going to index
import glob
import cv2

# construct the argument parser and parse the arguments
# The --dataset argument is the path to where our images are stored on disk and
# the --index option is the path to where we will store our index once it has been computed.
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required = True,
	help = "Path to the directory that contains the images to be indexed")
ap.add_argument("-i", "--index", required = True,
	help = "Path to where the computed index will be stored")
args = vars(ap.parse_args())

# initialize the index dictionary to store our our quantifed
# images, with the 'key' of the dictionary being the image
# filename and the 'value' our computed features
index = {}

# initialize our image descriptor -- a 3D RGB histogram with
# 8 bins per channel
desc = RGBHistogram([8, 8, 8])

# open the output index file for writing
output = open(args["index"], "w")

# use glob to grab the image paths and loop over them
# We use glob to grab the image paths and start to loop over our dataset.
for imagePath in glob.glob(args["dataset"] + "/*"):
	# extract our unique image ID (i.e. the filename)
	k = imagePath[imagePath.rfind("/") + 1:]

	# load the image, describe it using our RGB histogram
	# descriptor, and update the index
	image = cv2.imread(imagePath)
    ###### Extracting features: normalization ######
	features = desc.describe(image)
    # key:value = k:features
	index[k] = features
	#print(k)
	#print("&")
	#print(features)
	features = [str(f) for f in features]
	output.write("%s,%s\n" % (k, ",".join(features)))
	#print(index)
	#print(type(cPickle.dumps(index)))


# we are now done indexing our image -- now we can write our
# index to disk
#f = open(args["index"], "w")
#f = open(args["index"], "wb")
#f.write(cPickle.dumps(index))
#f.write(cPickle.dumps(index))
#f.close()
output.close();
