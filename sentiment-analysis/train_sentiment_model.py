"""
Aluno: Kirk Patrick Gomes Ferreira - RM356344
FIAP - MLET1 - Grupo: 65
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('./dataset/amazon_reviews.csv')
df = df.dropna(subset=['content'])


def get_sentiment(score):
    if score > 3:
        return "Positive"
    elif score < 3:
        return "Negative"
    else:
        return "Neutral"


df['sentiment'] = df['score'].apply(get_sentiment)

neutral_examples = [
    "The software update takes about 5 minutes to complete.",
    "The product arrived on the scheduled date.",
    "The package contains 500 grams of the item.",
    "The app has several different features.",
    "The instruction manual comes in three languages.",
    "The warranty is valid for one year from the date of purchase.",
    "The device requires two AA batteries to operate.",
    "The product is available in three different sizes.",
    "The company has been in the market for 10 years.",
    "The order can be canceled within 24 hours after purchase."
]

neutral_df = pd.DataFrame({
    'content': neutral_examples,
    'sentiment': ['Neutral'] * len(neutral_examples)
})

df = pd.concat([df, neutral_df], ignore_index=True)

X = df['content']
y = df['sentiment']

le = LabelEncoder()
y_encoded = le.fit_transform(y)

vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 3))
X_vectorized = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

model = LogisticRegression(
    multi_class='ovr', solver='lbfgs', max_iter=1000, class_weight='balanced')

cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')

print(f"Cross-Validation (5-folds) - Accuracies: {cv_scores}")
print(f"Average accuracy: {np.mean(cv_scores):.4f}")
print(f"Standard deviation of accuracy: {np.std(cv_scores):.4f}")

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred, target_names=le.classes_))

conf_matrix = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=le.classes_, yticklabels=le.classes_)
plt.title('Confusion Matrix')
plt.ylabel('True Value')
plt.xlabel('Expected Value')
plt.show()

joblib.dump(model, './models/sentiment_model.joblib')
joblib.dump(vectorizer, './models/vectorizer.joblib')
joblib.dump(le, './models/label_encoder.joblib')


def predict_sentiment(text):
    vectorized_text = vectorizer.transform([text])
    prediction = model.predict(vectorized_text)
    return le.inverse_transform(prediction)[0]


test_sentences = [
    "The software update takes about 5 minutes to complete.",
    "This product is amazing!",
    "I'm very disappointed with this purchase.",
    "The item arrived on time and works as expected.",
    "The package contains 500 grams of the item.",
    "The app crashed multiple times during use.",
    "The product exceeded my expectations in every way."
]

for sentence in test_sentences:
    print(f"Sentence: '{sentence}'")
    print(f"Predicted sentiment: {predict_sentiment(sentence)}\n")

print("Training completed and model saved successfully.")
