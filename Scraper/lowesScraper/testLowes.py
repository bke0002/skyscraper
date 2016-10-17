import urllib
import scraperFunctions as scraperFunks
from bs4 import BeautifulSoup
from subprocess import call
import csv
import math
import time
from datetime import datetime
import getLowesProducts as getProducts


URLTOAPPEND = "/reviews?offset="

# Review Counter (generates temporary review key will update to Review Key found in HomeDepot's HTML)
j = 1

# Main Scraper Function scrapes a single page of reviews
def scrapePage(productURL, offset, csvFile, productName, modelNumber, productID):
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
		
		#write entire review to csv file
		csvFile.writerow( (j, productID, modelNumber, productName, reviewId, username, reviewTitle, reviewDate, reviewRating, str(isRecommended), helpful, notHelpful, reviewText, productURL) )
		
		j = j + 1
	print("------------------done with page-----------------------------")


	
# Start CSV doc.
csvFile = open("scraperResultsLowes.csv", 'wb')
csvWriter = csv.writer(csvFile)

#read list of product reviews from file	
start = time.time()

#call function that grabs all products matching criteria
productInfo = getProducts.getProductInfo()

i = 1
for product in productInfo:
	# product = [0=productID, 1=productName, 2=productLink, 3=modelNumber, 4=numReviews]	
	offsetSt = 0
	numReviews = int(product[4])		
	
	# get all reviews for a given product
	while (offsetSt <= numReviews):
			scrapePage(product[2], offsetSt, csvWriter, product[1], product[3], product[0])
			offsetSt = offsetSt + 10

#saves the total time the scraper took to run			
end = time.time()
print("Elapsed time: " + str(end - start))

#close files
csvFile.close()
