import tensorflow as tf
from tensorflow import keras
import numpy as np


data = keras.datasets.imdb


word_index = data.get_word_index()
word_index = {k:(v+3) for k, v in word_index.items()}
word_index["<PAD>"] = 0
word_index["<START>"] = 1
word_index["<UNK>"] = 2
word_index["<UNUSED>"] = 3


reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

def review_encode(s):
	encoded= [1]
	for word in s:
		if word.lower() in word_index:
			encoded.append(word_index[word.lower()])
		else:
			encoded.append(2)
	return encoded

model = keras.models.load_model("model.h5")
input("Please make sure your review is in review.txt in this dirrectory. That is the textfile used for the predictuion (Type any key and press enter to aknowledge)")
with open("review.txt", encoding="utf-8") as f:
	for line in f.readlines():
		nline = line.replace(",", "").replace(".", "").replace("(", "").replace(")", "").replace(":", "").replace("\"","").strip().split(" ")
		encode = review_encode(nline)
		encode = keras.preprocessing.sequence.pad_sequences([encode], value=word_index["<PAD>"], padding="post", maxlen=250) # make the data 250 words long
		predict = model.predict(encode)
		print(line)
		print(encode)
		# predict from 0-1 negative-positive
		#print(predict[0])
		prediction = predict[0]

		if prediction < .21:
			print("With the given reviews, the model thinks that the text writer thinks the topic is poorly (1 star)")

		elif prediction < .41:
			print("With the given reviews, the model thinks that the text writer thinks the topic is bad (2 stars)")
		
		elif prediction < .61:
			print("With the given reviews, the model thinks that the text writer thinks the topic is ok (3 stars)")
		
		elif prediction < .81:
			print("With the given reviews, the model thinks that the text writer thinks the topic is good (4 stars)")
		
		else:
			print("With the given reviews, the model thinks that the text writer thinks the topic is perfect (5 stars)")
