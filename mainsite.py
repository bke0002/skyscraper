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
	string = string.replace("<br />", "\t")
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
		
		reviewDate = review.find('meta', {'itemprop':'datePublished'})
		date = reviewDate['content'][:-1]
		print("Date: " + reviewDate['content'])
		
		nickname = review.find('span',{'itemprop':'author'})
		print("Username: " + nickname.string.strip())

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
			
		yesHelpful = review.find('a', {'title': 'helpful'}).find('span', { 'class' : 'BVDINumber'} )
		print("How many people found this Helpful: " + yesHelpful.string.strip())
			
		notHelpful = review.find('a', {'title': 'unhelpful'}).find('span', { 'class' : 'BVDINumber'} )
		print("How many people found this Not Helpful: " + notHelpful.string.strip())	
		
		print("\n")
		
		csvFile.writerow( (j, productID, date, reviewScore.string.strip(), reviewText.strip(), yesHelpful.string.strip(), notHelpful.string.strip()) )

		j = j + 1


	
# Start CSV doc.
csvFile = open("scraperResults.csv", 'wb')
csvWriter = csv.writer(csvFile)

scrapePage("205811151", 1, csvWriter)