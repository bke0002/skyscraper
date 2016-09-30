import urllib
import scraperFunctions as scraperFunks
from bs4 import BeautifulSoup

# Make TCP Request
request = urllib.urlopen("http://homedepot.ugc.bazaarvoice.com/1999aa/205811145/reviews.djs?dir=asc&format=embeddedhtml&page=2&scrollToTop=true&sort=submissionTime")

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

count = 1
for review in allReviews:

	nicknameContainer = review.findAll('div',{'class':'BVRRUserNicknameContainer'})

	#try to get the author's name a few <span>'s down.
	for nicknameContObj in nicknameContainer:
		nicknames = nicknameContObj.findAll('span',{'itemprop':'author'})

		for author in nicknames:
			username = (author.string).strip()
			print( str(count) + ": " + username)

	# Contains: location, age, & verified purchase
	contextDataContainer = review.findAll('div',{'class':'BVRRContextDataContainer'}) 

	#Retreive the title of the review
	titleHolder = review.find('span', {'itemprop':'name'})
	title = titleHolder.string.strip()
	print (title)
			
	textBodyContainer = review.find('span', {'class', 'BVRRReviewText'})
	text = textBodyContainer.string.strip()
	print (text)
	# Why though?
	# Find all review information within the review container.
	reviewContainer = review.findAll('div',{'class':'BVRRReviewDisplayStyle5BodyWrapper'})

	print ("\n")
	count += 1


#print(prettyHTML)

output = open("o.txt", "w")
output.write(prettyHTML)