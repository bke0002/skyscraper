import urllib
import scraperFunctions as scraperFunks
from bs4 import BeautifulSoup
from subprocess import call
import csv
import math
import time
from datetime import datetime


#URL for Home Depot's main website
ROOTURL1 = "http://www.lowes.com/pd/"
ROOTURL2 = "reviews?offset="


# Total number of pages always set to one, is updated for every Product Id
totalPages = 1

# Review Counter (generates temporary review key will update to Review Key found in HomeDepot's HTML)
j = 1

# Main Scraper Function scrapes a single page of reviews
def scrapePage(productID, offset, csvFile):
	global j
	# Make TCP Request
	request = urllib.urlopen(ROOTURL1 + productID + ROOTURL2 + str(offset))

	soup = BeautifulSoup(request, "html.parser")
	prettyHTML = soup.prettify()
	
	output = open("lowesLastPage.txt", 'a')
	output.write(prettyHTML)
	output.close()
	
	reviews = soup.find_all( 'div', { 'itemprop' : 'review' } )
	
	for review in reviews:
		reviewId = review['data-reviewid']
		print(reviewId)
		
		username = review.find('span', { 'itemprop' : 'author' } )
		username = username.get_text().strip().encode("ascii", "ignore")
		print(username)
		
		
		reviewDate = review.find('div', { 'class' : 'vertical-align-center padding-left-medium' } ).find('small', {'class': 'darkMidGrey'})
		reviewDate = reviewDate.get_text().strip()[-10:]
		print(reviewDate)
		
		recommended = review.find('i', {'class':'icon-check green'} )		
		isRecommended = False
		if (recommended is not None):
			isRecommended = True
		print("Recommended Product? " + str(isRecommended))	
		
		helpfulAll = review.find_all('a', {'class':'js-review-vote'})
		helpful = "NA"
		notHelpful = "NA"
		if (len(helpfulAll) == 2):
			helpful = helpfulAll[0].find('span').get_text()
			notHelpful = helpfulAll[1].find('span').get_text()
			
		print("is Helpful? " + helpful)
		print("is not Helfpul? " + notHelpful)
		
		reviewText = review.find('p', { 'itemprop' : 'reviewBody' } )
		reviewText = reviewText.get_text().strip().encode("ascii", "ignore")
		print(reviewText)

		print("\n")
		
		csvFile.writerow( (j, reviewId, username, reviewDate, str(isRecommended), helpful, notHelpful, reviewText) )
		j = j + 1
	print("------------------done with page-----------------------------")


	
# Start CSV doc.
csvFile = open("scraperResults.csv", 'wb')
csvWriter = csv.writer(csvFile)

#read list of product reviews from file	
start = time.time()

productID = "Whirlpool-40-Gallon-6-Year-Short-Natural-Gas-Water-Heater/50397596/"
offsetSt = 810
while (offsetSt <= 819):
	scrapePage(productID, offsetSt, csvWriter)
	offsetSt = offsetSt + 10

#saves the total time the scraper took to run			
end = time.time()
print("Elapsed time: " + str(end - start))


#close files
csvFile.close()
