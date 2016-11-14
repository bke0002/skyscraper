import urllib
import scraperFunctions as scraperFunks
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
import math
import time
from datetime import datetime, timedelta

# set sort Method and direction so we get most recent reviews first (used with review date in scraper)
URLTOAPPEND = "/reviews?sortMethod=SubmissionTime&sortDirection=desc&offset="
REVIEWS_PER_PAGE = 10

# Review Counter (generates temporary review key will update to Review Key found in HomeDepot's HTML)
j = 1

def getReviewData(review, reviewDict):
	#review identifier
	reviewDict['key'] = review['data-reviewid']
	
	#reviewer username
	username = review.find('span', { 'itemprop' : 'author' } )
	reviewDict['username'] = username.get_text().strip().encode("ascii", "ignore")
	
	#title of review
	reviewTitle = review.find('h4', {'class':'reviews-list-quote grid-60 clearfix v-spacing-medium'})
	reviewTitle = reviewTitle.get_text().strip().encode("ascii", "ignore")
	if reviewTitle.startswith('"') and reviewTitle.endswith('"'):
		reviewDict['title'] = reviewTitle[1:-1]
	else:
		reviewDict['title'] = reviewTitle
	
	#overall review rating
	reviewRating = review.find('meta', { 'itemprop' : 'ratingValue' } )
	reviewDict['rating'] = reviewRating['content']
	
	#is this product recommended
	recommended = review.find('i', {'class':'icon-check green'} )		
	if (recommended is not None):
		reviewDict['recommended'] = "Yes"
	
	#how many people marked review helpful or not helpful
	helpfulAll = review.find_all('a', {'class':'js-review-vote'})
	if (len(helpfulAll) == 2):
		reviewDict['helpful'] = helpfulAll[0].find('span').get_text()
		reviewDict['notHelpful'] = helpfulAll[1].find('span').get_text()
	
	#review text body
	reviewText = review.find('p', { 'itemprop' : 'reviewBody' } )
	reviewDict['text'] = reviewText.get_text().strip().encode("ascii", "ignore")
	
	pics = review.find('div', { 'class' : 'review-image' } )
	if (pics is not None):
		reviewDict['media'] = "Yes"
	

# Main Scraper Function scrapes a single page of reviews
def scrapePage(productURL, offset, rootXML, savedDate, productName, modelNumber, productID, price):
	global j
	# Make TCP Request
	request = urllib.urlopen(productURL + URLTOAPPEND + str(offset))

	#make beautiful soup object
	soup = BeautifulSoup(request, "html.parser")
	prettyHTML = soup.prettify()
	
	#get each individual review
	reviews = soup.find_all( 'div', { 'itemprop' : 'review' } )
	
	for review in reviews:
		# Python Dictionary for all review Info
		reviewDict = {'key': "", 'id': productID, 'productName': productName, 'modelNumber': modelNumber, 
			'link': productURL, 'price': price, 'media': "No", 'recommended': "No", 'title': "", 'username': "",
			'notHelpful': "NA", 'helpful': "NA", 'text': "", 'date': "", 'rating': "" }
	
		#review date (Used to optimize scraper)
		reviewDate = review.find('div', { 'class' : 'vertical-align-center padding-left-medium' } ).find('small', {'class': 'darkMidGrey'})
		reviewDate = reviewDate.get_text().strip()[-10:]
		if (savedDate != -1):
			reviewDateObj = datetime.strptime(reviewDate, "%m/%d/%Y")			
			#if the review was outside the date range then every review after is also old 
			if (reviewDateObj < savedDate):
				return False
			else:
				#review in range, so save date		
				reviewDict['date'] = reviewDate	
				#get rest of review data
				getReviewData(review, reviewDict)

		#write review to xml file (False is for isHomeDepot indicator)
		scraperFunks.writeReviewToXML(rootXML, reviewDict, False)				
		
		
		
		#print for debugging purposes
		#	print single field
		#print("Review Title: " + reviewDict['title'])
		#	print all fields
		#for key,value in reviewDict.items():
		#	print(key + ": " + value)
		#print("\n")	

		j = j + 1
		
	return True

start = time.time()	
# Start XML doc
rootXML = ET.Element("xmlToImport")

#call function that grabs all products matching criteria (from scraperFunctions Lowe's section)
productInfo = scraperFunks.getProductInfo()

#process the saved date from file (if exists)
date = scraperFunks.readDate("dateHolderLowes.txt")

i = 1
for product in productInfo:
	# product = [0=productID, 1=productName, 2=productLink, 3=modelNumber, 4=numReviews, 5=price]	
	offsetSt = 0
	numReviews = int(product[4])		
	#print("***************** Product " + str(i) + " *****************************")
	# get all reviews for a given product
	while (offsetSt <= numReviews):
		if (scrapePage(product[2], offsetSt, rootXML, date, product[1], product[3], product[0], product[5])):
			offsetSt = offsetSt + REVIEWS_PER_PAGE
		else:
			break
	i = i + 1

#print the current date to file 
newDateFile = open("dateHolderLowes.txt", 'w')
newDateFile.write(str(datetime.now().date() - timedelta(days=14)))
newDateFile.close()			
			
#saves the total time the scraper took to run			
end = time.time()
#print("Elapsed time: " + str(end - start))

#publish xml files
tree = ET.ElementTree(rootXML)
tree.write("scraperResults.xml")

#call script to add file to Rheem's FTP server (with filename of script)
#scraperFunks.uploadToFTP("ftpUploadLowes.txt")