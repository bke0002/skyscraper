from bs4 import BeautifulSoup
import urllib.request

# Url to scrape
url = "http://www.homedepot.com/p/Rheem-Performance-40-Gal-Tall-6-Year-36-000-BTU-Natural-Gas-Water-Heater-XG40T06EC36U1/205811145?keyword=XG40T06EC36U1"

# Set up web socket with given url
request = urllib.request.urlopen(url)

# Create BeautifulSoup object
soup = BeautifulSoup(request, "html.parser")

# Can prettify code and display with indentations
#print (soup.prettify()[0:1000])

# Find all the divs with the customer_reviews id
allReviewsOnPage = soup.find_all('div',{'id':'customer_reviews'})

# Find divs with multiple classes
# 	NOTE: Home Depot has different multiple classes for each review in the list. Consider even and odd items in review list
#allReviewsOnPage = soup.find_all('div', {'class':['BVRRContentReview','BVRRDisplayContentReview','BVDIContentNative','BVRRContentReviewNative','BVDI_BAContentDIY']})       
#allReviewsOnPage = soup.find_all('div', {'class':['BVRRContentReview','BVRRDisplayContentReview','BVDIContentNative','BVRRContentReviewNative','BVDI_BAContentDIY','BVDI_BAContentVerifiedPurchaser','BVRRDisplayContentReviewOdd','BVRRDisplayContentReviewFirst','BVRROdd','BVRRFirst']})

# Iterate through all reviews on the page and find review descriptions, ratings and review dates
descriptions = []
ratings = []
dates = []

for review in allReviewsOnPage:
	descriptions = (review.find_all('span',{'itemprop':'description'}))
	ratings = (review.find_all('span',{'itemprop':'ratingValue'}))
	dates = (review.find_all('meta',{'itemprop':'datePublished'}))

# Output & Formatting
# 	Dependencies:
#		- descriptions, ratings, dates all have the same number of elements
#		- each element corresponds to eachother on the web page respectively
#			- e.g: dates[1] corresponds correctly with descriptions[1] and ratings[1]

output = ""
i = 0
for date in dates:
	strungAlongDate = str(date) 			# Haha... date jokes.
	strungAlongDate = strungAlongDate[15:25]

	if date == "":
		strungAlongDate = "Forever Alone. :( "

	output += "\nDate: " + strungAlongDate + "\n"
	output += "Score: " + ratings[i].string + "\n"
	output += "Review: " + descriptions[i].string + "\n"
	i += 1

print(output)

'''
OLD CODE ... just in case.

import urllib.request
from html.parser import HTMLParser

# Global url text
urlText = []
otherUrlText = []
html_stuff = ""

# Url to use
url2Scrape = "http://www.homedepot.com/p/Rheem-Performance-40-Gal-Tall-6-Year-36-000-BTU-Natural-Gas-Water-Heater-XG40T06EC36U1/205811145?keyword=XG40T06EC36U1"
#url2Scrape = "https://www.google.com/"

response = urllib.request.urlopen(url2Scrape)
html_stuff = response.read()

# Copy bytes into urlText list
for byte in html_stuff:
	urlText.append(byte)
	
# Decode and remove bad bytes from html_stuff
source = ""
for character in urlText:
	if character >= 32 and character <= 126: 
		source += str(chr(character))

	else:
		continue

# Create and define HTMLParser methods
class myHTMLParser(HTMLParser):
	def handle_data(self, data):
		source2 = ""
		for character in data:
			if character != '\n' and character != '\xAE' and character != '®' and character != '\u0301' and character != '\xA9':
				source2 += character
		otherUrlText.append(source2)

# Create instance of HTMLParser
parser = myHTMLParser()

# Feed source into parser
parser.feed(source)
parser.close()

for item in otherUrlText: print(item)
'''