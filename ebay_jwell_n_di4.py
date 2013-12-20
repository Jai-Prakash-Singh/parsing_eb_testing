#!/usr/bin/env python 

from bs4 import BeautifulSoup
import urllib2, urllib, re, time, sys, MySQLdb
import proxy_module

def seller_info(seller_link):
    page = proxy_module.main(seller_link)
    soup=BeautifulSoup(page)
    page.close()
    view_item = soup.find_all("td", attrs={"id":"viewItemId"})
    try:
        view_item = str(view_item[0].a.get("href"))
	view_link = view_item
        print view_link
	page2 = proxy_module.main(view_item)
	soup2=BeautifulSoup(page2)
        page2.close()
	last_item_content = soup2.find_all("h1", attrs={"class":"vi-is1-titleH1"})
	last_item_content = str(last_item_content[0].get_text()).encode('ascii','ignore') 
	item_condition = soup2.find_all("span", attrs={"class":"vi-is1-condText"})
        item_condition = str(item_condition[0].string).encode('ascii','ignore') 
	ended = soup2.find_all("span", attrs={"class":"vi-is1-dt"})
	ended = str(ended[0].get_text()).encode('ascii','ignore') 
	selling_price = soup2.find_all("span", attrs={"id":"v4-27"})
	selling_price=str(selling_price[0].get_text()).encode('ascii','ignore') 
	shipping = soup2.find_all("span", attrs={"id":"fshippingCost"})
        shipping = str(shipping[0].get_text()).encode('ascii','ignore') 
    except:
        view_item ="private"

    if  view_item.lower()=="private":
        last_item_content = "None as it is private "
        view_link = "No link as it is private "
        item_condition = "Private"
        ended = "Not Known  "
	selling_price = "Not Known  "
	shipping = "Not Known"
    #print last_item_content,view_link ,item_condition, ended, selling_price, shipping
    return last_item_content, view_link,item_condition, ended, selling_price, shipping
        
        
        
       
       
def ebay_jwell_n_dia(db, cursor):
    #open main link for jwellery and fashion 
    link = "http://www.ebay.in/chp/jewellery-diamonds"
    print link 
    page = proxy_module.main(link)
    soup = BeautifulSoup(page)
    page.close()
    time.sleep(1)
    #fetching data for all of tabs and sub tabs from mainlink
    data1 = soup.find_all("a", attrs={"_sp":"p2051337.m1685.c281"})
    #fetching data for ony tabs , one or two tabs not comes here so we will fect by combination 
    # of data1, and data2 
    data2 = soup.find_all("a", attrs={"aria-haspopup":"true"})
    # using concept of set we will extract uniqe data
    data3 =set(data1)^set(data2)
    # upto here we have all the usable link 
    for l in data3:
        # now feting a first link for the set of avalable link 
	# and we will do it till last link 
        link2 = str(l.get("href"))
        print link2
	#open usable link which will give us price, and item content 
	page2 = proxy_module.main(link2)
	soup2 = BeautifulSoup(page2)
	page2.close()
	#time.sleep(1)
	#searching for main category
	#like 	    Home>Jewellery & Diamonds>Loose Diamonds
	# where main category is Jewellery & Diamonds
	#main sub cat is Loose Diamonds
	data4 = soup2.find_all("a",attrs={"class":"thrd"})
	#searching for main category  and sub category 
	cat = str(data4[3].get_text()).encode('ascii','ignore') 
	if cat =="About eBay":
	    cat = str(l.get_text())
	sub_cat = str(l.get_text())
        #seacrcing for item content from the link 2 
	item = soup2.find_all("div",attrs={"class":"mtitle"})
	#searching for item price  from the link 2
	price = soup2.find_all("div",attrs={"class":re.compile("^price")})
	for i, p  in zip(item, price):
	    #ites hold the item content 
	    item_content = str(i.a.get_text()).encode('ascii', 'ignore')
	    #it hoil the link will will stor  the info of seller 
	    item_link = str(i.a.get("href"))
	    #it contain the price , i did some maupuation so tha extar text not come  
	    item_price = str("".join(p.get_text().split()[0:2])).encode('ascii','ignore') 
	    # this liink hold the information of seller 
	    link3 = item_link
            print link3
            #print link3
	    # opening link which hold the information of seller 
	    page3 = urllib2.urlopen(link3)
	    soup3 = BeautifulSoup(page3)
	    page3.close()
	    #time.sleep(1)
	    #searching for seller  information  on link3 sourse 
	    seller = soup3.find_all("span", attrs={"class":"mbg-nw"})
	    item_seller = str(seller[0].get_text()).encode('ascii','ignore') 
	    seller_page = "http://www.ebay.in/usr/"+item_seller
            print seller_page
            seller_data = soup3.find_all("a", attrs={"class":"mbg-fb"})
	    seller_link  = str(seller_data[0].get("href"))
            #print seller_link
            seller_info(seller_link)

	    last_item_content,view_link, item_condition, ended, selling_price, shipping = seller_info(seller_link)
	    last_item_content = last_item_content.replace('"','')
	    view_link = view_link.replace('"','')
            item_condition = item_condition.replace('"','')
	    ended = ended.replace('"','')
	    selling_price = selling_price.replace('"','')
	    shipping = shipping.replace('"','')


            #print seller
	    # fetching the name of seller
            cat  = cat.replace('"','')
            sub_cat = sub_cat.replace('"','')
	    item_content = item_content.replace('"','')
	    item_price = item_price.replace('"','')
	    item_seller = item_seller.replace('"','')
	    #print cat,sub_cat,item_content,item_price,item_seller
            sql = """insert  ignore into seller_info(seller_name,seller_url) values("%s","%s")"""%(item_seller,seller_page)
            #print sql
            #sys.exit()
            try:
                cursor.execute(sql)
                db.commit()
            except:
                db.rollback()
	    sql = """insert ignore into j_n_d_record(category,category_url,sub_category,item_content,price,seller_name,seller_page,seller_selling_url,last_item_content,item_condition,selling_price, sold_time,shipping) values("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s")"""%(cat,link,sub_cat,item_content,item_price,item_seller,seller_page,view_link, last_item_content,item_condition, selling_price, ended, shipping)
	    print sql   
            #sys.exit()
            try:
	        # Execute the SQL command
	        #cursor.execute(sql,(link,cat,sub_cat,item_content,item_price,item_seller))
                cursor.execute(sql)
	        # Commit your changes in the database
	        db.commit()
	    except:
	    #	# Rollback in case there is any error
	    	db.rollback()
	    

	    


def main():
    # Open database connection
    db = MySQLdb.connect("localhost","root","india123","ebay_db")
    # prepare a cursor object using cursor() method
    cursor = db.cursor()
    ebay_jwell_n_dia(db,cursor)
    db.close()



        
if __name__=="__main__":
    link = "http://www.ebay.in/chp/jewellery-diamonds"
    #ip_port = "83.99.169.129:8080"
    ip_port = "217.23.67.68:8080"
    proxy_module.main(link)
    main()
