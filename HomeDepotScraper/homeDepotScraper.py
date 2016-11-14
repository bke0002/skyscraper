import urllib
import scraperFunctions as scraperFunks
from bs4 import BeautifulSoup
from subprocess import call
import xml.etree.cElementTree as ET
import math
import time
from datetime import datetime, timedelta

# URLs for scraping
ROOTURL1 = "http://homedepot.ugc.bazaarvoice.com/1999aa/"
ROOTURL2 = "/reviews.djs?&format=embeddedhtml&page="
ROOTURL3 = "&scrollToTop=true&sort=submissionTime"
SEARCH_URL = "http://www.homedepot.com/s/"
# number of reviews of page 1 of HomeDepot
PAGE_ONE_REVIEWS = 8
# normal number of review per page for Home Depot
REVIEWS_PER_PAGE = 30
# Total number of pages always set to one, is updated for every Product Id
totalPages = 1

j = 1

def getReviewData(review, reviewDict):
	revID = review['id'][27:]
	reviewDict['key'] = revID

	# Get Review Username
	nicknames = review.find('span', {'itemprop': 'author'})
	reviewDict['username'] = nicknames.get_text().strip().encode("ascii", "ignore")

	# Gets review title
	reviewTitle = review.find('span', {'itemprop': 'name'})
	reviewDict['title'] = reviewTitle.get_text().strip().encode("ascii", "ignore")

	#Get Review Sub-rating values
	ratingHolder = review.find('div', {'class', 'BVRRReviewDisplayStyle5RatingWrapper'})
	subRatingHolder = ratingHolder.findAll('div', {'class': 'BVRRRating'})
	for item in subRatingHolder:
		label = item.find('div', {'class', 'BVRRLabel'}).string.strip()
		num = item.find('img', {'class', 'BVImgOrSprite'})
		if (label == 'Quality'):
			reviewDict['quality'] = num['title']
		elif (label == "Value"):
			reviewDict['value'] = num['title']
		elif (label == 'Ease of installation'):
			reviewDict['eoi'] = num['title']

	# Gets Overall review score
	reviewScore = review.find('span', {'itemprop': 'ratingValue'})
	reviewDict['rating'] = reviewScore.string.strip()

	# Gets review text
	reviewTextSpans = review.find('div', {'itemprop': 'description'}).findAll('span', {'class': 'BVRRReviewText'})
	# Reviews can be separated into multiple <spans> if the review used newline, put them into one string for output
	reviewText = ""
	for paragraph in reviewTextSpans:
		reviewText = reviewText + paragraph.string.strip() + "\t"
	# Remove any special characters that cannot be saved into csv file (non ascii (128))
	reviewDict['text'] = reviewText.strip().encode("ascii", "ignore")

	# Gets the number of people who marked the review as helpful (if none recorded outputs 0)
	yesHelpful = review.find('a', {'title': 'helpful'})
	if (yesHelpful is not None):
		reviewDict['helpful'] = yesHelpful.find('span', {'class': 'BVDINumber'}).string.strip()

	# Gets the number of people who marked the review as not helpful (if none recorded outputs 0)
	notHelpful = review.find('a', {'title': 'unhelpful'})
	if (notHelpful is not None):
		reviewDict['notHelpful'] = notHelpful.find('span', {'class': 'BVDINumber'}).string.strip()

	# Get the Response from Rheem if there is one
	responseClass = review.find('div', {'class': 'BVRRReviewClientResponseText'})
	if (responseClass is not None):
		response = review.find('span', {'class': 'BVRRPlainTextMarkup'})
		reviewDict['response'] = response.get_text().strip().encode("ascii", "ignore")

	# Get Recommended Product True or False
	recommended = review.find('div', {'class': 'BVRRReviewDisplayStyle5AdditionalWrapper'})
	recommended = recommended.find('div', {'class': 'BVRRRecommendedContainer'})
	try:
		recommended.a.extract().get_text()
	except:
		reviewDict['recommended'] = "No"

	# Get media indicator
	hasMedia = review.find('div', {'class': 'BVRRReviewDisplayStyle5Media'})
	if (hasMedia is not None):
		reviewDict['media'] = "Yes"

	#get link to review
	link = review.find('div', {'class': 'BVRRUserNicknameContainer'})
	try:
		link = link.a.extract()
		reviewDict['link'] = link['href']
	except:
		reviewDict['link'] =  SEARCH_URL + str(reviewDict['id'])
		
	return reviewDict	
	
# Main Scraper Function scrapes a single page of reviews
def scrapePage(productID, pageNumber, rootXML, savedDate, modelNumber, prodTitle, prodPrice):
	global j
	# Make TCP Request
	request = urllib.urlopen(ROOTURL1 + productID + ROOTURL2 + str(pageNumber) + ROOTURL3)

	# removes any output that cannot be processed by BeautifulSoup
	string = scraperFunks.prepareHTML(request)

	# Make soup with a string that is clean of bad characters
	soup = BeautifulSoup(string, "html.parser")
	prettyHTML = soup.prettify()

	# for some reason, missing an apostrophe in the wrong place did some weird things, lets take care of that.
	# [WARNING]: prettyHTML will have extra stuff that isn't in soup.
	prettyHTML = prettyHTML.replace("\'http:=\"\"", "\'http:=\"\"\'")

	# Make BETTER soup with better html formatting
	soup = BeautifulSoup(prettyHTML, "html.parser")

	if (not soup.find('div', {'class', 'BVRRHistogramTitle'})):
		return False  # There are no reviews for this product

	# find the total number of reviews
	if (pageNumber == 1):
		numReviews = soup.find('div', {'class', 'BVRRHistogramTitle'}).find('span',
																			{'class', 'BVRRNumber'}).string.strip()
		#print ("Total Number of Reviews: " + numReviews)
		if (numReviews <= PAGE_ONE_REVIEWS):
			pages = 1
		else:
			pages = (math.floor((int(numReviews) - PAGE_ONE_REVIEWS) / REVIEWS_PER_PAGE)) + 2
			pages = int(pages)
		global totalPages
		totalPages = pages

	# Find all the reviews (should be about 30-ish).
	allReviews = soup.find_all('div', {'class':'BVRRContentReview'})

	# parse through each review on page
	for review in allReviews:
		# Python Dictionary for all review Info with default values
		reviewDict = {'key': "", 'id': productID, 'productName': prodTitle, 'modelNumber': modelNumber, 
			'link': "", 'price': prodPrice, 'media': "No", 'recommended': "Yes", 'title': "", 'username': "",
			'notHelpful': "NA", 'helpful': "NA", 'text': "", 'date': "", 'rating': "", 
			'eoi': "0", 'quality': "0", 'value': "0", 'response': "No Response From Rheem" }	
		
		# check the date of the review and compare it to
		dateString = review.find('meta', {'itemprop': 'datePublished'})
		dateString = dateString['content'][:-1]
		if (savedDate != -1):
			reviewDateObj = datetime.strptime(dateString, "%Y-%m-%d")
			#if the review was outside the date range then every review after is also old 
			if (reviewDateObj < savedDate):
				return False  

		#review in range so save date
		reviewDict['date'] = dateString
		# get rest of review fields
		reviewDictionary = getReviewData(review, reviewDict)

		#write review to xml file (True is for isHomeDepot indicator)
		scraperFunks.writeReviewToXML(rootXML, reviewDictionary, True)
		
		#print for debugging purposes
		#	print single field
		#print("Review Title: " + reviewDict['title'])
		#	print all fields
		#for key,value in reviewDictionary.items():
			#print(str(key) + ": " + str(value))
		#print("\n")	

		j = j + 1  # increments the review key counter

	return True  # the review was inside the date range

start = time.time()
# Start xml file
rootXML = ET.Element("xmlToImport")

#call function that grabs all products from Homed Depot using search
productInfo = scraperFunks.getHDProductIDs()

# process the saved date from file (if exists)
date = scraperFunks.readDate("dateHolderHD.txt")

for item in productInfo:
	pagenum = 1
	# item = [0=productID, 1=productTitle, 2=modelNumber, 3=price]
	#print ("----------------Reviews for productID: " + productID + "-------------------\n")
	while (pagenum <= totalPages):
		if (scrapePage(item[0], pagenum, rootXML, date, item[2], item[1], item[3])):
			pagenum += 1
		else:
			break

# saves the total time the scraper took to run
end = time.time()
#print("Elapsed time: " + str(end - start))
#print("Total Number Reviews " + str(j))

# print the current date to file
newDateFile = open("dateHolderHD.txt", 'w')
newDateFile.write(str(datetime.now().date() - timedelta(days=14)))
newDateFile.close()

tree = ET.ElementTree(rootXML)
tree.write("scraperResultsHD.xml")

# call script to add file to Rheem's FTP server
#scraperFunks.uploadToFTP("ftpUploadScript.txt")