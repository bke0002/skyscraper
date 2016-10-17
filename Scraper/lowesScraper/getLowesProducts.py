from bs4 import BeautifulSoup
import urllib

# the url for Lowe's water heater search list
BASELOWESURL = "http://www.lowes.com"
SEARCHLISTURL = "http://www.lowes.com/search/products?searchTerm=water%20heaters"
SEARCHOFFSETURL = "&offset="

# returns a list of lists containing data in the form [productID, productName, productLink, modelNumber, numReviews]
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
			offset += 36
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

		numReviews = soup.find('a', { 'title' : 'View Ratings and Reviews' } ).get_text()
		numReviews = (numReviews.partition("(")[2]).partition(" ")[0].strip()
		try:
			int(numReviews)
			item.append(numReviews)
		except ValueError:
			item.append("0")
			
	# returns the list of product info with the modelNumber now appended
	return items