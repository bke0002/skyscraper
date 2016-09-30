import urllib
import scraperFunctions as scraperFunks
from bs4 import BeautifulSoup
import csv

ROOTURL1 = "http://homedepot.ugc.bazaarvoice.com/1999aa/"
ROOTURL2 = "/reviews.djs?dir=asc&format=embeddedhtml&page="
ROOTURL3 = "&scrollToTop=true&sort=submissionTime"

def scrapePage(productID, pageNumber, csvFile):
	# Make TCP Request
	request = urllib.urlopen(ROOTURL1 + productID + ROOTURL2 + str(pageNumber) + ROOTURL3)

	# Find where our reviews are located in BazaarVoice JavaScript
	count = 1
	for line in request.readlines():
		if count == 9: 
			index = line.index("SourceID")
			string = line[index + 11:]
			string = string[:len(string) - 6]
		count += 1

	# Remove bad characters
	string = string.replace("\\/","/")
	string = string.replace("\\\"","")
	string = string.replace(chr(ord(u'\xbd')),"") # found this odd character "HALFWIDTH HANGUL LETTER PHIEUPH"
	string = string.replace(chr(ord(u'\xc2')),"") # This one looks like a T.

	# Make soup with a string that is clean of bad characters
	soup = BeautifulSoup(string, "html.parser")
	prettyHTML = soup.prettify()

	# for some reason, missing an apostrophe in the wrong place did some weird things.
	# lets take care of that.
	# [WARNING]: prettyHTML will have extra stuff that isn't in soup.
	prettyHTML = prettyHTML.replace("\'http:=\"\"", "\'http:=\"\"\'")

	# Make BETTER soup with better html formatting
	soup = BeautifulSoup(prettyHTML, "html.parser")

	# Find all the reviews (should be about 30-ish).
	allReviews = scraperFunks.findAllReviews(soup,"div","id","BVSubmissionPopupContainer")
	j = 1
	for review in allReviews:
		print("Review Number: " + str(j))
		
		nicknames = review.find('span',{'itemprop':'author'})
		print("Username: " + nicknames.string.strip())
		
		# Find all review information within the review container.
		reviewContainer = review.findAll('div',{'class':'BVRRReviewDisplayStyle5BodyWrapper'})

		# Gets review title from reviewContainer
		reviewTitle = review.find('span',{'itemprop':'name'})
		print("Review Title: " + reviewTitle.string.strip())

		reviewScore = review.find('span', {'itemprop' : 'ratingValue'})
		print(reviewScore.prettify())
		print("Review Score: " + reviewScore.string.strip())

		reviewText = review.find('div', { 'itemprop' : 'description' }).findAll('span', { 'class' : 'BVRRReviewText' } )
		
		#print("Review Test: ")
		for paragraph in reviewText:		
			#print(paragraph.string.strip() + "\n")
			print(paragraph.prettify())

		j = j + 1


	#print(prettyHTML)

	#output = open("o.txt", "w")
	#output.write(prettyHTML)
	
# Start CSV doc.
csvFile = open("scraperResults.csv", 'wt')
csvWriter = csv.writer(csvFile)

scrapePage("205811151", 1, csvWriter)