# Natural Language Processing (NLP)

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

analyser = SentimentIntensityAnalyzer()

phrases = ["I've just had the absolute worst day, it could not have been any worse.", 
           "Today wasn't the best, I felt a little down and lonely.",
           "I'm okay, I guess.", 
           "Not terrible but not great either.",
           "It was a boring but relaxed day today.", 
           "This was a really lovely afternoon, I had a nice time.", 
           "The sun is out, the birds are singing and I feel ecstatic!",
           "The sun is out, the birds are singing and I feel ectatic!"]

def analyse_sentiment_VADER(text):
    scores = analyser.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.05:        # label 
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"
    if abs(compound) >= 0.5:     # instensity
        intensity = "Strong"
    else:
        intensity = "Mild"
    return {
        "compound": compound,
        "scores": scores,
        "label": label,
        "intensity": intensity}


sentiment_model = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english")

def analyse_sentiment_transformer(text):
    result = sentiment_model(text)
    label = result[0]['label']
    score = result[0]['score']
    return {
        "label": label,
        "score": score}


if __name__ == "__main__":
    for i, phrase in enumerate(phrases, 1):
        result = analyse_sentiment_VADER(phrase)         # VADER ANALYSIS 
        print(f"{i}. {phrase}\n{result}\n")

    for i, phrase in enumerate(phrases, 1):
        result = analyse_sentiment_transformer(phrase)  # Transformer TORCH ANALYSIS
        print(f"{i}. {phrase}\n{result}\n")

