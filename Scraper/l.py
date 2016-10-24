import urllib
import scraperFunctions as scraperFunks
from bs4 import BeautifulSoup
from subprocess import call
import xml.etree.cElementTree as ET
import math
import time
from datetime import datetime, timedelta
import getLowesProducts as getProducts


URLTOAPPEND = "/reviews?offset="

# Review Counter (generates temporary review key will update to Review Key found in HomeDepot's HTML)
j = 1

# Main Scraper Function scrapes a single page of reviews
def scrapePage(productURL, offset, rootXML, productName, modelNumber, productID):
	global j
	# Make TCP Request
	request = urllib.urlopen(productURL + URLTOAPPEND + str(offset))

	#make beautiful soup object
	soup = BeautifulSoup(request, "html.parser")
	prettyHTML = soup.prettify()
	
	#get each individual review
	reviews = soup.find_all( 'div', { 'itemprop' : 'review' } )
	
	for review in reviews:
		#review identifier
		reviewId = review['data-reviewid']
		
		#reviewer username
		username = review.find('span', { 'itemprop' : 'author' } )
		username = username.get_text().strip().encode("ascii", "ignore")
		print("Username: " + username)
		
		#title of review
		reviewTitle = scraperFunks.findOneItem(review, 'h4', 'class', 'reviews-list-quote grid-60 clearfix v-spacing-medium')
		reviewTitle = reviewTitle.get_text().strip().encode("ascii", "ignore")
		if reviewTitle.startswith('"') and reviewTitle.endswith('"'):
			reviewTitle = reviewTitle[1:-1]
		
		#overall review rating
		reviewRating = review.find('meta', { 'itemprop' : 'ratingValue' } )
		reviewRating = reviewRating['content']
		
		#review date
		reviewDate = review.find('div', { 'class' : 'vertical-align-center padding-left-medium' } ).find('small', {'class': 'darkMidGrey'})
		reviewDate = reviewDate.get_text().strip()[-10:]
		print("Review Date: " + reviewDate)
		if (dateObj != -1):
			reviewDateObj = datetime.strptime(reviewDate, "%m/%d/%Y")
			if (reviewDateObj < dateObj):
				return False	#the review was outside the date range
		
		
		#is this product recommended
		recommended = review.find('i', {'class':'icon-check green'} )		
		isRecommended = False
		if (recommended is not None):
			isRecommended = True
		
		#how many people marked review helpful or not helpful
		helpfulAll = review.find_all('a', {'class':'js-review-vote'})
		helpful = "NA"
		notHelpful = "NA"
		if (len(helpfulAll) == 2):
			helpful = helpfulAll[0].find('span').get_text()
			notHelpful = helpfulAll[1].find('span').get_text()
		
		#review text body
		reviewText = review.find('p', { 'itemprop' : 'reviewBody' } )
		reviewText = reviewText.get_text().strip().encode("ascii", "ignore")
		
		pics = review.find('div', { 'class' : 'review-image' } )
		hasPics = False 
		if (pics is not None):
			hasPics = True

		
		#write entire review to csv file
		#csvFile.writerow( (j, productID, modelNumber, productName, reviewId, username, reviewTitle, reviewDate, reviewRating, str(isRecommended), helpful, notHelpful, reviewText, productURL) )
		
		#write review to xml file
		reviewTag = ET.SubElement(rootXML, "review")
		ET.SubElement(reviewTag, "key").text = reviewId
		ET.SubElement(reviewTag, "id").text = productID
		ET.SubElement(reviewTag, "rating").text = reviewRating
		ET.SubElement(reviewTag, "date").text = reviewDate
		ET.SubElement(reviewTag, "text").text = reviewText
		ET.SubElement(reviewTag, "helpful").text = helpful
		ET.SubElement(reviewTag, "notHelpful").text = notHelpful
		ET.SubElement(reviewTag, "modelNumber").text = modelNumber
		ET.SubElement(reviewTag, "productName").text = productName
		ET.SubElement(reviewTag, "username").text = username
		ET.SubElement(reviewTag, "title").text = reviewTitle
		ET.SubElement(reviewTag, "recommended").text = str(isRecommended)
		ET.SubElement(reviewTag, "link").text = productURL
		ET.SubElement(reviewTag, "pics").text = str(hasPics)
		

		j = j + 1
		
	print("------------------done with page-----------------------------")
	return True

	
# Start XML doc
rootXML = ET.Element("xmlToImport")

#read list of product reviews from file	
start = time.time()

#call function that grabs all products matching criteria
productInfo = getProducts.getProductInfo()

#process the saved date from file (if exists)
try:
	lastDate = open("dateHolder.txt", 'r')
	date = lastDate.readline()
	#j = int(lastDate.readline().strip())
	if (date != ""):
		dateObj = datetime.strptime(date, "%Y-%m-%d")

	else:
		dateObj = -1

	lastDate.close()	
except IOError:
	dateObj = -1

i = 1
for product in productInfo:
	# product = [0=productID, 1=productName, 2=productLink, 3=modelNumber, 4=numReviews]	
	offsetSt = 0
	numReviews = int(product[4])		
	print("***************** Product " + str(i) + " *****************************")
	# get all reviews for a given product
	while (offsetSt <= numReviews):
		if (scrapePage(product[2], offsetSt, rootXML, product[1], product[3], product[0])):
			offsetSt = offsetSt + 10
		else:
			break
	i = i + 1

#print the current date to file 
newDateFile = open("dateHolder.txt", 'w')
newDateFile.write(str(datetime.now().date() - timedelta(days=14)))
newDateFile.close()			
			
#saves the total time the scraper took to run			
end = time.time()
print("Elapsed time: " + str(end - start))

#close files
tree = ET.ElementTree(rootXML)
tree.write("scraperResults.xml")