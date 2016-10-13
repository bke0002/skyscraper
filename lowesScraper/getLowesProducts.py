from bs4 import BeautifulSoup
import urllib

# the url for Lowe's water heater search list
SEARCHLISTURL = "http://www.lowes.com/search/products?searchTerm=water%20heaters"
SEARCHOFFSETURL = "&offset="

# returns a list of productIDs to scrape for
def getProductIDs():
	# make request to first page
	request = urllib.urlopen(SEARCHLISTURL)

	# set initial values
	offset = 0
	productIDs = []
	productTitles = []
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

		# appends the productIDs of products with (water heater and (GE or Whirlpool)) in the title to the list
		for product in products:
			title = product.get("data-producttitle")
			if (title.lower().find("water heater") >= 0):
				if (title.find("GE") >= 0) or (title.find("Whirlpool") >= 0):
					productTitles.append(title)
					productIDs.append(product.get("data-productid"))

		# if there is no next page break else get the next url
		nextPage = soup.find_all('li', {'class', 'page-next disabled'})
		if len(nextPage) > 0:
			break
		else:
			offset += 36
			url = SEARCHLISTURL + SEARCHOFFSETURL + str(offset)

	return productIDs,productTitles
