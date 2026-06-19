# API LAYERRR

from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.database import save_checkin, initialise_db, get_checkins
from src.nlp import analyse_sentiment_VADER, analyse_sentiment_transformer
from src.time_series import compute_rolling_stats
from src.anomaly_detection import compute_zscore, flag_anomalies_zscore, run_isolation_forest

class CheckIn(BaseModel):
    user_id: int
    energy_level: float = Field(ge=1, le=10)
    stress_level: float = Field(ge=1, le=10)
    heart_rate: float = Field(ge=40, le=140)
    mood_text: str

app = FastAPI() 

initialise_db()         # runs once at startup - make sure tables exist 


@app.get("/")
def read_root():
    return {"message": "Hello from signum backend"}


@app.post("/checkin")
def submit_checkin(checkin: CheckIn):
    # run sentiment only if there's actual text
    if checkin.mood_text.strip():
        vader = analyse_sentiment_VADER(checkin.mood_text)
        transformer = analyse_sentiment_transformer(checkin.mood_text)
        vader_compound = vader["compound"]
        transformer_label = transformer["label"]
        transformer_score = transformer["score"]
    else:
        vader_compound = None
        transformer_label = None
        transformer_score = None

    save_checkin(
        user_id=checkin.user_id,
        energy=checkin.energy_level,
        stress=checkin.stress_level,
        heart_rate=checkin.heart_rate,
        mood_text=checkin.mood_text,
        vader_compound=vader_compound,
        transformer_label=transformer_label,
        transformer_score=transformer_score,
    )
    return {
        "message": "received",
        "data": checkin,
        "sentiment": {
            "vader_compound": vader_compound,
            "transformer_label": transformer_label,
            "transformer_score": transformer_score,
        },
    }


@app.get("/users/{user_id}/anomalies")
def get_anomalies(user_id: int, method: str = "zscore"):
    df = get_checkins(user_id)
    if df.empty:
        return {"user_id": user_id, 
                "method": method, 
                "anomalies": [], 
                "message": "No check-in history"}

    # prepare rolling stats (needed by both methods)
    df = compute_rolling_stats(df, column="heart_rate")

    if method == "zscore":
        df = compute_zscore(df)
        df = flag_anomalies_zscore(df)
        flagged = df[df["is_anomaly_zscore"] == True]
        flag_column = "heart_rate_zscore"
    else:
        df, _ = run_isolation_forest(df, features=["heart_rate"])
        flagged = df[df["isolation_forest_anomaly"] == True]
        flag_column = "isolation_forest_score"

    anomalies = []
    for _, row in flagged.iterrows():
        anomalies.append({
            "timestamp": row["timestamp"],
            "heart_rate": row["heart_rate"],
            "score": row[flag_column],
        })

    if len(df) < 7:
        return {"user_id": user_id, "method": method, "anomalies": [],
                "message": "Not enough history for reliable detection (need at least 7 check-ins)"}