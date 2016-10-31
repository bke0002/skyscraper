#=================================================================
#
#                    LOWES REVIEW SCRAPER
#
#  1) get it working for all review pages 
#  2) all product id's
# 
#=================================================================


from bs4 import BeautifulSoup
import urllib
import xlwt
import Tkinter
import math
import scraperFunctions as scraperFunks
import getProductIDs as getProductIDeez

# method scrapes HomeDepot for specific Model Number		
def scraper(productID, productTitle):	

   baseURL = "http://lowes.com/"
   urlBasic = scraperFunks.createURL(baseURL, productTitle, productID)
   url = scraperFunks.addOffsetToURL(urlBasic, 0)

   allHTML = scraperFunks.getHTML(url)

   allReviewsOnPage = scraperFunks.findAllReviews(allHTML, 'div', 'itemprop', 'review')

	# Check to see if there are no reviews
   for rev in allReviewsOnPage:
      if (rev.find(string="No reviews")):
         print ("No Reviews for Model Number " + productID)
         return "No Reviews"

   numReviews = scraperFunks.findOneItem(allHTML, 'span', 'class', 'reviews-number h3')
   numReviews = numReviews.getText().strip().split("\n")
   numReviews = str(numReviews[0]).strip()

   # While we're here, may as well grab the reviews.
   count = 0
   for review in allReviewsOnPage:
      count += 1
      reviewTitle = scraperFunks.findOneItem(review, 'h4', 'class', 'reviews-list-quote grid-60 clearfix v-spacing-medium')
      reviewTitle = reviewTitle.text

      reviewRating = scraperFunks.findOneItem(review,'span','class','ada screen-reader-only')
      reviewRating = reviewRating.text

      reviewDate = scraperFunks.findOneItem(review, 'small', 'class','darkMidGrey')      
      reviewDate = reviewDate.text

      print("Review: " + str(count))
      print("Title: " + reviewTitle)
      print("Review Date: " + reviewDate)
      print("Rating: " + reviewRating + "\n")

	
   print("Total Reviews: " + numReviews)

   #Determine if we need to go to other pages
   #  if 10 reviews, reviews are indexed 0-9
   #  if 11 reviews, the 11th review will be at index 10
   if numReviews > count:
      page = 10

      #for multiple pages, at the end of this loop, count should increase by ~10 per iteration. If count == numReviews, we will get a blank page.
      #for single pages, this loop evaluates to false
      while count in range(int(numReviews)): 
         url = scraperFunks.addOffsetToURL(urlBasic, page)
         pageOfReviewsHtml = scraperFunks.getHTML(url)
         allReviewsOnPage = scraperFunks.findAllReviews(pageOfReviewsHtml, 'div', 'itemprop', 'review')
         page += 10

         for review in allReviewsOnPage:
            count += 1
            reviewTitle = scraperFunks.findOneItem(review, 'h4', 'class', 'reviews-list-quote grid-60 clearfix v-spacing-medium')
            reviewTitle = reviewTitle.text

            reviewRating = scraperFunks.findOneItem(review,'span','class','ada screen-reader-only')
            reviewRating = reviewRating.text

            reviewDate = scraperFunks.findOneItem(review, 'small', 'class','darkMidGrey')      
            reviewDate = reviewDate.text

            print("Review: " + str(count))
            print("Title: " + reviewTitle)
            print("Review Date: " + reviewDate)
            print("Rating: " + reviewRating + "\n")

   print("Number of Reviews Retrieved: " + str(count) + " for productID: " + str(productID))

   return count

'''
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
'''


#No Reviews:
#http://www.lowes.com/pd/Rinnai-All-Parts-5-Years-Labor-1-Year-Outdoor-Natural-Gas-Water-Heater/999959667/reviews

#One Review:
#http://www.lowes.com/pd/Eemax-240-Volt-36-kW-5-Year-Limited-Indoor-Tankless-Electric-Water-Heater/999956440/reviews

#19 Reviews:
#http://www.lowes.com/pd/Whirlpool-50-Gallon-10-Year-Tall-Natural-Gas-Water-Heater/999947618/reviews

#Many Reviews:
#http://www.lowes.com/pd/GE-GeoSpring-50-Gallon-240-Volt-10-Year-Limited-Residential-Regular-Electric-Water-Heater-with-Hybrid-Heat-Pump/50335967/reviews

#Review with Response (username Termite):
#http://www.lowes.com/pd/GE-GeoSpring-50-Gallon-240-Volt-10-Year-Limited-Residential-Regular-Electric-Water-Heater-with-Hybrid-Heat-Pump/50335967/reviews?offset=9

productIDs = []
productTitles = []
#productIDs, productTitles = getProductIDeez.getProductIDs()

productID = "999947618"
productTitle = "Whirlpool-50-Gallon-10-Year-Tall-Natural-Gas-Water-Heater"
productIDs.append(productID)
productTitles.append(productTitle)

productID = "999956440"
productTitle = "Eemax-240-Volt-36-kW-5-Year-Limited-Indoor-Tankless-Electric-Water-Heater"
productIDs.append(productID)
productTitles.append(productTitle)

#Handle multiple productIDs
i = 0
for thisID in productIDs:
   productID = str(thisID)
   productTitle = str(productTitles[i])
   scraper(productID, productTitle)

#workbook.save("scraperResult.txt")