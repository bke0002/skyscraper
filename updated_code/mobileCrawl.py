from bs4 import BeautifulSoup
import urllib.request

#put in different file eventually
#class Queue:
#    def __init__(self):
#        self.items = []
#
#    def enqueue(self, item):
#        self.items.insert(0, item)
#    
#    def dequeue(self):
#        return (self.items.pop())
#        
#    def size(self):
#        return (len(self.items))
#        
#    def isEmpty(self):
#        return (self.items == [])

		
		
		
#base url
baseURL = "http://m.homedepot.com"

# Url to scrape
url = "http://m.homedepot.com/p/Rheem-Performance-40-Gal-Tall-6-Year-36-000-BTU-Natural-Gas-Water-Heater-XG40T06EC36U1/205811145?keyword=XG40T06EC36U1"

# Set up web socket with given url
request = urllib.request.urlopen(url)

# Create BeautifulSoup object
soup = BeautifulSoup(request, "html.parser")

# Can prettify code and display with indentations
#print (soup.prettify()[0:1000])

# Get link to all the reviews
allReviewsOnPage = soup.find_all('li',{'id':'reviews'})
reviewsPage = (allReviewsOnPage[0]).find_all('a',{'class':'text-secondary flex space-between flex-grow-1'})
numReviews = int(reviewsPage[0].find('span', {'class':'text-primary'}).string)
	
#make new url
newUrl = baseURL + reviewsPage[0].get('href')
#print (newUrl)

# set up web socket with new url
request = urllib.request.urlopen(newUrl)

# create new BeautifulSoup object for reviews page
soup = BeautifulSoup(request, "html.parser")



#determine number of pages of reviews with 10 reviews per page
numPages = round((numReviews / 10), 0)
mod = (numReviews % 10)
if mod == 10:
	numPages = numPages + 1
	

#get list of review info
descriptions = []
ratings = []
dates = []

#start loop
i = 0
while i <= numPages:
	# find all reviews on current page
	allReviewsOnPage = soup.find_all('div',{'class':'reviews-entry p-top-normal p-bottom-normal sborder border-bottom border-default review static-height'})
	
	for review in allReviewsOnPage:
		ratings.append(review.find('div', {'class':'stars'}))
		descriptions.append(review.find('p', {'class':'review line-height-more'}))
		dates.append(review.find('div', {'class':'small text-muted right'}))

	if i != numPages:
		paginationSoup = soup.find_all('ul', {'class':'pagination'})
		allAElements = paginationSoup[0].find_all('a')
		link = allAElements[len(allAElements) - 1].get('href')
		
		newUrl = baseURL + link
		#get new socket for next review page
		request = urllib.request.urlopen(newUrl)
		#get soup for next review page
		soup = BeautifulSoup(request, "html.parser")
	i = i + 1



reviewScores = []
for rating in ratings:
	reviewScores.append(rating.get('rel'))
	

# Find divs with multiple classes
# 	NOTE: Home Depot has different multiple classes for each review in the list. Consider even and odd items in review list
#allReviewsOnPage = soup.find_all('div', {'class':['BVRRContentReview','BVRRDisplayContentReview','BVDIContentNative','BVRRContentReviewNative','BVDI_BAContentDIY']})       
#allReviewsOnPage = soup.find_all('div', {'class':['BVRRContentReview','BVRRDisplayContentReview','BVDIContentNative','BVRRContentReviewNative','BVDI_BAContentDIY','BVDI_BAContentVerifiedPurchaser','BVRRDisplayContentReviewOdd','BVRRDisplayContentReviewFirst','BVRROdd','BVRRFirst']})

# Iterate through all reviews on the page and find review descriptions, ratings and review dates
#descriptions = []
#ratings = []
#dates = []
#
#for review in allReviewsOnPage:
#    descriptions = (review.find_all('span',{'itemprop':'description'}))
#    ratings = (review.find_all('span',{'itemprop':'ratingValue'}))
#    dates = (review.find_all('meta',{'itemprop':'datePublished'}))
    



# Output & Formatting
# 	Dependencies:
#		- descriptions, ratings, dates all have the same number of elements
#		- each element corresponds to eachother on the web page respectively
#			- e.g: dates[1] corresponds correctly with descriptions[1] and ratings[1]

output = ""
i = 0
for date in dates:
	strungAlongDate = date 			# Haha... date jokes.
	#strungAlongDate = strungAlongDate[15:25]

	if date == "":
		strungAlongDate = "Forever Alone. :( "

	output += "\nDate: " + strungAlongDate.string + "\n"
	output += "Score: " + str(reviewScores[i]) + "\n"
	output += "Review: " + descriptions[i].string + "\n"
	i += 1

#replace single quotes
output.replace('\u2018', "\'")	

print(len(descriptions))
f = open('test.txt', 'w')
f.write(output)
f.close()


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
			#had to get rid of this line for it to compile
				source2 += character
		otherUrlText.append(source2)

# Create instance of HTMLParser
parser = myHTMLParser()

# Feed source into parser
parser.feed(source)
parser.close()

for item in otherUrlText: print(item)
'''