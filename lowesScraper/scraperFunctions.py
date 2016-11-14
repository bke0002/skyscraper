from bs4 import BeautifulSoup
import urllib
from datetime import datetime, timedelta
from subprocess import call
import xml.etree.cElementTree as ET



####################################################################
#Home Depot Functions
####################################################################    

#Used to parse out non-html returned by the javascript call
def prepareHTML(request):
	# Find where our reviews are located in BazaarVoice JavaScript
	count = 1
	for line in request.readlines():
		if count == 9: 
			index = line.index("SourceID")
			string = line[index + 11:]
			string = string[:len(string) - 6]
		count += 1

	# Remove bad characters
	string = string.replace("<br />", "\n")
	string = string.replace("\\/","/")
	string = string.replace("\\\"","")
	string = string.replace(chr(ord(u'\xbd')),"") # found this odd character "HALFWIDTH HANGUL LETTER PHIEUPH"
	string = string.replace(chr(ord(u'\xc2')),"") # This one looks like a T.
	
	return string
	

####################################################################
# Lowe's Functions
#################################################################### 	
##### Lowes Constants #####
BASELOWESURL = "http://www.lowes.com"
SEARCHLISTURL = "http://www.lowes.com/search/products?searchTerm=water%20heaters"
SEARCHOFFSETURL = "&offset="
PRICEURL1 = "https://lowes.ecorebates.com/api/search/lowes/productRebateDetails.json?jsoncallback=angular.callbacks._0&skus="
PRICEURL2 = "&uiContext=PDP"
PRODUCTS_PER_PAGE = 36

# returns a list of lists containing data in the form [productID, productName, productLink, modelNumber, numReviews, price]
def getProductInfo():
	# make request to first page
	request = urllib.urlopen(SEARCHLISTURL)

	# set initial values
	offset = 0
	productsInfo = []
	url = ""
	# start looping through pages to get productIDs
	while True:
		# get request if this is not the first time through the loop
		if offset != 0:
			request = urllib.urlopen(url)

		# parse the html
		soup = BeautifulSoup(request, "html.parser")

		# find all products on current page
		products = soup.find_all('li', {'class', 'product-wrapper grid-25 tablet-grid-33 v-spacing-large'})

		# appends the productIDs, tile, and link of products with (water heater and (GE or Whirlpool)) in the title to the list
		for product in products:
			title = product.get("data-producttitle")
			if (title.lower().find("water heater") >= 0):
				if (title.find("GE") >= 0) or (title.find("Whirlpool") >= 0):
					productID = product.get("data-productid")
					link = BASELOWESURL + product.get("data-producturl")
					info = [str(productID), str(title), str(link)]
					productsInfo.append(info)

		# if there is no next page break else get the next url
		nextPage = soup.find_all('li', {'class', 'page-next disabled'})
		if len(nextPage) > 0:
			break
		else:
			offset += PRODUCTS_PER_PAGE
			url = SEARCHLISTURL + SEARCHOFFSETURL + str(offset)

	# makes a call to get the modelNumber for each product
	productsInfo = getModelNumber(productsInfo)

	return productsInfo

# returns the model number given a list of product information (has to include a link to the product page)
# Also grabs the number of reviews
def getModelNumber(items):
	for item in items:
		# link to the product page
		link = item[2]
		# product id for product
		productID = item[0]

		# make url request
		request = urllib.urlopen(link)

		# parse the html
		soup = BeautifulSoup(request, "html.parser")

		# finds the modelNumber and appends it to the item record for each item in items
		info = soup.find('p', {'class', 'secondary-text small-type'}).get_text().strip()
		index = info.rfind("#")
		if (index >= 0):
			modelNum = info[index + 2:]
			item.append(str(modelNum))

		# finds the number of Reviews for each product
		numReviews = soup.find('a', {'title': 'View Ratings and Reviews'}).get_text()
		numReviews = (numReviews.partition("(")[2]).partition(" ")[0].strip()
		try:
			int(numReviews)
			item.append(numReviews)
		except ValueError:
			item.append("-1")

		# finds the price for the product
		url = PRICEURL1 + str(productID) + PRICEURL2
		request = urllib.urlopen(url)
		for line in request.readlines():
			index = line.find("price\":")
			sub = line[index:]
			index = sub.find(":")
			index2 = sub.find(",")
			price = sub[index + 1:index2]
			item.append(price)


	# returns the list of product info with the modelNumber now appended
	return items


####################################################################
# All Scraper Functions
#################################################################### 

def readDate(dateFile):
	try:
		lastDate = open(dateFile, 'r')
		date = lastDate.readline()

		if (date != ""):
			dateObj = datetime.strptime(date, "%Y-%m-%d")
		else:
			dateObj = -1

		lastDate.close()
	
	except IOError:
		dateObj = -1
	
	return dateObj

def uploadToFTP(filename):
	script = "script=" + filename
	call("winscp.com /" + script)
	
def writeReviewToXML(xmlTree, reviewDict, isHomeDepot):
	reviewTag = ET.SubElement(xmlTree, "review")
	ET.SubElement(reviewTag, "key").text = reviewDict['key']
	ET.SubElement(reviewTag, "id").text = reviewDict['id']
	ET.SubElement(reviewTag, "rating").text = reviewDict['rating']
	ET.SubElement(reviewTag, "date").text = reviewDict['date']
	ET.SubElement(reviewTag, "text").text = reviewDict['text']
	ET.SubElement(reviewTag, "helpful").text = reviewDict['helpful']
	ET.SubElement(reviewTag, "notHelpful").text = reviewDict['notHelpful']
	ET.SubElement(reviewTag, "modelNumber").text = reviewDict['modelNumber']
	ET.SubElement(reviewTag, "productName").text = reviewDict['productName']
	ET.SubElement(reviewTag, "username").text = reviewDict['username']
	ET.SubElement(reviewTag, "title").text = reviewDict['title']
	ET.SubElement(reviewTag, "recommended").text = reviewDict['recommended']
	ET.SubElement(reviewTag, "link").text = reviewDict['link']
	ET.SubElement(reviewTag, "media").text = reviewDict['media']	
	ET.SubElement(reviewTag, "price").text = reviewDict['price']
	
	if(isHomeDepot) :
		ET.SubElement(reviewTag, "eoi").text = EoI
		ET.SubElement(reviewTag, "quality").text = quality
		ET.SubElement(reviewTag, "value").text = value
		ET.SubElement(reviewTag, "response").text = responseText