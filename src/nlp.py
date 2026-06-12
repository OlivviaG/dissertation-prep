# Natural Language Processing (NLP)

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline
import pandas as pd 

analyser = SentimentIntensityAnalyzer()

phrases = ["I've just had the absolute worst day, it could not have been any worse.", 
           "Today wasn't the best, I felt a little down and lonely.",
           "I'm okay, I guess.", 
           "Not terrible but not great either.",
           "It was a boring but relaxed day today.", 
           "This was a really lovely afternoon, I had a nice time.", 
           "The sun is out, the birds are singing and I feel ecstatic!",
           "The sun is out, the birds are singing and I feel ectatic!"]

check_ins = ["I've felt quite tired today, I just want to go to bed.",
             "I had a really nice day, I went for a walk and had a good chat with a friend.", 
             "I feel pretty good today, I got some work done and had a nice lunch.", 
             "I'm feeling so meh today, it was a bit of a nothing day.", 
             "Today was okay, I cba to do anything.",
             "I was so proud of myself today, I accomplished a lot and felt really good about it.",
             "I didn't do a lot of work today, I met with some mates though.",
             "lowkey rly tired today, I still did some work but I'm ready for bed now.",
             "I just had the best day, I lost my phone and my wallet with all my money in. SO great.",
             "Not the best day, I feel like a bad person.",
             "",
             "lovely and chill day, did shit my pants though",
             "I feel like a troll coming out of a cave, the sun is really nice",
             "I dont know waht to put here, it was a mid day.",
             "I hated today!",
             "I don't know why I even bother sometimes, I feel so out of my depth.",
             "I'm doing so good actually, i'm smarter than I think I am!",
             "Not a lot of work done today, but I had a much needed rest day.",
             "I've been so excited for today but It wasn't all that.",
             "Love this little life, I feel so put together for once.",
             "The mental has taken a dip today, I don't know how to get better."]

check_ins_decline = ["Normal day, got my work done",
                     "Visited my friend and saw her new cat, i love cats",
                     "Just went to the gym, good day.",
                     "today is the best gym day, i get to do arms.",
                     "called a mate from work, it was a lovely chat",
                     "Went on a walk today, the sun is out",
                     "today was okay, i got a lot of work done",
                     "Fine day, cooked a nice meal.",
                     "the sun is out again, it's so nice and warm",
                     "I'm chilling, got a nice day off",
                     "Uneventful day, work was okay",
                     "tuesdays, am i right? boring day.",
                     "I called my mom today, nice to know she's doing well",
                     "I made plans to meet with my friends, looking foward to it",
                     "Nice day, enjoy doing chest in the gym",
                     "Pretty boring day",
                     "All my friends cancelled the plans, I'm feeling a little down about it",
                     "I'm feeling a little lonely, my mom didn't pick up the phone",
                     "My friends don't want to reschedule which hurts a bit",
                     "I feel really alone, I have no one to talk to",
                     "My mental health is taking a dip, do my friends hate me?",
                     "I feel so alone and sad",
                     "I'm a waste of space, all I do is work. No once cares about me.",
                     "I hate myself"]

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


from src.time_series import compute_rolling_stats
from src.anomaly_detection import run_isolation_forest






if __name__ == "__main__":
    list_of_dicts = []
    for check_in in check_ins_decline:
        vader = analyse_sentiment_VADER(check_in)
        vader_compound = vader['compound']

        transformer = analyse_sentiment_transformer(check_in)
        transformer_label = transformer['label']
        transformer_score = transformer['score']

        checkin_row = {'text': check_in, 'vader_compound': vader_compound, 
                       'transformer_label': transformer_label, 'transformer_score': transformer_score}
        list_of_dicts.append(checkin_row)

    df = pd.DataFrame(list_of_dicts)

    # adding a date column 
    df['date'] = pd.date_range(start="2026-05-25", periods=len(df), freq="D")

    # finding anomalies using z-score analysis 
    compute_rolling_stats(df, column='vader_compound', window=7)
    df['sentiment_anomaly_zscore'] = df['vader_compound'] < (df['vader_compound_mean'] - 2 * df['vader_compound_std'])

    # finding anomalies using isolation forest 
    df, forest_model = run_isolation_forest(df, features=["vader_compound"], train_days=14, contamination="auto")

    #df.to_csv("data/sentiment_batch.csv", index=False)

    print(df)
    print(df[['date', 'vader_compound', 'sentiment_anomaly_zscore', 'isolation_forest_score', 'isolation_forest_anomaly']])


