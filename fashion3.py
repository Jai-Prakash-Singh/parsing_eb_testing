#!/usr/bin/env python 

from bs4 import BeautifulSoup
import re,urllib2,urlparse, MySQLdb,sys,time
import proxy_module 


def seller_info(link):
    page  = proxy_module.main(link)
    soup = BeautifulSoup(page)
    page.close()
    data = soup.find_all("td", attrs={"id":"viewItemId"})
    try:
        view_link = str(data[0].a.get("href"))
        page  = proxy_module.main(view_link)
        print view_link
        soup = BeautifulSoup(page)
        data = soup.find_all("h1", attrs={"class":"vi-is1-titleH1"})
        last_item_content = str(data[0].get_text())
        data = soup.find_all("span", attrs={"class":"vi-is1-condText"})
        item_condition = str(data[0].string)
        try:
            data = soup.find_all("span", attrs={"class":"vi-is1-dt"})
            ended = str(data[0].get_text())
        except:
            ended ="Not yet ended"
        data = soup.find_all("span", attrs={"class":"vi-is1-prcp"})
        selling_price = str(data[0].get_text())
        data = soup.find_all("span", attrs={"id":"fshippingCost"})
        shipping  = str(data[0].get_text())
    except:
        view_link ="private"
    if  view_link.lower()=="private":
        last_item_content = "None as it is private "
	view_link = "No link as it is private "
	item_condition = "Private"
	ended = "Not Known  "
	selling_price = "Not Known  "
	shipping = "Not Known"
    return last_item_content, view_link,item_condition, ended, selling_price, shipping






     

def get_domain(url):
    return urlparse.urlparse(url).netloc



def men_tshirts(db,cursor,gender, main_link,sub_cat,cat_url):
    #capturing link 
    #main_link = "http://fashion.ebay.in/index.html#men_tshirts"
    #get domain name from  above link 
    domane = get_domain(main_link)
    #open page sourse code of above link 
    main_page = proxy_module.main(main_link)
    #maintaing the beautiful on above sourse
    main_soup=BeautifulSoup(main_page)
    #closing above page 
    main_page.close()
    #collecting the sub category of above link 
    data = main_soup.find_all("div",attrs= {"class":"itmTitle"})
    #collecting price of above sub category
    #price = main_soup.find_all("span",attrs={"class":"catlblTitle"})
    #fetching link and category from  list named data
    for x in data :
        #capturing category in string 
        cat = str(x.a.string)
	#capturing  link  in string and adding its domain name 
	link = "http://"+domane+"/"+str(x.a.get("href"))
	#opening sourse code of link name as link
        print link
        page = proxy_module.main(link)
	#crating beautiful soup on above page named page 
        soup = BeautifulSoup(page)
	#closing page 
        page.close()
	#fetching item title list  from sourse page 
        item = soup.find_all("div",attrs={"class":"itemTitle"})
	#fetching price lsit  from sourse page 
        price = soup.find_all("div", attrs={"class":"itemPrice"})
        #fetching item and price individualy  form item and price list 
        for x,y in zip(item,price):
	    #fetching iyem title 
            item_content=str(x.a.string)
	    #fetching price title 
            p = str(y.p.string)
	    #fetching page sourse for seller  from link of item title 
            link2 = str(x.a.get("href"))
	    print link2
	    #opening sourse code of  just above link 
            page =proxy_module.main(link2)
	    #creatug beauti 
            soup = BeautifulSoup(page)
	    #closing page
            page.close()
	    #feticng seller data 
            data = soup.find_all("span", attrs={"class":"mbg-nw"})
	    data_view = soup.find_all("a", attrs={"class":"mbg-fb"})
	    link_view = str(data_view[0].get("href"))
	    last_item_content, view_link,item_condition, ended, selling_price, shipping = seller_info(link_view)
            seller = str(data[0].string)
            seller_page = "http://www.ebay.in/usr/"+seller
            print last_item_content, view_link,item_condition, ended, selling_price, shipping
	    #inserting into mysql 
            sql = """insert ignore into fashion4(category, category_url, sub_category, item_content, price, seller_name, seller_page, seller_selling_url, last_item_content, item_condition, selling_price, sold_time, shipping) values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")"""%("fashion",cat_url,sub_cat,item_content,p,seller,seller_page,view_link,last_item_content,item_condition,selling_price,ended,shipping)
            print sql
	    #sys.exit()
	    #try:
            cursor.execute(sql)
            db.commit()
            #except:
            #    db.rollback()





if __name__=="__main__":
    #entering into myseql db named ebay_db
    db = MySQLdb.connect("localhost","root","india123","ebay_db" )
    cursor = db.cursor()
    #calling function for men_tshirt 
    link = "http://fashion.ebay.in/index.html#men_tshirts"
    print link
    page = proxy_module.main(link)
    #working on link with beautiful soup 
    soup = BeautifulSoup(page)
    #fetching all li which contains role=presentation as it contains gender  tabs like man_tshirts where  "
    #where men is gender and tshits are tshirts
    data = soup.find_all("li", attrs={"role":"presentation"})
    #looping on data
    for l in data:
        #converion into string as its typ in <class 'bs4.element.Tag'>
        l = str(l)
        #calling BeautifulSoup on this perticular "l" as  we have to fetch gender  and tabs example men_tshirt 
        #where menn is gender and tshit is its tab 
        data2 = BeautifulSoup(l)
        #now capturing gender and tabs and concatinate it example man_tshit
        #sometime there is null in  data-cat
        if data2.li["data-map"] and data2.li["data-cat"]:
        #captur gender for further use
            gender = str(data2.li["data-map"])
            data2 = data2.li["data-map"]+"_"+data2.li["data-cat"]
            data2=str(data2).strip()
            #maiking a link to fetch like http://fashion.ebay.in/index.html#men_tshirts" 
            link =  "http://fashion.ebay.in/index.html"+"#"+data2
            print link
            #calling module which will give output like
            #gender(type) , link,category, itemcontent, price, seller,created on
            men_tshirts(db,cursor,gender,link,data2,link)
        else:
            print "eroor in data-map  or data-cat"
    db.close()

