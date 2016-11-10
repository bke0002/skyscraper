import urllib
import scraperFunctions as scraperFunks
from bs4 import BeautifulSoup
from subprocess import call
import xml.etree.cElementTree as ET
import math
import time
from datetime import datetime, timedelta

# URL for Home Depot's main website
BASEURL = "http://www.homedepot.com"
SEARCHLISTURL = "http://www.homedepot.com/s/Rheem"
ROOTURL1 = "http://homedepot.ugc.bazaarvoice.com/1999aa/"
ROOTURL2 = "/reviews.djs?&format=embeddedhtml&page="
ROOTURL3 = "&scrollToTop=true&sort=submissionTime"

# Total number of pages always set to one, is updated for every Product Id
totalPages = 1

# Review Counter (generates temporary review key will update to Review Key found in HomeDepot's HTML)
j = 1


# Main Scraper Function scrapes a single page of reviews
def scrapePage(productID, pageNumber, rootXML, modelNumber, prodTitle, prodPrice):
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

	if (not soup.find('div', {'class', 'BVRRHistogramTitle'})):
		return False  # There are no reviews for this product

	# find the total number of reviews
	if (pageNumber == 1):
		numReviews = soup.find('div', {'class', 'BVRRHistogramTitle'}).find('span',
																			{'class', 'BVRRNumber'}).string.strip()
		print ("Total Number of Reviews: " + numReviews)
		if (numReviews <= 8):
			pages = 1
		else:
			pages = (math.floor((int(numReviews) - 8) / 30)) + 2
			pages = int(pages)
		global totalPages
		totalPages = pages

	# Find all the reviews (should be about 30-ish).
	allReviews = scraperFunks.findAllReviews(soup, "div", "class", "BVRRContentReview")

	# parse through each review on page
	for review in allReviews:

		revID = review['id'][27:]
		print ("ReviewID: " + revID)

		print ("product ID: " + productID)
		# check the date of the review and compare it to
		reviewDate = review.find('meta', {'itemprop': 'datePublished'})
		# Format date output
		dateString = reviewDate['content'][:-1]
		print ("Date: " + dateString)
		if (dateObj != -1):
			reviewDateObj = datetime.strptime(dateString, "%Y-%m-%d")
			if (reviewDateObj < dateObj):
				return False  # the review was outside the date range

		# Output for debugging purposes
		print("Review Number: " + str(j))

		# Extra Field that is not in current output (moved to Cycle 2)
		nicknames = review.find('span', {'itemprop': 'author'})
		username = nicknames.get_text().strip().encode("ascii", "ignore")
		print("Username: " + username)

		# Gets review title
		reviewTitle = review.find('span', {'itemprop': 'name'})
		reviewTitle = reviewTitle.get_text().strip().encode("ascii", "ignore")
		print("Review Title: " + reviewTitle)

		EoI = "0"
		quality = "0"
		value = "0"
		ratingHolder = review.find('div', {'class', 'BVRRReviewDisplayStyle5RatingWrapper'})
		subRatingHolder = ratingHolder.findAll('div', {'class': 'BVRRRating'})
		for item in subRatingHolder:
			label = item.find('div', {'class', 'BVRRLabel'}).string.strip()
			num = item.find('img', {'class', 'BVImgOrSprite'})
			if (label == 'Quality'):
				quality = num['title']
			elif (label == "Value"):
				value = num['title']
			elif (label == 'Ease of installation'):
				EoI = num['title']

		print ("EoI: " + EoI)
		print ("Q: " + quality)
		print ("V: " + value)

		# Gets review score
		reviewScore = review.find('span', {'itemprop': 'ratingValue'})
		print("Review Score: " + reviewScore.string.strip())

		# Gets review text
		reviewTextSpans = review.find('div', {'itemprop': 'description'}).findAll('span', {'class': 'BVRRReviewText'})
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
			yesHelpful = yesHelpful.find('span', {'class': 'BVDINumber'}).string.strip()
			print("How many people found this Helpful: " + yesHelpful)
		else:
			yesHelpful = "0"

		# Gets the number of people who marked the review as not helpful (if none recorded outputs 0)
		notHelpful = review.find('a', {'title': 'unhelpful'})
		if (notHelpful is not None):
			notHelpful = notHelpful.find('span', {'class': 'BVDINumber'}).string.strip()
			print("How many people found this Not Helpful: " + notHelpful)
		else:
			notHelpful = "0"

		# Get the Response from Rheem if there is one
		responseClass = review.find('div', {'class': 'BVRRReviewClientResponseText'})
		responseText = ""
		if (responseClass is not None):
			response = review.find('span', {'class': 'BVRRPlainTextMarkup'})
			responseText = response.get_text().strip().encode("ascii", "ignore")
		else:
			responseText = "No Response From Rheem"

		print("Response from Rheem: " + responseText)

		# Get Recommended Product True or False
		recommended = review.find('div', {'class': 'BVRRReviewDisplayStyle5AdditionalWrapper'})
		recommended = recommended.find('div', {'class': 'BVRRRecommendedContainer'})
		isRecommended = True
		try:
			recommended = recommended.a.extract().get_text()
		except:
			isRecommended = False
		print("Is this product recommended? " + str(isRecommended))

		# Get media indicator
		hasMedia = review.find('div', {'class': 'BVRRReviewDisplayStyle5Media'})
		isMedia = False
		if (hasMedia is not None):
			isMedia = True
		print("Does this product have photo/video? " + str(isMedia))

		link = review.find('div', {'class': 'BVRRUserNicknameContainer'})
		reviewLink = ""
		try:
			link = link.a.extract()
			reviewLink = link['href']
		except:
			reviewLink = "http://www.homedepot.com/s/" + str(productID)

		print("Link to Review " + reviewLink)

		print("\n")

		# Write all review fields to csv file in the correct order (must match connection profile mapping!)
		# csvFile.writerow( (j, revID, productID, username, reviewTitle, dateString, reviewScore.string.strip(), EoI, quality, value, reviewText, yesHelpful, notHelpful, responseText, str(isRecommended), str(isMedia), reviewLink) )

		# write xml for each review
		reviewTag = ET.SubElement(rootXML, "review")
		ET.SubElement(reviewTag, "key").text = revID
		ET.SubElement(reviewTag, "id").text = productID
		ET.SubElement(reviewTag, "rating").text = reviewScore.string.strip()
		ET.SubElement(reviewTag, "eoi").text = EoI
		ET.SubElement(reviewTag, "quality").text = quality
		ET.SubElement(reviewTag, "value").text = value
		ET.SubElement(reviewTag, "date").text = dateString
		ET.SubElement(reviewTag, "text").text = reviewText
		ET.SubElement(reviewTag, "helpful").text = yesHelpful
		ET.SubElement(reviewTag, "notHelpful").text = notHelpful
		ET.SubElement(reviewTag, "modelNumber").text = modelNumber
		ET.SubElement(reviewTag, "productName").text = prodTitle
		ET.SubElement(reviewTag, "price").text = prodPrice
		ET.SubElement(reviewTag, "username").text = username
		ET.SubElement(reviewTag, "title").text = reviewTitle
		ET.SubElement(reviewTag, "recommended").text = str(isRecommended)
		ET.SubElement(reviewTag, "response").text = responseText
		ET.SubElement(reviewTag, "link").text = reviewLink
		ET.SubElement(reviewTag, "media").text = str(isMedia)

		j = j + 1  # increments the review key counter

	return True  # the review was inside the date range


# returns a list of productInfo lists; each productInfo list is in the format [productID, productName, modelNumber, price]
def getHDProductIDs():
	request = urllib.urlopen(SEARCHLISTURL)

	productInfo = []
	count = 0
	while True:
		soup = BeautifulSoup(request, "html.parser")
		products = soup.find_all('div', {'class', 'pod-inner'})

		# iterates through each product on this page
		for product in products:
			info = product.find('div', {'class', 'pod-plp__description'})
			aElementInfo = info.find('a')

			# get productID for this product
			productLink = aElementInfo.get('href')
			index = productLink.rfind("/")
			productID = str(productLink[index + 1:])

			# get productName and make it readable for this product
			productName = aElementInfo.get_text().strip()
			productName = str(productName.replace("\n", "").replace("    ", ""))


			# get the modelNumber for this product
			modelNumInfo = product.find('div', {'class', 'pod-plp__model'})
			if modelNumInfo != None:
				modelNumInfo = modelNumInfo.get_text().strip()
				index = modelNumInfo.rfind("#")
				modelNum = str((modelNumInfo[index + 2:]).replace(u'\xa0', ""))
			else:
				newUrl = BASEURL + productLink
				request = urllib.urlopen(newUrl)
				newSoup = BeautifulSoup(request, "html.parser")

				modelNum = newSoup.find('h2', {'class', 'product_details modelNo'}).get_text().strip()
				index = modelNum.rfind("#")
				modelNum = str(modelNum[index + 2:])

			# get the price for this product
			priceInfo = product.find('div', {'class', 'price'})
			if priceInfo != None:
				priceInfo = str(priceInfo.get_text().strip())
				#print priceInfo
				price = priceInfo[:len(priceInfo) - 2] + "." + priceInfo[len(priceInfo) - 2:]
			else:
				price = str(product.find('div', {'class', 'pod-plp__discontinued'}).get_text().strip())
				price = price.replace("\n\n", " ")


			# puts info on product into a productInfo list
			thisProdInfo = [productID, productName, modelNum, price]

			productInfo.append(thisProdInfo)

		# goes to next page of products
		nextPage = soup.find_all('a', {'class', 'hd-pagination__link'})
		title = str(nextPage[len(nextPage) - 1].get('title'))
		if(title != "Next"):
			break
		else:
			nextPage = nextPage[len(nextPage) - 1].get('href')
			url = BASEURL + nextPage
			request = urllib.urlopen(url)

	return productInfo


# Start xml file
rootXML = ET.Element("xmlToImport")

# process the saved date from file (if exists)
try:
	lastDate = open("dateHolder.txt", 'r')
	date = lastDate.readline()
	# j = int(lastDate.readline().strip())
	if (date != ""):
		dateObj = datetime.strptime(date, "%Y-%m-%d")

	else:
		dateObj = -1

	lastDate.close()
except IOError:
	dateObj = -1

#badIDs = open("badProductsIDs.txt", 'a')

# read list of product reviews from file
start = time.time()
list = getHDProductIDs()
for item in list:
	pagenum = 1
	productID = item[0]
	print ("----------------Reviews for productID: " + productID + "-------------------")

	modelNum = item[2]
	productTitle = item[1]
	price = item[3]
	print("\n")
	while (pagenum <= totalPages):
		if (scrapePage(productID, pagenum, rootXML, modelNum, productTitle, price)):
			pagenum += 1
		else:
			break

# saves the total time the scraper took to run
end = time.time()
print("Elapsed time: " + str(end - start))
print("Total Number Reviews " + str(j))

# print the current date to file
newDateFile = open("dateHolder.txt", 'w')
newDateFile.write(str(datetime.now().date() - timedelta(days=14)))

newDateFile.close()

# close files
# csvFile.close()
tree = ET.ElementTree(rootXML)
tree.write("scraperResultsHD.xml")

# call script to add file to Rheem's FTP server
#call("winscp.com /script=ftpUploadScript.txt")