from bs4 import BeautifulSoup
import urllib
import xlwt
import Tkinter
import math

def createURL(modelNumber):		
   return "http://m.homedepot.com/s/" + modelNumber		

# method scrapes HomeDepot for specific Model Number		
def scraper(modelNum, excelFile):	
	#base url
	baseURL = "http://m.homedepot.com"

	# Url to scrape
	#url = "http://m.homedepot.com/p/Rheem-Performance-40-Gal-Tall-6-Year-36-000-BTU-Natural-Gas-Water-Heater-XG40T06EC36U1/205811145?keyword=XG40T06EC36U1"

	# Set up web socket with given url
	request = urllib.urlopen(createURL(modelNum))

	# Create BeautifulSoup object
	soup = BeautifulSoup(request, "html.parser")

	# Can prettify code and display with indentations
	#print (soup.prettify()[0:1000])

	# Get link to all the reviews
	allReviewsOnPage = soup.find_all('li',{'id':'reviews'})
	
	# Check to see if there are no reviews
	for rev in allReviewsOnPage:
		if (rev.find(string="No Reviews")):
			print ("No Reviews for Model Number " + modelNum)
			return "No Reviews"
	
	
	
	reviewsPage = (allReviewsOnPage[0]).find_all('a',{'class':'text-secondary flex space-between flex-grow-1'})
	
	#Check for only one review
	if (reviewsPage == []):
		print ("Only one review")
		return "Only one review"
	
	numReviewsString = reviewsPage[0].find('span', {'class':'text-primary'}).string
	numReviews = int(numReviewsString)
	
	#make new url
	newUrl = baseURL + reviewsPage[0].get('href')
	#print (newUrl)

	# set up web socket with new url
	request = urllib.urlopen(newUrl)

	# create new BeautifulSoup object for reviews page
	soup = BeautifulSoup(request, "html.parser")


	#determine number of pages of reviews with 10 reviews per page
	numPages = math.floor((numReviews / 10))
	mod = (numReviews % 10)
	if mod > 0:
		numPages = numPages + 1
		

	#get list of review info
	descriptions = []
	ratings = []
	dates = []

	#start loop
	i = 0
	j = 0
	while i < numPages:
		# find all reviews on current page
		allReviewsOnPage = soup.find_all('div',{'class':'reviews-entry p-top-normal p-bottom-normal sborder border-bottom border-default review static-height'})
		
		for review in allReviewsOnPage:
			ratings.append(review.find('div', {'class':'stars'}))
			descriptions.append(review.find('p', {'class':'review line-height-more'}))
			dates.append(review.find('div', {'class':'small text-muted right'}))
			print ("Review: " + str(j))
			j = j + 1
		if i != (numPages - 1):
			paginationSoup = soup.find_all('ul', {'class':'pagination'})
			allAElements = paginationSoup[0].find_all('a')
			link = allAElements[len(allAElements) - 1].get('href')
			
			newUrl = baseURL + link
			#get new socket for next review page
			request = urllib.urlopen(newUrl)
			#get soup for next review page
			soup = BeautifulSoup(request, "html.parser")
		i = i + 1



	reviewScores = []
	for rating in ratings:
		reviewScores.append(rating.get('rel'))
		



	workbook = xlwt.Workbook()
	sheet = workbook.add_sheet("Reviews1", cell_overwrite_ok=True)
	sheet.write(0, 0, "Review Date")
	sheet.write(0, 1, "Review Score")
	sheet.write(0, 2, "Review Text")

	output = ""
	i = 0
	for date in dates:
		strungAlongDate = date 			# Haha... date jokes.
		#strungAlongDate = strungAlongDate[15:25]

		if date == "":
			strungAlongDate = "Forever Alone. :( "

		sheet.write(i + 1, 0, strungAlongDate.string)    
		sheet.write(i + 1, 1, str(reviewScores[i]))
		sheet.write(i + 1, 2, descriptions[i].string)

		output += "\nDate: " + strungAlongDate.string + "\n"
		output += "Score: " + str(reviewScores[i]) + "\n"
		output += "Review: " + descriptions[i].string + "\n"
		i += 1

		#replace single quotes
		output.replace('\u2018', "\'")	

	print(len(descriptions))
	f = open('test.txt', 'w')
	f.write(output.encode("utf-8"))

	workbook.save(excelFile)

	f.close()
	return "Success"
	
	

#################### UI CALLS #########################################
top = Tkinter.Tk()
L1 = Tkinter.Label( top, text="Model Number" )
L1.grid(row=1, column=1, columnspan=2, rowspan=1)
modelNumberE = Tkinter.Entry(top, bd = 5)
modelNumberE.grid(row=1, column=3, columnspan=3, rowspan=1)

L2 = Tkinter.Label( top, text="Excel Spreadsheet Name")
L2.grid(row=2, column=1, columnspan=2, rowspan=1)
excelSheet = Tkinter.Entry(top, bd = 5)
excelSheet.grid(row=2, column=3, columnspan=3, rowspan=1)

B = Tkinter.Button(top, text="Submit", command = lambda: scraper(modelNumberE.get(), excelSheet.get()))
B.grid(row=3, column=2, columnspan=1, rowspan=1)

top.mainloop()