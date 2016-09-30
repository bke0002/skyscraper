import urllib
import scraperFunctions as scraperFunks
from bs4 import BeautifulSoup
import csv
import math
import time
from datetime import datetime

ROOTURL1 = "http://homedepot.ugc.bazaarvoice.com/1999aa/"
ROOTURL2 = "/reviews.djs?&format=embeddedhtml&page="
ROOTURL3 = "&scrollToTop=true&sort=submissionTime"
totalPages = 1

def scrapePage(productID, pageNumber, csvFile):
	# Make TCP Request
	request = urllib.urlopen(ROOTURL1 + productID + ROOTURL2 + str(pageNumber) + ROOTURL3)

	string = scraperFunks.prepareHTML(request)

	# Make soup with a string that is clean of bad characters
	soup = BeautifulSoup(string, "html.parser")
	prettyHTML = soup.prettify()

	# for some reason, missing an apostrophe in the wrong place did some weird things.
	# lets take care of that.
	# [WARNING]: prettyHTML will have extra stuff that isn't in soup.
	prettyHTML = prettyHTML.replace("\'http:=\"\"", "\'http:=\"\"\'")

	# Make BETTER soup with better html formatting
	soup = BeautifulSoup(prettyHTML, "html.parser")

	#find the total number of reviews
	if (pageNumber == 1):
		numReviews = soup.find('div', {'class', 'BVRRHistogramTitle'}).find('span', {'class', 'BVRRNumber'}).string.strip()
		print ("Total Number of Reviews: " + numReviews)
		if (numReviews <= 8):
			pages = 1
		else:
			pages = (math.floor((int(numReviews)-8) / 30)) + 2
			pages = int(pages)
		global totalPages 
		totalPages = pages
	
	# Find all the reviews (should be about 30-ish).
	allReviews = scraperFunks.findAllReviews(soup,"div","id","BVSubmissionPopupContainer")
	if (pageNumber == 1):
		j = 1
	else:
		j = (9 + (30 * (pageNumber - 2)))
	
	for review in allReviews:
		print("Review Number: " + str(j))
		
		nicknames = review.find('span',{'itemprop':'author'})
		print("Username: " + nicknames.string.strip())
		
		reviewDate = review.find('meta', {'itemprop':'datePublished'})
		dateString = reviewDate['content'][:-1]
		print ("Date: " + dateString)
		if (dateObj != -1):
			reviewDateObj = datetime.strptime(dateString, "%Y-%m-%d")
			if (reviewDateObj < dateObj):
				return False
		
		# Find all review information within the review container.
		reviewContainer = review.findAll('div',{'class':'BVRRReviewDisplayStyle5BodyWrapper'})

		# Gets review title from reviewContainer
		reviewTitle = review.find('span',{'itemprop':'name'})
		print("Review Title: " + reviewTitle.string.strip())

		reviewScore = review.find('span', {'itemprop' : 'ratingValue'})
		print("Review Score: " + reviewScore.string.strip())

		reviewText = review.find('div', { 'itemprop' : 'description' }).findAll('span', { 'class' : 'BVRRReviewText' } )
		
		#print("Review Test: ")
		#for paragraph in reviewText:		
			#print(paragraph.string.strip() + "\n")
			#print(paragraph.prettify())

		j = j + 1
		print("\n")

	return True
	#print(prettyHTML)

	#output = open("o.txt", "w")
	#output.write(prettyHTML)
	
# Start CSV doc.
csvFile = open("scraperResults.csv", 'wt')
csvWriter = csv.writer(csvFile)
try:
	lastDate = open("dateHolder.txt", 'r')
	date = lastDate.readline()
	if (date != ""):
		dateObj = datetime.strptime(date, "%Y-%m-%d")
	else:
		dateObj = -1
except IOError:
	dateObj = -1

start = time.time()
inFile = open("productIDs.txt", 'r')
for line in inFile:
	pagenum = 1
	print ("------------------Reviews for productID: " + line + "----------------------")
	while (pagenum <= totalPages):
		if (scrapePage(line, pagenum, csvWriter)):
			pagenum += 1
		else:
			break

end = time.time()
print("Elapsed time: " + str(end - start))















