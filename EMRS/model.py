import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
import pickle


df=pd.read_csv('dataset.csv', encoding_errors='ignore')
le = LabelEncoder()
df['label'] = le.fit_transform(df['genre'])
df=df.sample(frac=1)
X_train, X_test, Y_train, Y_test = train_test_split(df['lyrics'], df['label'], test_size=0.2, random_state=42)
clf=Pipeline([('vectorizer',CountVectorizer()), ('xgb',XGBClassifier())])
clf.fit(X_train,Y_train)
pickle.dump(le, open("le.pickle", "wb"))      # Saving label encoder to use it for inverse_transform() later
pickle.dump(clf, open("model.pickle", "wb"))  # Saving ML model