from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, insert, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
import csv
from datetime import datetime

import joblib
from pydantic import BaseModel

SQLALCHEMY_DATABASE_URL = "sqlite:///./amazon_reviews.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    reviewId = Column(String, unique=True, index=True)
    userName = Column(String)
    content = Column(String)
    score = Column(Integer)
    thumbsUpCount = Column(Integer)
    reviewCreatedVersion = Column(String)
    at = Column(String)
    appVersion = Column(String)


class SentimentStats(Base):
    __tablename__ = "sentiment_stats"

    id = Column(Integer, primary_key=True, index=True)
    sentiment = Column(String, unique=True, index=True)
    count = Column(Integer, default=0)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load('./models/sentiment_model.joblib')
vectorizer = joblib.load('./models/vectorizer.joblib')
label_encoder = joblib.load('./models/label_encoder.joblib')


def predict_sentiment(text):
    vectorized_text = vectorizer.transform([text])
    prediction = model.predict(vectorized_text)
    sentiment = label_encoder.inverse_transform(prediction)[0]
    return sentiment


class SentimentRequest(BaseModel):
    text: str


class UpdateStatsRequest(BaseModel):
    sentiment: str


@app.post("/analyze-sentiment")
def analyze_sentiment(request: SentimentRequest):
    sentiment = predict_sentiment(request.text)
    return {"sentiment": sentiment}


def load_csv_to_db(db: Session):
    rows_processed = 0
    with open('./dataset/amazon_reviews.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            stmt = sqlite_upsert(Review).values(
                reviewId=row['reviewId'],
                userName=row['userName'],
                content=row['content'],
                score=int(row['score']),
                thumbsUpCount=int(row['thumbsUpCount']),
                reviewCreatedVersion=row['reviewCreatedVersion'],
                at=row['at'],
                appVersion=row['appVersion']
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=['reviewId'],
                set_={
                    'userName': stmt.excluded.userName,
                    'content': stmt.excluded.content,
                    'score': stmt.excluded.score,
                    'thumbsUpCount': stmt.excluded.thumbsUpCount,
                    'reviewCreatedVersion': stmt.excluded.reviewCreatedVersion,
                    'at': stmt.excluded.at,
                    'appVersion': stmt.excluded.appVersion
                }
            )
            db.execute(stmt)
            rows_processed += 1

            if rows_processed % 1000 == 0:
                db.commit()

    db.commit()
    return rows_processed


@app.post("/load-data")
def load_data(db: Session = Depends(get_db)):
    try:
        rows_processed = load_csv_to_db(db)
        return {
            "message": "Data loaded successfully",
            "rows_processed": rows_processed
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error loading data: {str(e)}")


@app.get("/reviews")
def get_reviews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reviews = db.query(Review).offset(skip).limit(limit).all()
    return reviews


@app.get("/reviews/{review_id}")
def get_review(review_id: str, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.reviewId == review_id).first()
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found.")
    return review


@app.post("/reviews")
def create_review(review: dict, db: Session = Depends(get_db)):
    db_review = Review(**review)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@app.put("/reviews/{review_id}")
def update_review(review_id: str, review_data: dict, db: Session = Depends(get_db)):
    db_review = db.query(Review).filter(Review.reviewId == review_id).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found.")
    for key, value in review_data.items():
        setattr(db_review, key, value)
    db.commit()
    db.refresh(db_review)
    return db_review


@app.delete("/reviews/{review_id}")
def delete_review(review_id: str, db: Session = Depends(get_db)):
    db_review = db.query(Review).filter(Review.reviewId == review_id).first()
    if db_review is None:
        raise HTTPException(status_code=404, detail="Review not found.")
    db.delete(db_review)
    db.commit()
    return {"message": "Review deleted successfully"}


@app.post("/update-stats")
def update_stats(request: UpdateStatsRequest, db: Session = Depends(get_db)):
    sentiment = request.sentiment
    db_stat = db.query(SentimentStats).filter(
        SentimentStats.sentiment == sentiment).first()

    if db_stat:
        db_stat.count += 1
    else:
        db_stat = SentimentStats(sentiment=sentiment, count=1)
        db.add(db_stat)

    db.commit()
    db.refresh(db_stat)

    return {"message": f"Updated {sentiment} count to {db_stat.count}"}


@app.get("/sentiment-stats")
def get_sentiment_stats(db: Session = Depends(get_db)):
    stored_stats = db.query(SentimentStats).all()

    if stored_stats:
        return {stat.sentiment: stat.count for stat in stored_stats}
    else:
        reviews = db.query(Review).all()
        sentiments = [predict_sentiment(review.content) for review in reviews]
        stats = {
            "Positive": sentiments.count("Positive"),
            "Neutral": sentiments.count("Neutral"),
            "Negative": sentiments.count("Negative")
        }

        for sentiment, count in stats.items():
            db.add(SentimentStats(sentiment=sentiment, count=count))
        db.commit()

        return stats


def initialize_stats(db: Session):
    existing_stats = db.query(SentimentStats).count()
    if existing_stats == 0:
        reviews = db.query(Review).all()
        sentiments = [predict_sentiment(review.content) for review in reviews]
        stats = {
            "Positive": sentiments.count("Positive"),
            "Neutral": sentiments.count("Neutral"),
            "Negative": sentiments.count("Negative")
        }
        for sentiment, count in stats.items():
            db.add(SentimentStats(sentiment=sentiment, count=count))
        db.commit()


@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    initialize_stats(db)
    db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
