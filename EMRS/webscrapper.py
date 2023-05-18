from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
import re
import contractions
import re, unicodedata
import inflect
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from keras.preprocessing.text import text_to_word_sequence
import pickle

# Remove contractions ex. didn't -> did not
def denoise(x):
  text=contractions.fix(x)
  return text
  
# Tokenizing data
def tokenize(x):
  return text_to_word_sequence(x)

# Remove non-ASCII characters from list of tokenized words
def remove_non_ascii(x):
  new_words = []
  for word in x:
    new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    new_words.append(new_word)
  return new_words

# Convert all characters to lowercase from list of tokenized words
def to_lowercase(x):
  new_words = []
  for word in x:
    new_word = word.lower()
    new_words.append(new_word)
  return new_words

# Remove punctuation from list of tokenized words
def remove_punctuation(x):
  new_words = []
  for word in x:
    new_word = re.sub(r'[^\w\s]', '', word)
    if new_word != '':
      new_words.append(new_word)
  return new_words

# Replace all interger occurrences in list of tokenized words with textual representation
def replace_numbers(x):
  p = inflect.engine()
  new_words = []
  for word in x:
    if word.isdigit():
      new_word = p.number_to_words(word)
      new_words.append(new_word)
    else:
      new_words.append(word)
  return new_words

# Remove stop words from list of tokenized words
def remove_stopwords(x):  
  new_words = []
  for word in x:
    if word not in stopwords.words('english'):
      new_words.append(word)
  return new_words

# Lemmatize verbs in list of tokenized words
def lemmatize_verbs(x):
  lemmatizer = WordNetLemmatizer()
  lemmas = []
  for word in x:
    lemma = lemmatizer.lemmatize(word, pos='v')
    lemmas.append(lemma)
  return lemmas

# Driver function to normalize text
def normalize_text(x):
  x = denoise(x)
  x = tokenize(x)
  x = remove_non_ascii(x)
  x = to_lowercase(x)
  x = remove_punctuation(x)
  x = replace_numbers(x)
  x = lemmatize_verbs(x)
  x = ' '.join([word for word in x])
  return x

# Predicts genre for given lyrics
def predict_genre(lyrics):
    inp=[]
    inp.insert(0, lyrics)
    clf=pickle.load(open("model.pickle", "rb"))
    le=pickle.load(open("le.pickle", "rb"))
    out=clf.predict(inp)
    genre=le.inverse_transform(out)
    return genre

# Fetches lyrics for given song
def fetch_lyrics(artist, song):
    base_url = f"https://www.azlyrics.com/lyrics/{artist}/{song}.html"
    delay = 8
    try:
        html_page = urlopen(base_url)
        soup = BeautifulSoup(html_page, 'html.parser')
        html_pointer = soup.find('div', attrs={'class':'lyricsh'})
        inc_artist_name = html_pointer.find_next('b').contents[0].strip()
        inc_artist_name = inc_artist_name.split()
        artist_name = ' '.join(inc_artist_name[:len(inc_artist_name)-1])
        html_pointer = soup.find('div', attrs={'class':'ringtone'})
        inc_song_name = html_pointer.find_next('b').contents[0].strip()
        song_name = inc_song_name.strip('"')
        lyrics = html_pointer.find_next('div').text.strip()
        lyrics=' '.join(lyrics.split('\n'))
    except:
        return "failed", "failed", "failed"
    finally:
        sleep(delay)
    lyrics=normalize_text(lyrics)
    return artist_name, song_name, lyrics