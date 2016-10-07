import urllib
import scraperFunctions as scraperFunks
from bs4 import BeautifulSoup
from subprocess import call
import csv
import math
import time
from datetime import datetime


#URL for Home Depot's main website
ROOTURL1 = "http://homedepot.ugc.bazaarvoice.com/1999aa/"
ROOTURL2 = "/reviews.djs?&format=embeddedhtml&page="
ROOTURL3 = "&scrollToTop=true&sort=submissionTime"

# Total number of pages always set to one, is updated for every Product Id
totalPages = 1

# Review Counter (generates temporary review key will update to Review Key found in HomeDepot's HTML)
j = 1

# Main Scraper Function scrapes a single page of reviews
def scrapePage(productID, pageNumber, csvFile):
	global j
	# Make TCP Request
	request = urllib.urlopen(ROOTURL1 + productID + ROOTURL2 + str(pageNumber) + ROOTURL3)

	# removes any output that cannot be processed by BeautifulSoup
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
	
	# parse through each review on page
	for review in allReviews:
	
		#check the date of the review and compare it to 
		reviewDate = review.find('meta', {'itemprop':'datePublished'})
		#Format date output
		dateString = reviewDate['content'][:-1]
		print ("Date: " + dateString)		
		if (dateObj != -1):
			reviewDateObj = datetime.strptime(dateString, "%Y-%m-%d")
			if (reviewDateObj < dateObj):
				return False	#the review was outside the date range
		
		#Output for debugging purposes
		print("Review Number: " + str(j))
		
		#Extra Field that is not in current output (moved to Cycle 2)
		nicknames = review.find('span',{'itemprop':'author'})
		print("Username: " + nicknames.string.strip())
		

		# Gets review title 
		reviewTitle = review.find('span',{'itemprop':'name'})
		print("Review Title: " + reviewTitle.string.strip())

		# Gets review score
		reviewScore = review.find('span', {'itemprop' : 'ratingValue'})
		print("Review Score: " + reviewScore.string.strip())

		# Gets review text
		reviewTextSpans = review.find('div', { 'itemprop' : 'description' }).findAll('span', { 'class' : 'BVRRReviewText' } )		
		print("Review Text: ")		
		# Reviews can be separated into multiple <spans> if the review used newline, put them into one string for output
		reviewText = ""
		for paragraph in reviewTextSpans:					
			reviewText = reviewText + paragraph.string.strip() + "\t"		
		# Remove any special characters that cannot be saved into csv file (non ascii (128))
		reviewText = reviewText.strip().encode("ascii", "ignore")
		print(reviewText)
		
		# Gets the number of people who marked the review as helpful (if none recorded outputs 0)
		yesHelpful = review.find('a', {'title': 'helpful'})
		if (yesHelpful is not None):
			yesHelpful = yesHelpful.find('span', { 'class' : 'BVDINumber'} ).string.strip()
			print("How many people found this Helpful: " + yesHelpful)
		else:
			yesHelpful = "0"
		
		# Gets the number of people who marked the review as not helpful (if none recorded outputs 0)
		notHelpful = review.find('a', {'title': 'unhelpful'})
		if (notHelpful is not None):
			notHelpful = notHelpful.find('span', { 'class' : 'BVDINumber'} ).string.strip()
			print("How many people found this Not Helpful: " + notHelpful)	
		else:
			notHelpful = "0"
		print("\n")

		#Write all review fields to csv file in the correct order (must match connection profile mapping!)
		csvFile.writerow( (j, productID, dateString, reviewScore.string.strip(), reviewText, yesHelpful, notHelpful) )
		
		j = j + 1 #increments the review key counter

	return True #the review was inside the date range
	
# Start CSV doc.
csvFile = open("scraperResults.csv", 'wb')
csvWriter = csv.writer(csvFile)

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

#read list of product reviews from file	
start = time.time()
inFile = open("productIDsAll.txt", 'r')
for line in inFile:
	pagenum = 1
	print ("------------------Reviews for productID: " + line + "----------------------")
	while (pagenum <= totalPages):
		if (scrapePage(line, pagenum, csvWriter)):
			pagenum += 1
		else:
			break

#saves the total time the scraper took to run			
end = time.time()
print("Elapsed time: " + str(end - start))

#print the current date to file 
newDateFile = open("dateHolder.txt", 'w')
newDateFile.write(str(datetime.now().date()))
	#newDateFile.write("\n" + str(j))
newDateFile.close()

#close files
csvFile.close()
inFile.close()

#call script to add file to Rheem's FTP server
call("winscp.com /script=ftpUploadScript.txt")