from bs4 import BeautifulSoup 
from selenium.webdriver.common.keys import Keys
import time 
import csv
import pandas as pd
from userinfo import uid,passw
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import jellyfish
import pyodbc


#Defined Global Variables
set_tweet  = set()   ;  same_tweet  = list()  ;  diff_tweet = list()
dict_like  = dict()  ;  dict_reply  = dict()  ;  dict_rt    = dict()   
dict_like2 = dict()  ;  dict_reply2 = dict()  ;  dict_rt2   = dict() 

#Tweet letter filter    
def defined_letters_filter(tweet):
    tweet = tweet.lower()
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i'," ",
               'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    for i in tweet:
        if(i not in letters):
            tweet = tweet.replace(i, '')
    return tweet

#Erase the words in space
def space_cleaner(tweet):
    space = [" "]
    for i in tweet:
        if(i  in space):
            tweet = tweet.replace(i,'')
            return tweet
    return tweet

#Only ascii characters filter
def ascii_filter(tweet):
    letters = list()
    letters.append('£') ; letters.append('é') ; letters.append('½') ; letters.append('¾')
    for i in range(0,128):
        letters.append(chr(i))
        
    for i in tweet:
        if(i not in letters):
            return False
    return True
    

    
#Link cleaning
def link_clean(tweet):
    tweet = tweet.lower()
    tweet = space_cleaner(tweet)
    count = 0
    count = tweet.count("http")
    
    if(count != 0):
        return False
    return True

#Defined tag filter
def defined_tag_filter(tweet):
    count = 0 ; count1 = 0 ; counts = 0
    tweet = tweet.lower()
    count1 = tweet.count("#") ;
    count += tweet.count("#trump")
    count += tweet.count("#usa")
    count += tweet.count("#fake")
    count += tweet.count("#country")
    count += tweet.count("#money")
    count += tweet.count("#donald")
    count += tweet.count("#joe")
    count += tweet.count("#pence")
    count += tweet.count("#white")
    count += tweet.count("#house")
    count += tweet.count("#win")
    count += tweet.count("#vote")
    count += tweet.count("#support")
    count += tweet.count("#president")
    count += tweet.count("#vpdebate")
    count += tweet.count("#debate")
    count += tweet.count("#potus")
    count += tweet.count("#november")
    count += tweet.count("#america")
    count += tweet.count("#election")
    counts = count1 - count  
   
    if(counts != 0):
        return False
    return True


#Spam Control Function
def similarity_control(tweet2):
    tweet2 = defined_letters_filter(tweet2)
    for i in set_tweet:
        i = defined_letters_filter(i)
        similarity  = jellyfish.levenshtein_distance(tweet2,i)
        if(float(similarity / len(tweet2)) <= 0.4):
            return False
    return True


#Fetch Data Functions
def fetch_data(scroll_count):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    #search hashtag since:2020-08-24 until:2020-10-10
    search_hashtag_link = "https://twitter.com/search?q=%23trump%20since%3A2020-08-24%20until%3A2020-10-10&src=typed_query&f=live"
    driver.get(search_hashtag_link)
    time.sleep(20)
    
    
#Fetch Start
    tw_counts = 0 ; current_page = 0  
    while (current_page < scroll_count):
        time.sleep(5)
        start_time2 = datetime.now(); 
        page_source = driver.page_source
        soup = BeautifulSoup(page_source,"html.parser")
        tweets = soup.find_all("div",attrs={"data-testid":"tweet"})
          
        #Parse Processing...
        for i in tweets:
            try:
                tweet  = i.find("div",attrs={"css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0"}).text
                like = i.find("div",attrs={"data-testid":"like"}).text
                reply  = i.find("div",attrs={"data-testid":"reply"}).text
                rt     = i.find("div",attrs={"data-testid":"retweet"}).text
                
                if ((reply == "")):
                    reply = 0
                if((like == "")):
                    like = 0
                if((rt == "")):
                    rt = 0
                    
            #Data filter functions
                if(ascii_filter(tweet) == True):
                    if((link_clean(tweet)) == True):
                        if((similarity_control(tweet) == True)):
                            if(defined_tag_filter(tweet) == True):
                                set_tweet.add(tweet)
                                dict_like[tweet] = like
                                dict_reply[tweet] = reply
                                dict_rt[tweet] = rt
                            else:
                                same_tweet.append(tweet)
                                dict_like2[tweet] = like
                                dict_reply2[tweet] = reply
                                dict_rt2[tweet] = rt
                        else:
                            same_tweet.append(tweet)
                            dict_like2[tweet] = like
                            dict_reply2[tweet] = reply
                            dict_rt2[tweet] = rt
               
                    
            except Exception as ex:
                print("try error")
                print(ex)
        
        
        #Total tweet Counting Process..
        tw_count = len(tweets)
        tw_counts += tw_count
        current_page += 1
        
        
        #Step Ending Print Process
        end_time2 = datetime.now()
        print(current_page,".scroll",tw_counts,".tweet")
        print('Duration: {}'.format(end_time2 - start_time))       

        
        #Scroll Down Process
        last_height = driver.execute_script("return document.body.scrollHeight")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            delay_start = datetime.now() ; print(delay_start)
            print("can't more slip") ; print(new_height," == ",last_height) ; print("delay 10sn")
            time.sleep(5)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if(new_height == last_height):
                break
            else:
                delay_end = datetime.now() ; print("continue process... ",delay_end)
                last_height = new_height
                continue
        last_height = new_height
       
        
        #Delay Process..
        if((current_page % 9000) == 0):
            print("waiting ...10dk")
            start3_time = datetime.now()
            print("Duration date",start3_time)
            time.sleep(600)
    
    
    #Print Processing
    print("total_tweet",tw_counts)
    print(" len diff_tweet=",len(set_tweet))
    print(" len same_tweet=",len(same_tweet))
    
        
#Db Write Process
    diff_tweet = list(set_tweet) ; x = 0 ; y = 0
    con = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                  'SERVER=localhost;'
                  'DATABASE=abdElection2020;'
                  'UID=' + uid + ";"
                  'PWD=' + passw + ";")
   
       
    for i in diff_tweet:
        c = con.cursor()
        query = 'INSERT INTO trump2020 VALUES(?,?,?,?,?)' # insert to database table original tweets
        data = (x,diff_tweet[x],dict_like[i],dict_reply[i],dict_rt[i])
        c.execute(query,data)
        con.commit()
        x += 1

    for j in same_tweet:
        c2 = con.cursor()
        query2 = 'INSERT INTO trump2020same VALUES(?,?,?,?,?)' # insert to database table spam tweets
        data2 = (y,same_tweet[y],dict_like2[j],dict_reply2[j],dict_rt2[j])
        c2.execute(query2,data2)
        con.commit()
        y += 1
        
    print("succesfully db writing finish...")    
    
#Main Process
start_time = datetime.now()
print("starting=",start_time)

scroll_count = 10
fetch_data(scroll_count)
print("data fetch succesfully finish...")
    
end_time = datetime.now()
print('total_Duration: {}'.format(end_time - start_time))
print("start_time:",start_time," end_time:",end_time)