import requests
from lxml import etree
import re
import sys
from urlparse import urljoin

def scrape_tel(url, keys, col_site, html, identifier='office|tel|call|phone|T:|T', echo=False):
    tel = ''
    if tel == '' and ('.au' in keys or col_site.endswith('.au')): # in Australia
        #r = re.compile(r'(tel|call|phone)[^\d]{0,12}(\+61\s)?(\(?\d{1,2}\)?.\d{4}.\d{4})', re.I) #3 .au
        r = re.compile(r'(%s)[^\d]{0,12}(\+61\s)?(\(0\)\s)?(\d{1,2}.\d{4}.\d{4})' % identifier, re.I) #3 .au
        ss = r.findall(html)
        if len(ss)>0:
            _, s1, _, s2 = ss[0]
            tel = s1 + s2
        if tel == '':
            r = re.compile(r'(%s)[^\d\(\)]{0,12}(\(?\+\d{3,4}\)?.\d{4}.\d{4})' % identifier, re.I) #3 .au
            ss = r.findall(html)
            if len(ss)>0:
                _, tel = ss[0]
        if echo :
            print 'scrape_tel:hit #1 ' + tel
    #NY 10012 | T: +1 212 925 2555 | F: +1 212 925 2556
    if tel == '':
        r = re.compile(r'(%s)[^\d\+]{0,6}(\+?\d+[- \.]\d{3}[- \.]\d{3}[- \.]?\d{4})' % identifier, re.I)
        ss = r.findall(html)
        if len(ss)>0:
            _, tel = ss[0]
            if echo :
                print 'scrape_tel:hit #2 ' + tel
    #TEL: 1-212-581-7000
    #if tel == '':
    #    r = re.compile(r'(%s)[^\d]{0,6}(\d+[- \.]\d{3}[- \.]\d{3}[- \.]\d{4})' % identifier, re.I)
    #    ss = r.findall(html)
    #    if len(ss)>0:
    #        _, tel = ss[0]
    if tel == '':
        r = re.compile(r'(%s)[^\d]{0,12}(\d{3,4}[- \.]\d{3}[- \.]\d{3,4})' % identifier, re.I) #2
        ss = r.findall(html)
        if len(ss)>0:
            _, tel = ss[0]
            if echo :
                print 'scrape_tel:hit #3 ' + tel
    #(212) 485 2400
    if tel == '':
        r =  re.compile(r'(%s)[^\d\(\)]*(\(\d{3}\) ?\d{3}[- \.]\d{4})' % identifier, re.I)
        ss = r.findall(html)
        #print 'ss:', ss
        if len(ss)>0:
            _, tel = ss[0]
            if echo :
                print 'scrape_tel:hit #4'
    if tel == '' and identifier != 'fax':
        r = re.compile(r'(\d{1,2}-\d{3}-\d{3}-\d{4})', re.I) #1
        ss = r.findall(html)
        if len(ss)>0:
            tel = ss[0]
            if echo :
                print 'scrape_tel:hit #5'
     #&nbsp;333-333-4444
    if tel == '' and identifier != 'fax':
        r = re.compile(r'&nbsp;(\d{3}[- \.]\d{3}[- \.]\d{4})', re.I)
        ss = r.findall(html)
        if len(ss)>0:
            tel = ss[0]
            if echo :
                print 'scrape_tel:hit #6'
     # 333-333-4444
    if tel == '' and identifier != 'fax':
        r = re.compile(r'[ >](\d{3}[- \.]\d{3}[- \.]\d{4})', re.I) #1
        ss = r.findall(html)
        if len(ss)>0:
            tel = ss[0]
            if echo :
                print 'scrape_tel:hit #7'
    #if tel == '':
    #    r = re.compile(r'(%s)[^\d]{0,12}([\d]{9,12})' % identifier, re.I) #1
    #    ss = r.findall(html)
    #    if len(ss)>0:
    #        _, tel = ss[0]
    #        if echo :
    #            print 'scrape_tel:hit #8'

    return tel

def email_filter(emails):
    rt = []
    for email in emails:
        ok = True
        ext_pass=['.jpg','.png','.gif','.pdf','.zip']
        for ext in ext_pass:
            if ext in email.lower():
                ok = False
        if ok:
            rt.append(email)
    return rt

#required pattern='[^@]+@[^@]+\.[a-zA-Z]{2,6}'
def scrape_email(url, keys, col_site, html, echo=False):
    email = ''
    if echo :
        print 'have @ :', '@' in html
    if '@' in html:
        r = re.compile(r'(\b[\w]+@%s)' % col_site)
        if 'email' in keys:
            #r = re.compile(r'(\b[\w.]+@[\w.]+.[\w.]\b)')
            r = re.compile(r'\b[\w.-]+@[\w.-]+\.\w+\b')
        ss = r.findall(html)
        ss = email_filter(ss)
        if len(ss)>0:
            email = ss[0]
        else:
            r = re.compile(r'(\b[\w]+@%s)' % col_site.split('.',1)[1])
            ss = r.findall(html)
            ss = email_filter(ss)
            if len(ss)>0:
                email = ss[0]
    return email

def htmlspy(html, keys=[]):
    datas = {}
    #Initial keys.
    if 'email' in keys or 'siteemail' in keys:
        email = scrape_email('', keys, '', html)
        datas['email'] = email
    if 'tel' in keys:
        tel = scrape_tel('', keys, '', html)
        datas['tel'] = tel
    if 'fax' in keys:
        fax = scrape_tel('', keys, '', html, identifier='fax')
        datas['fax'] = fax

    return datas

def sitespy(url, keys=[], echo=False):

    if '//' in url:
        col_site = url.split('//')[1].split('/')[0]
    else:
        col_site = url.split('/')[0]
        url = 'http://' + url
    if echo :
        print 'website:%s' % col_site

    datas = {}
    html = requests.get(url).text

    #Initial keys.
    if 'email' in keys or 'siteemail' in keys:
        email = ''
    if 'tel' in keys:
        tel = ''
    if 'fax' in keys:
        fax = ''

    for i in range(2):
        #scrape one page
        #Open contact web at two loop.
        if i==1:
            try:
                tree = etree.HTML(html)
                tmp = tree.xpath('//a[contains(text(),"contact") or contains(text(),"Contact") or contains(text(),"CONTACT")]/@href')
                if not tmp:
                    tmp = tree.xpath('//a[contains(*/text(),"contact") or contains(*/text(),"Contact") or contains(*/text(),"CONTACT")]/@href')
                if tmp:
                    u = urljoin(url, tmp[0])
                    html = requests.get(u).text
                if echo :
                    print 'Scan contact page...'
            except Exception:
                #try:
                #    firstLink = br.find_link(url_regex=re.compile("contact", re.I),nr=0)
                #    br.follow_link(firstLink)
                #    html = br.response().read()
                #except Exception:
                break
        #scrape email
        if ('email' in keys or 'siteemail' in keys) and email == '':
            email = scrape_email(url, keys, col_site, html, echo)
            datas['email'] = email
        #scrape tel
        if 'tel' in keys and tel == '':
            tel = scrape_tel(url, keys, col_site, html, echo=echo)
            datas['tel'] = tel
        #scrape fax
        if 'fax' in keys and fax == '':
            fax = scrape_tel(url, keys, col_site, html, identifier='fax', echo=echo)
            datas['fax'] = fax

    return datas

if __name__ == '__main__':
    #print sitespy(sys.argv[1], ['email','tel'])
    if len(sys.argv)<3:
        print 'Usage: sitespy.py email,tel url'
    else:
        print sitespy(sys.argv[2], sys.argv[1], True)
