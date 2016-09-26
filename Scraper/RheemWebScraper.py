from bs4 import BeautifulSoup
import urllib
import xlwt
import Tkinter
import math
import scraperFunctions as scraperFunks
from datetime import datetime


# method scrapes HomeDepot for specific Model Number
def scraper(modelNum, sheet, j):
	baseURL = "http://m.homedepot.com"

	allHTML = scraperFunks.getHTML(scraperFunks.createURL(modelNum, "http://m.homedepot.com/s/"))

	allReviewsOnPage = scraperFunks.findAllReviews(allHTML, 'li', 'id', 'reviews')

	# get the last date scraper was ran from the text file
	try:
		file = open("LastRanDate.txt", "r")
		stringDate = file.read()
		lastRanDate = (datetime.strptime(stringDate, "%Y-%m-%d")).date()
	except IOError:
		print "No file for date previously run"
		lastRanDate = -1

	# Check to see if there are no reviews
	if (len(allReviewsOnPage) == 0):
		print "Could not find product with model number " + modelNum
		return
	for rev in allReviewsOnPage:
		if (rev.find(string="No Reviews")):
			print ("No Reviews for Model Number " + modelNum)
			return "No Reviews"

	reviewsPage = scraperFunks.findNumberOfReviewsText(allReviewsOnPage, 'a', 'class',
													   'text-secondary flex space-between flex-grow-1')

	# Check for only one review
	if (reviewsPage == []):
		print ("Only one review")
		return "Only one review"

	numReviews = scraperFunks.getNumReviews(reviewsPage, 'span', 'class', 'text-primary')

	# determine number of pages of reviews with 10 reviews per page
	numPages = int(math.floor((numReviews / 10)))
	mod = (numReviews % 10)
	if mod > 0:
		numPages = numPages + 1

	link = reviewsPage.get('href')
	link = link.replace("sort=Most-helpful", "sort=Oldest")

	if (lastRanDate == -1):
		i = 0  # Current page
		count = 0
		while i < numPages:
			# get page of reviews
			pageOfReviewsHtml = scraperFunks.getHTML(scraperFunks.createURL(link, baseURL))

			# find all reviews on current page
			allReviewsOnPage = scraperFunks.findAllReviews(pageOfReviewsHtml, 'div', 'class',
														   'reviews-entry p-top-normal p-bottom-normal sborder border-bottom border-default review static-height')

			# Write reviews from page into excel sheet
			for review in allReviewsOnPage:
				count += 1
				sheet.write(j, 0, modelNum)

				starRating = str((review.find('div', {'class': 'stars'})).get('rel'))
				sheet.write(j, 2, starRating)

				reviewText = (review.find('p', {'class': 'review line-height-more'})).string
				sheet.write(j, 3, reviewText)

				reviewDate = (review.find('div', {'class': 'small text-muted right'})).string
				sheet.write(j, 1, reviewDate)

				helpful = (review.findAll('span', {'class': 'small m-left-small'}))

				# Helpful can sometimes not exist, check for that.
				if helpful is None:
					j = j + 1
					continue
				else:
					# There can be multiple spans with same class. First is something like "Pro" or "DIY" or "Reccommended"
					# Second is "x in y found this helpful". We want that one.
					k = 0
					wasHelpful = False
					for item in helpful:
						if "helpful" in item.string:
							helpful = item
							helpful = helpful.string
							wasHelpful = True

							break

						if wasHelpful:
							sheet.write(j, 4, helpful)
							# print ("Review: " + str(j) + "\nHelpful Msg: " + helpful)
						else:
							sheet.write(j, 4, "Not Helpful")
							# print ("Review: " + str(j) + " was not helpful.")

				response = ""

				j = j + 1

			if i != (numPages - 1):
				paginationSoup = pageOfReviewsHtml.find_all('ul', {'class': 'pagination'})
				allAElements = paginationSoup[0].find_all('a')
				link = allAElements[len(allAElements) - 1].get('href')

			i = i + 1
	else:
		i = numPages  # last page of reviews
		count = 0

		while i > 0:
			# change link to last page of reviews
			pageString = "/" + str(i) + "?"
			link = link.replace("/1?", pageString)

			# get page of reviews
			pageOfReviewsHtml = scraperFunks.getHTML(scraperFunks.createURL(link, baseURL))

			# find all reviews on current page
			allReviewsOnPage = scraperFunks.findAllReviews(pageOfReviewsHtml, 'div', 'class',
														   'reviews-entry p-top-normal p-bottom-normal sborder border-bottom border-default review static-height')

			numOfReviews = len(allReviewsOnPage) - 1
			noMoreNewReviews = False
			while numOfReviews >= 0:

				reviewDate = (allReviewsOnPage[numOfReviews].find('div', {'class': 'small text-muted right'})).string
				reviewDateTime = (datetime.strptime(reviewDate, "%B %d, %Y")).date()
				# check if it is a new review
				if reviewDateTime <= lastRanDate:
					noMoreNewReviews = True
					break

				count += 1
				sheet.write(j, 0, modelNum)

				starRating = str((allReviewsOnPage[numOfReviews].find('div', {'class': 'stars'})).get('rel'))
				sheet.write(j, 2, starRating)

				reviewText = (allReviewsOnPage[numOfReviews].find('p', {'class': 'review line-height-more'})).string
				sheet.write(j, 3, reviewText)

				sheet.write(j, 1, reviewDate)

				helpful = (allReviewsOnPage[numOfReviews].findAll('span', {'class': 'small m-left-small'}))

				# Helpful can sometimes not exist, check for that.
				if helpful is None:
					j = j + 1
					numOfReviews = numOfReviews - 1
					continue
				else:
					# There can be multiple spans with same class. First is something like "Pro" or "DIY" or "Reccommended"
					# Second is "x in y found this helpful". We want that one.
					k = 0
					wasHelpful = False
					for item in helpful:
						if "helpful" in item.string:
							helpful = item
							helpful = helpful.string
							wasHelpful = True

							break

						if wasHelpful:
							sheet.write(j, 4, helpful)
							#print ("Review: " + str(j) + "\nHelpful Msg: " + helpful)
						else:
							sheet.write(j, 4, "Not Helpful")
							#print ("Review: " + str(j) + " was not helpful.")

					response = ""

					j = j + 1
					numOfReviews = numOfReviews - 1


			if noMoreNewReviews:
				break

			if i > 2:
				paginationSoup = pageOfReviewsHtml.find_all('ul', {'class': 'pagination'})
				allAElements = paginationSoup[0].find_all('a')
				link = allAElements[0].get('href')

			i = i - 1

	date = (datetime.today()).date()
	file = open("LastRanDate.txt", "w")
	file.write(str(date))
	file.close()

	print("Number of Reviews " + str(count) + " for productID " + str(modelNum))

	return j


file = open('productIDs.txt')

# Start Excel doc.
workbook = xlwt.Workbook()
sheet = workbook.add_sheet("Reviews1", cell_overwrite_ok=True)
sheet.write(0, 0, "Product ID")
sheet.write(0, 1, "Review Date")
sheet.write(0, 2, "Review Score")
sheet.write(0, 3, "Review Text")
sheet.write(0, 4, "Helpful?")

sheet.write(1, 0, "Product Identifier for Home Depot's Website")
sheet.write(1, 1, "Date the Review was made")
sheet.write(1, 2, "Rating level of the product 1 - 5")
sheet.write(1, 3, "Comments the user made about the product")
sheet.write(1, 4, "How many people marked this review as helpful")

currentLine = 2

for line in file:
	currentLine = scraper(line, sheet, currentLine)

workbook.save("scraperResult.txt")
