import csv
import tensorflow as tf
from tensorflow import keras
import numpy as np
import pandas as pd
import praw
import threading
import time
from datetime import datetime
#https://towardsdatascience.com/scraping-reddit-data-1c0af3040768 https://www.reddit.com/prefs/apps
#https://www.geeksforgeeks.org/python-test-if-string-contains-element-from-list/
#https://www.nasdaq.com/market-activity/stocks/screener

now = datetime.now()

data = keras.datasets.imdb


word_index = data.get_word_index()
word_index = {k:(v+3) for k, v in word_index.items()}
word_index["<PAD>"] = 0
word_index["<START>"] = 1
word_index["<UNK>"] = 2
word_index["<UNUSED>"] = 3
reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

current_time = now.strftime("%H:%M:%S")
#print("Start Time =", current_time)
reference_words = []
line_count = 0
reddit_posts = []
def read_in_key_words(file):
    global reference_words
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        global line_count
        for row in csv_reader:
            item_counter=0
            for item in row:
                if(item_counter==0 or item_counter==1):
                    reference_words.append(item)
                item_counter+=1
            line_count+=1

def scrape_reddit(subreddit,thread_number):
    global reference_words
    global reddit_posts
    #print('Thread: '+str(thread_number)+" started")
    reddit = praw.Reddit(client_id='secret', client_secret='secret', user_agent='secret')
    hot_posts = reddit.subreddit(subreddit).hot(limit=1000)
    for post in hot_posts:
        #Fix ele is not defined issue
        for word in reference_words:
            if(word in post.selftext):
                reddit_posts.append(post.selftext)
        
    #print("finished printing")
#gets keywords that are searched for in reddit thread
print("Reading in CSV")
read_in_key_words("nasdaq_screener_1618621880006.csv")

print("We are searching for "+str(line_count/2)+" many stocks and 2X that many key words")
#based on list found at: https://www.reddit.com/r/ListOfSubreddits/comments/ja8du7/list_of_economic_and_stock_market_subreddits/
list_stock_subreddits = ['investing','Stocks','Economics','StockMarket','Economy',
                        'GlobalMarkets','WallStreetBets','Options','Finance','Bitcoin','Dividends',
                        'Cryptocurrency','SecurityAnalysis','AlgoTrading','DayTrading','PennyStocks',
                        'PennystocksDD','RobinHoodPennyStocks', 'algorithmictrading',
                         'ausstocks', 'CanadianInvestor', 'Daytrading', 'dividends', 'econmonitor', 
                         'finance', 'InvestmentClub', 'quant', 'quantfinance','Stock_Picks', 'Trading' ,
                         'UKInvesting', 'weedstocks','ValueInvesting']
def review_encode(s):
	encoded= [1]
	for word in s:
		if word.lower() in word_index:
			encoded.append(word_index[word.lower()])
		else:
			encoded.append(2)
	return encoded

model = keras.models.load_model("Product-rating-predictor/model.h5")
bad_stocks =[]
good_stocks =[]
def predict_stocks(post):
    global reddit_posts
    global reference_words
    global bad_stocks
    global good_stocks
    global model
    
    nline = post.replace(",", "").replace(".", "").replace("(", "").replace(")", "").replace(":", "").replace("\"","").strip().split(" ")
    encode = review_encode(nline)
    encode = keras.preprocessing.sequence.pad_sequences([encode], value=word_index["<PAD>"], padding="post", maxlen=250) # make the data 250 words long
    predict = model.predict(encode)
    #print(encode)
    prediction = predict[0]
    for word in reference_words:
        #print('Running stock predictor')
        if word in post:
            if prediction < .41:
                print(word+" stock price will go down")
                bad_stocks.append(word)
                #elif prediction < .61:
                #   print("With the given reviews, the model thinks that the text writer thinks the topic is ok (3 stars)")
                
            else:
                print(word+" stock price will go up")
                good_stocks.append(word)
#print(reference_words)
thread_list = []
print("We are also using "+str(len(list_stock_subreddits))+" subreddits to collect data")
thread_counter = 0;

for subreddit in list_stock_subreddits:
    x = threading.Thread(target=scrape_reddit,args=(subreddit,thread_counter))
    thread_counter+=1
    thread_list.append(x)
    x.start()
dead_thread_count=0



while(len(thread_list)>0):
    active_thread_count=0
    for thread in thread_list:
        #removes finished threads
        if not thread.is_alive():
            thread_list.remove(thread)
            dead_thread_count+=1
            
        else:
            active_thread_count+=1
    time.sleep(20)
print("Data Scrapped and filtered")
print("Predicting stock changes")
thread_list = []
for post in reddit_posts:
    predict_stocks(post)
    break

now2 = datetime.now()
current_time2 = now2.strftime("%H:%M:%S")
print("Start Time: "+current_time)
print("End Time: "+current_time2)
#prediction is it will go up if good_stock is passed in as list and down if bad_stock is passed in
stop_threads = False
def find_stock(stock):
    global stop_threads
    for stocks in bad_stocks:
        if(stocks==stock):
            print(stock+" price will go down")
            break;
    for stocks in bad_stocks:
        if(stocks==stock):
            print(stock+" price will go up")
            break;
    print(stock+" price will stay the same")
user_request = input("Which stocks do you want to know about?")
while(not(user_request=='finished')):
    find_stock(user_request)
    user_request = input("Which stocks do you want to know about?")

                