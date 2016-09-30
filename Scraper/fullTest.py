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
j = 1

def scrapePage(productID, pageNumber, csvFile):
	global j
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
	
	for review in allReviews:
		#check the date of the review and compare it to 
		reviewDate = review.find('meta', {'itemprop':'datePublished'})
		dateString = reviewDate['content'][:-1]
		print ("Date: " + dateString)
		if (dateObj != -1):
			reviewDateObj = datetime.strptime(dateString, "%Y-%m-%d")
			if (reviewDateObj < dateObj):
				return False
		
		print("Review Number: " + str(j))
		
		nicknames = review.find('span',{'itemprop':'author'})
		print("Username: " + nicknames.string.strip())
		
		# Find all review information within the review container.
		reviewContainer = review.findAll('div',{'class':'BVRRReviewDisplayStyle5BodyWrapper'})

		# Gets review title from reviewContainer
		reviewTitle = review.find('span',{'itemprop':'name'})
		print("Review Title: " + reviewTitle.string.strip())

		reviewScore = review.find('span', {'itemprop' : 'ratingValue'})
		print("Review Score: " + reviewScore.string.strip())

		reviewTextSpans = review.find('div', { 'itemprop' : 'description' }).findAll('span', { 'class' : 'BVRRReviewText' } )
		
		print("Review Text: ")
		reviewText = ""
		for paragraph in reviewTextSpans:		
			print(paragraph.string.strip())
			reviewText = reviewText + paragraph.string.strip() + "\t"
		
		yesHelpful = review.find('a', {'title': 'helpful'})
		if (yesHelpful is not None):
			yesHelpful = yesHelpful.find('span', { 'class' : 'BVDINumber'} ).string.strip()
			print("How many people found this Helpful: " + yesHelpful)
		else:
			yesHelpful = "0"
		
		notHelpful = review.find('a', {'title': 'unhelpful'})
		if (notHelpful is not None):
			notHelpful = notHelpful.find('span', { 'class' : 'BVDINumber'} ).string.strip()
			print("How many people found this Not Helpful: " + notHelpful)	
		else:
			notHelpful = "0"
		print("\n")

		csvFile.writerow( (j, productID.encode('utf-8'), dateString.encode('utf-8'), reviewScore.string.encode('utf-8').strip(), reviewText.encode('utf-8').strip(), yesHelpful.encode('utf-8'), notHelpful.encode('utf-8')) )
		
		j = j + 1

	return True
	#print(prettyHTML)

	#output = open("o.txt", "w")
	#output.write(prettyHTML)
	
# Start CSV doc.
csvFile = open("scraperResults.csv", 'wb')
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















