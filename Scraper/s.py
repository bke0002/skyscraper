import urllib
from bs4 import BeautifulSoup

request = urllib.urlopen("http://homedepot.ugc.bazaarvoice.com/1999aa/205810505/reviews.djs?dir=asc&format=embeddedhtml&page=2&scrollToTop=true&sort=submissionTime")

count = 1

for line in request.readlines():
	if count == 9: 
		index = line.index("SourceID")
		string = line[index + 11:]
		string = string[:len(string) - 6]
	count += 1
	
soup = BeautifulSoup(string, "html.parser")

output = open("o.txt", "w")
output.write(string)