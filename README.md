# contact_scraper
Python script to scrape email and telephone from website

Usage:

Command line:
python sitespy.py email/tel/fax/.au http://www.africanenergyresources.com/

Call:
import sitespy
r = sitespy.sitespy('http://www.africanenergyresources.com/', 'email')
print r['email']
