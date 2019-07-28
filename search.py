# import the necessary packages
from searchalgo import Searcher
import numpy as np
import argparse
import _pickle as cPickle
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required = True,
	help = "Path to the directory that contains the images we just indexed")
ap.add_argument("-i", "--index", required = True,
	help = "Path to where we stored our index")
args = vars(ap.parse_args())

# load the index and initialize our searcher
index = cPickle.loads(open(args["index"], "rb").read())
# init search algorithm
searcher = Searcher(index)

# loop over images in the index -- we will use each one as
# a query image
# query: image name A
# queryFeatures: features of image A
# index.items(): array of image name & features

for (query, queryFeatures) in index.items():
	print(type(index))
	print("=== HERE A =====")
	print(type(query))
	print(query)
	print("=== HERE B =====")
	print(type(queryFeatures))
	print(type(queryFeatures[0]))
	# perform the search using the current query
    ###### Run similarity algorithm ######
	results = searcher.search(queryFeatures)
	# load the query image and display it
	path = args["dataset"] + "/%s" % (query)
	queryImage = cv2.imread(path)
	cv2.imshow("Query", queryImage)
	#print("========")
	#print("query: %s" % (query))

	# initialize the two montages to display our results --
	# we have a total of 25 images in the index, but let's only
	# display the top 10 results; 5 images per montage, with
	# images that are 400x166 pixels

	# montageA = np.zeros((166 * 5, 400, 3), dtype = "uint8")
	#montageA = np.zeros((75 * 5, 499, 3), dtype = "uint8")
	#print(montageA)
	# montageB = np.zeros((166 * 5, 400, 3), dtype = "uint8")
	#montageB = np.zeros((75 * 5, 499, 3), dtype = "uint8")

	# loop over the top ten results
	for j in range(0, 10):
		print(j)
		# grab the result (we are using row-major order) and
		# load the result image
		(score, imageName) = results[j]
		path = args["dataset"] + "/%s" % (imageName)
		result = cv2.imread(path)
		#print(result)
		#print(type(result)) #numpy.ndarray
		#print(score)
		#print(type(score)) #numpy.float64
		#print("\t%d. %s : %.3f" % (j + 1, imageName, score))
		###### algorithm ######

		#######################

		# check to see if the first montage should be used
		#if j < 5:
			#print(j)
			#print(result.shape)
			#print(montageA[j * 166:(j + 1) * 166, :].shape)
			#montageA[j * 166:(j + 1) * 166, :] = result
			#montageA[75*j,] = result
		# otherwise, the second montage should be used
		#else:
			#montageB[(j - 5) * 166:((j - 5) + 1) * 166, :] = result
			#montageB[75*j,] = result

	# show the results
		#cv2.imshow("Results 0", results[0])
		#cv2.imshow("Results 1", results[1])
		#cv2.imshow("Results 2", results[2])
		#cv2.imshow("Results 6-10", montageB)
		#cv2.waitKey(0)
