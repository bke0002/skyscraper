import urllib
from bs4 import BeautifulSoup

BASEURL = "http://www.homedepot.com"
SEARCHLISTURL = "http://www.homedepot.com/s/Rheem"


def getProductIDs():
	request = urllib.urlopen(SEARCHLISTURL)

	allProducts = []
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



			count += 1
			print count
			thisProdInfo = [productID, productName, modelNum, price]
			print thisProdInfo

			productInfo.append(thisProdInfo)

		nextPage = soup.find_all('a', {'class', 'hd-pagination__link'})
		title = str(nextPage[len(nextPage) - 1].get('title'))
		if(title != "Next"):
			break
		else:
			nextPage = nextPage[len(nextPage) - 1].get('href')
			url = BASEURL + nextPage
			request = urllib.urlopen(url)

	print len(allProducts)
	return productInfo

print len(getProductIDs())
