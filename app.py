from bs4 import BeautifulSoup
import requests
import re
from flask import Flask, request, render_template
# Sentiment with TextBlok
from textblob import TextBlob
# Sentiment with Natural Language Toolkit
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_lyric', methods=['POST'])
def search_lyric():
    song_title = request.form['song_title']
    author = request.form['author']

    song_title = re.sub(' ', '-', song_title.lower())

    author = re.sub(' ', '-', author.capitalize())

    link = 'https://genius.com/' + author + '-' + song_title + '-lyrics'
    
    html_text = requests.get(link)

    if html_text.status_code == 200:
        soup = BeautifulSoup(html_text.text, 'lxml')

        lyrics_html = soup.find_all('div', class_ = 'Lyrics__Container-sc-1ynbvzw-5 Dzxov')

        lyrics = []

        for lyric_html in lyrics_html :
            lyrics.extend([lyric for lyric in lyric_html.stripped_strings])

        clean_lyrics = []

        for lyric in lyrics:
            lyric = re.sub('\(.*?\)', '', lyric)
            lyric = re.sub(',', '', lyric)
            lyric = re.sub("'", "", lyric)
            lyric = re.sub("`", "", lyric)
            if '[' not in lyric:
                clean_lyrics.append(lyric.lower())

        # Sentiment Analyze with TextBlob method
        tblb_sentiment_scores = []

        for lyric in clean_lyrics:
            tblb_score = TextBlob(lyric.lower()).sentiment.polarity
            tblb_sentiment_scores.append(tblb_score)

        # Sentiment Analyze with nltk method
        sia = SentimentIntensityAnalyzer()
        nltk_sentiment_scores = []

        for lyric in clean_lyrics:
            nltk_score = sia.polarity_scores(lyric.lower())
            nltk_score['text'] = lyric.lower()
            nltk_sentiment_scores.append(nltk_score)

        return render_template(
            'lyric.html',
            array_lyric=lyrics, 
            heading=re.sub('-', ' ', song_title.title())+' by '+re.sub('-', ' ', author.title()), 
            tblb_sentiment_scores=tblb_sentiment_scores,
            nltk_sentiment_scores=nltk_sentiment_scores
        )

    else:
        return render_template(
            'lyric.html',
            array_lyric=['No lyrics were found base on your input','Make sure you did not make any typo or use any punctuation'], 
            heading='No data found'
        )

if __name__ == '__main__':
    app.run()
