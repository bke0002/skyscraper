from bs4 import BeautifulSoup
import urllib
import xlwt
import Tkinter
import math
import scraperFunctions as scraperFunks

# method scrapes HomeDepot for specific Model Number		
def scraper(modelNum, excelFile):	

   baseURL = "http://m.homedepot.com"

   allHTML = scraperFunks.getHTML(scraperFunks.createURL(modelNum, "http://m.homedepot.com/s/"))

   allReviewsOnPage = scraperFunks.findAllReviews(allHTML, 'li', 'id', 'reviews')

	# Check to see if there are no reviews
   for rev in allReviewsOnPage:
      if (rev.find(string="No Reviews")):
         print ("No Reviews for Model Number " + modelNum)
         return "No Reviews"

   reviewsPage = scraperFunks.findNumberOfReviewsText(allReviewsOnPage, 'a', 'class', 'text-secondary flex space-between flex-grow-1') 
   
   #Check for only one review
   if (reviewsPage == []):
      print ("Only one review")
      return "Only one review"

   numReviews = scraperFunks.getNumReviews(reviewsPage, 'span', 'class', 'text-primary')

	#determine number of pages of reviews with 10 reviews per page
   numPages = math.floor((numReviews / 10))
   mod = (numReviews % 10)
   if mod > 0:
      numPages = numPages + 1

   # Start Excel doc.
   workbook = xlwt.Workbook()
   sheet = workbook.add_sheet("Reviews1", cell_overwrite_ok=True)
   sheet.write(0, 0, "Review Date")
   sheet.write(0, 1, "Review Score")
   sheet.write(0, 2, "Review Text")
   sheet.write(0, 3, "Helpful?")
   sheet.write(0, 4, "Response?")
   sheet.write(0, 5, "Response ID")

   
   i = 0    # Current page
   j = 1    # Row number in excel sheet
   link = reviewsPage.get('href')

   while i < numPages:
      # get page of reviews
      pageOfReviewsHtml = scraperFunks.getHTML(scraperFunks.createURL(link, baseURL))

      # find all reviews on current page
      allReviewsOnPage = scraperFunks.findAllReviews(pageOfReviewsHtml, 'div', 'class', 'reviews-entry p-top-normal p-bottom-normal sborder border-bottom border-default review static-height')

      # Write reviews from page into excel sheet
      for review in allReviewsOnPage:
         starRating = str((review.find('div', {'class':'stars'})).get('rel'))
         sheet.write(j, 1, starRating)

         reviewText = (review.find('p', {'class':'review line-height-more'})).string
         sheet.write(j, 2, reviewText)

         reviewDate = (review.find('div', {'class':'small text-muted right'})).string
         sheet.write(j, 0, reviewDate)

         helpful = (review.findAll('span',{'class':'small m-left-small'}))
         
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
               sheet.write(j,3,helpful)
               print ("Review: " + str(j) + "\nHelpful Msg: " + helpful)
            else:
               sheet.write(j,3,"Not Helpful")
               print ("Review: " + str(j) + " was not helpful.")

         response = ""
         

         j = j + 1

      
      if i != (numPages - 1):
         paginationSoup = pageOfReviewsHtml.find_all('ul', {'class':'pagination'})
         allAElements = paginationSoup[0].find_all('a')
         link = allAElements[len(allAElements) - 1].get('href')

      i = i + 1


   #reviewScores = []
   #for rating in ratings:
   #   reviewScores.append()


   

   #i = 0
   #for date in dates:
   #   strungAlongDate = date 			# Haha... date jokes.
   #   #strungAlongDate = strungAlongDate[15:25]

   #   if date == "":
   #      strungAlongDate = "Forever Alone. :( "

   #   sheet.write(i + 1, 0, strungAlongDate.string)    
   #   sheet.write(i + 1, 1, str(reviewScores[i]))
   #   sheet.write(i + 1, 2, descriptions[i].string)

   #   i += 1

   


   workbook.save(excelFile)

   print("Number of Reviews" + str(j))

   return "Success"

scraper("XG40S09HE38U0", "scraperResult.xls")

#################### UI CALLS #########################################
#top = Tkinter.Tk()
#L1 = Tkinter.Label( top, text="Model Number" )
#L1.grid(row=1, column=1, columnspan=2, rowspan=1)
#modelNumberE = Tkinter.Entry(top, bd = 5)
#modelNumberE.grid(row=1, column=3, columnspan=3, rowspan=1)

#L2 = Tkinter.Label( top, text="Excel Spreadsheet Name")
#L2.grid(row=2, column=1, columnspan=2, rowspan=1)
#excelSheet = Tkinter.Entry(top, bd = 5)
#excelSheet.grid(row=2, column=3, columnspan=3, rowspan=1)

#B = Tkinter.Button(top, text="Submit", command = lambda: scraper(modelNumberE.get(), excelSheet.get()))
#B.grid(row=3, column=2, columnspan=1, rowspan=1)

#top.mainloop()