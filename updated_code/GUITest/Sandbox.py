import Tkinter
from Tkinter import *
#import Image
from ScrolledText import *
import tkFileDialog
import tkMessageBox
from subprocess import call
import os
 
root = Tkinter.Tk(className=" Just another Text Editor")

#Left side text editor
TextLeft = ScrolledText(root, width=75, height=30)

#Right side text editor
TextRight = ScrolledText(root, width=75, height=30)

filePath = ""
filename = "Default.py"

# Menu Bar Functions
def open_command():
        #Tell Python that we want to change the above filename & filePath variables globally
        global filename
        global filePath

        #Get a pathway to the file
        filePath = tkFileDialog.askopenfilename(parent=root, title='Select a file')
        filename = filePath.split('/')

        #Get last element
        filename = filename[-1]
        
        print("FilePath: "+str(filePath))

        fp = open(filePath, 'r')

        if fp != None:
            contents = fp.read()
            TextLeft.delete('1.0', END)
            TextLeft.insert('1.0',contents)
            fp.close()

def save_as_command():
    global filePath
    global filename

    #Get a pathway to the file
    filePath = tkFileDialog.asksaveasfilename(parent=root, title='Save file as')
    filename = filePath.split('/')

    #Get last element
    filename = filename[-1]
    print("Asked to save as file with name: "+str(filename))

    fp = open(filePath, 'w')

    #Get write the text from the textbox to the file
    #   slice off the last character from get, as an extra return is added
    data = TextLeft.get('1.0', END+'-1c')
    
    if fp != None:
        contents = fp.write(data)
        fp.close()
    
    #Now open the file again and write to the screen.
    fp = open(filePath, 'r')

    if fp != None:
        contents = fp.read()
        TextLeft.delete('1.0', END)
        TextLeft.insert('1.0',contents)
        fp.close()
 
def save_command():
    global filePath
    global filename

    #Open the file        
    fp = open(filePath, 'w')

    #Get write the text from the textbox to the file
    #   slice off the last character from get, as an extra return is added
    data = TextLeft.get('1.0', END+'-1c')

    if fp != None:
        fp.write(data)
        fp.close()

def exit_command():
    if tkMessageBox.askokcancel("Quit", "Do you really want to quit?"):
        if os.path.exists(os.path.abspath(filename)) and filename == "default.py":
            os.remove(filename)
        root.destroy()
 
def about_command():
    label = tkMessageBox.showinfo("About", "Just Another Textpad \n Copyright \n No rights left to reserve")

def run_command():
    global filename
    global filePath

    already_checked_for_file = False

    # Check if default.py exists. If so, rewrite it to whatever is in TextLeft screen.
    if os.path.exists(os.path.abspath(filename)) and filename == "default.py":
        filePath = os.path.abspath(filename)
        #Open the file        
        fp = open(filePath, 'w')

        #Get write the text from the textbox to the file
        #slice off the last character from get, as an extra return is added
        data = TextLeft.get('1.0', END+'-1c')

        if fp != None:
            fp.write(data)
            fp.close()

            # Run the given file
            print("Running: " + filename)
            command_string = "python " + filename
            call(command_string)

            # Open the textbox on the right, write results to that textbox
            fp = open("result.txt")

            if fp != None:
                contents = fp.read()
                TextRight.delete('1.0', END)
                TextRight.insert('1.0',contents)
                fp.close()

        else:
            print("No file path.")

        already_checked_for_file = True

    #check if our file exists before trying to call it.
    if not os.path.exists(os.path.abspath(filename)) and not already_checked_for_file:
        # if it doesn't exist, create the default file.
        filename = "default.py"
        filePath = os.path.abspath(filename)
        #Open the file        
        fp = open(filePath, 'w')

        #Get write the text from the textbox to the file
        #   slice off the last character from get, as an extra return is added
        data = TextLeft.get('1.0', END+'-1c')

        if fp != None:
            fp.write(data)
            fp.close()

            # Run the given file
            print("Running: " + filename)
            command_string = "python " + filename
            call(command_string)

            # Open the textbox on the right, write results to that textbox
            fp = open("result.txt")

            if fp != None:
                contents = fp.read()
                TextRight.delete('1.0', END)
                TextRight.insert('1.0',contents)
                fp.close()
        else:
            print("No file path.")

    
         
def new_command():
    #Tell Python that we want to change the above filename & filePath variables globally
    global filename
    global filePath
    global TextLeft

    #Get a pathway to the file
    filePath = tkFileDialog.asksaveasfilename(parent=root, title='Save file as')
    filename = filePath.split('/')

    #Get last element
    filename = filename[-1]
    print("Asked to save as file with name: "+str(filename))

    fp = open(filePath, 'w')
    
    if fp != None:
        contents = fp.write("This is where the contents of the file will go.")
        fp.close()
    
    #Now open the file again and write to the screen.
    fp = open(filePath, 'r')

    if fp != None:
        contents = fp.read()
        TextLeft.delete('1.0', END)
        TextLeft.insert('1.0',contents)
        fp.close()

def template_command():
    scraper_template_code =  "import urllib\t\t\t\t# Used for requesting data from web sites"
    scraper_template_code += "\nfrom bs4 import BeautifulSoup\t\t\t# Used for parsing the requested data. Must be installed on machine before using import."
    scraper_template_code += "\n\n# The URL of the root website that you want to scrape."
    scraper_template_code += "\nBASIC_URL = \"https://www.lowes.com/pd/Whirlpool-50-Gallon-10-Year-Tall-Natural-Gas-Water-Heater/999947618/reviews?sortMethod=SubmissionTime&sortDirection=desc&offset=0\""
    scraper_template_code += "\n\n# Local variables here."
    scraper_template_code += "\nelement = 'div'"
    scraper_template_code += "\nattribute = 'itemprop'"
    scraper_template_code += "\nattributeValue = 'review'"
    scraper_template_code += "\nprettyString = \"\""
    scraper_template_code += "\nitemString = \"\""
    scraper_template_code += "\n\n# Request information from the website"
    scraper_template_code += "\nrequest = urllib.urlopen(BASIC_URL)"
    scraper_template_code += "\n\n# Initialize the parser, \"html.parser\" tells BeautifulSoup to parse HTML format."
    scraper_template_code += "\nsoup = BeautifulSoup(request, \"html.parser\")"
    scraper_template_code += "\n\n#----------------------------------------------------------------------------------------------"
    scraper_template_code += "\n# Learn more about Beautiful Soup here: https://www.crummy.com/software/BeautifulSoup/bs4/doc/"
    scraper_template_code += "\n#----------------------------------------------------------------------------------------------"
    scraper_template_code += "\n\n# Write to result.txt file so that we can view it in the right-hand panel of the sandbox."
    scraper_template_code += "\nresultFile = open(\"result.txt\", \"w+\")"
    scraper_template_code += "\n\n# To find all items with a particular html tag and attribute value"
    scraper_template_code += "\nproducts = soup.find_all(element, {attribute : attributeValue})"
    scraper_template_code += "\nfor item in products:"
    scraper_template_code += "\n\tresultFile.write(\"\\n=======================================\\nREVIEW\\n=======================================\\n\"" 
    scraper_template_code += "+str(item))"
    scraper_template_code += "\n\n# To find a single element with attribute value"
    scraper_template_code += "\none_item = soup.find(element, { attribute : attributeValue })"
    scraper_template_code += "\nresultFile.write(\"\\n=======================================\\nONE ITEM\\n=======================================\\n\"" 
    scraper_template_code += "+str(one_item))"
    scraper_template_code += "\n\n# View the whole page HTML in HTML format, replace characters we can't encode (Example: copyright symbol)."
    scraper_template_code += "\nprettyString = soup.prettify().encode('utf-8','replace')"
    scraper_template_code += "\n\n#resultFile.write(prettyString)"
    scraper_template_code += "\nresultFile.write(itemString)"
    scraper_template_code += "\nresultFile.close()"

    TextLeft.delete('1.0', END)
    TextLeft.insert('1.0',scraper_template_code)

def clear_right_command():
    TextRight.delete('1.0', END)

def clear_left_command():
    TextLeft.delete('1.0', END)

def on_closing():
    global filename
    if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
        if os.path.exists(os.path.abspath(filename)) and filename == "default.py":
            os.remove(filename)
        root.destroy()
    
# Toolbar
toolbar = Frame(root, bd=1, relief=RAISED)
runButton = Button(toolbar, text="RUN" ,relief=FLAT,command=run_command)
templateButton = Button(toolbar, text="TEMPLATE", relief=FLAT, command=template_command)
clearLeftButton = Button(toolbar, text="CLEAR (left)", relief=FLAT, command=clear_left_command)
clearRightButton = Button(toolbar, text="CLEAR (right)", relief=FLAT, command=clear_right_command) 

runButton.pack(side=LEFT, padx=2, pady=2)
templateButton.pack(side=LEFT, padx=2, pady=2)
clearLeftButton.pack(side=LEFT, padx=2, pady=2)
clearRightButton.pack(side=RIGHT, padx=2, pady=2)
toolbar.pack(side=TOP, fill=X)

# Menu Bar
menu = Menu(root)
root.config(menu=menu)
menuBar = Menu(menu)
menu.add_cascade(label="File", menu=menuBar)
menuBar.add_command(label="New", command=new_command)
menuBar.add_command(label="Open...", command=open_command)
menuBar.add_command(label="Save As", command=save_as_command)
menuBar.add_separator()
menuBar.add_command(label="Exit", command=exit_command)
helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About...", command=about_command)
 
TextLeft.pack(side=LEFT)
#photo=PhotoImage(file='./testimage.jpg')
TextRight.insert(END,'Write output to result.txt to view it in this window.\n')
#TextRight.image_create(END,image=photo)
TextRight.pack(side=RIGHT)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()