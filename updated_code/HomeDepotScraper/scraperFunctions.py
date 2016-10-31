from bs4 import BeautifulSoup
import urllib


# creates complete URL using a baseUrl and a variable number or identifier
def createURL(modelNumber, baseURL):    
   return baseURL + modelNumber   

def getAllModelNumbers(filename):
  return 0

# returns parseable Html object from Beautiful Soup library
def getHTML(URL):

    # Set up web socket with given url
   request = urllib.urlopen(URL)

  # Create BeautifulSoup object
   soup = BeautifulSoup(request, "html.parser")
   
   return soup 

# returns Array of HTML review objects matching the descriptions
def findAllReviews(htmlToParse, htmlTag, tagAttrib, tagName):

   # Get link to all the reviews
   return htmlToParse.find_all(htmlTag, { tagAttrib : tagName })


def findNumberOfReviewsText(allReviewsHtml, htmlTag, tagAttrib, tagName):

    return (allReviewsHtml[0]).find_all(htmlTag, { tagAttrib : tagName})[0]


def getNumReviews(numReviewsText, htmlTag, tagAttrib, tagName):
   numReviewsString = numReviewsText.find(htmlTag, { tagAttrib : tagName }).string
   return int(numReviewsString)
   
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