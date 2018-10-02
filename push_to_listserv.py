#!/usr/bin/python2.7
import os
import re
from mechanize import Browser
import ssl

br = Browser()
br.set_handle_robots( False )
br.addheaders = [('User-agent', 'Firefox')]

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
br.open("https://listserv.ucsb.edu/lsv-cgi-bin/wa?LOGON")
br.select_form(nr=0)
br.form[ 'Y' ] = 'mattvolp@gmail.com'
br.form[ 'p' ] = 'papale21'
br.submit()

RES = br.open("https://listserv.ucsb.edu/lsv-cgi-bin/wa?BULKOP1=EXCURSIONCLUB-L&P=1&O=&N=&M=&X=0D7CC922BFB76CCADF&Y=mattvolp%40gmail.com")
#print RES.read()
br.select_form(nr=1)
#print(br.form)
br.form[ 'a' ] = [ '2' ]
filename = 'listserv_emails.txt'
br.form.add_file(open(filename), 'text/plain', filename)
output = br.submit()
#print output.read()
for line in output.read().split("\n"):
    if "DELETE" in line:
        delete=line.strip()
    if "ADD" in line:
        add=line.strip()
add=add[18:23]
delete=delete[8:13]
outString = "Last Tuesday: " + delete + " members\nCurrent: " + add + " members"
with open("/home/blake/excursion/travis/listservMessage.txt", "w") as text_file:
    text_file.write(outString)
#os.system("/home/blake/excursion/travis/sendEmail.py tfrecker@gmail.com /home/blake/excursion/travis/listservMessage.txt")
os.system("/home/blake/excursion/travis/sendEmail.py info@excursionclubucsb.org /home/blake/excursion/travis/listservMessage.txt")
