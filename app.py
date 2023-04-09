from bs4 import BeautifulSoup
import requests
import re
from flask import Flask, request, render_template
from textblob import TextBlob

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

        final_lyric = ''

        for lyric_html in lyrics_html : 
            final_lyric = final_lyric + re.sub('\[.*?\]', '', lyric_html.text)

        final_lyric = re.sub('\(.*?\)', '', final_lyric)
        
        final_lyric = re.sub(r'(\S)([A-Z])', r'\1\n\2', final_lyric)
        final_lyric = re.sub(r'\s+([A-Z])', r'\n\1', final_lyric)

        final_lyric = re.sub(',', '', final_lyric)
        final_lyric = final_lyric.lower()
        
        array_lyric = final_lyric.split('\n')

        # Sentiment Analyze with matplotlib method
        sentiment_scores = []

        for line in final_lyric.split("\n"):
            sentiment = TextBlob(line).sentiment.polarity
            sentiment_scores.append(sentiment)

        return render_template(
            'lyric.html',
            array_lyric=array_lyric, 
            heading=re.sub('-', ' ', song_title.title())+' by '+re.sub('-', ' ', author.title()), 
            mtplb_sentiment_scores=sentiment_scores
        )

    else:
        return render_template(
            'lyric.html',
            array_lyric=['No lyrics were found base on your input'], 
            heading='No data found'
        )

if __name__ == '__main__':
    app.run()
