# contact_scraper
Python script to scrape email and telephone from website.
<br>
Usage:<br>
<br>
Command line:<br>
python sitespy.py email/tel/fax/.au http://www.africanenergyresources.com/<br>
<br>
Call:<br>
import sitespy<br>
r = sitespy.sitespy('http://www.africanenergyresources.com/', 'email')<br>
print r['email']<br>
