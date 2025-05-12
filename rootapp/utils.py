import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler

priority_map = {"low": 1, "medium": 2, "high": 3}

def time_to_float(t):
    return t.hour + t.minute / 60

def float_to_time(f):
    hour = int(f)
    minute = int((f - hour) * 60)
    return f"{hour:02d}:{minute:02d}"

def optimize_schedule(tasks_queryset):
    if not tasks_queryset.exists():
        print("No tasks found.")
        return []

    print("Task count:", tasks_queryset.count())
    tasks = []

    for task in tasks_queryset:
        print(f"- {task.task_description} | {task.priority} | {task.date} {task.time} to {task.deadline}")
        tasks.append({
            "name": task.task_description,
            "duration": 1.5,
            "preferred_date": str(task.date),
            "preferred_time": time_to_float(task.time),
            "priority": task.priority.lower(),
            "deadline": str(task.deadline)
        })

    df = pd.DataFrame(tasks)
    print("DataFrame:\n", df)

    df["priority_num"] = df["priority"].map(priority_map)
    df["preferred_date"] = pd.to_datetime(df["preferred_date"])
    df["deadline"] = pd.to_datetime(df["deadline"])
    df["urgency"] = (df["deadline"] - datetime.now()).dt.days

    scaler = MinMaxScaler()
    df[["norm_priority", "norm_urgency"]] = scaler.fit_transform(df[["priority_num", "urgency"]])
    df["score"] = 0.7 * df["norm_priority"] + 0.3 * (1 - df["norm_urgency"])
   
      
    df = df.sort_values(by="score", ascending=False).reset_index(drop=True)

    schedule = []
    calendar = {}
     
    for _, row in df.iterrows():
        date = row["preferred_date"]
        duration = row["duration"]
        preferred_time = row["preferred_time"]
        task_name = row["name"]

        while True:
            date_str = date.strftime("%Y-%m-%d")
            if date_str not in calendar:
                calendar[date_str] = []

            slots = calendar[date_str]
            current_time = preferred_time

            while current_time + duration <= 17:
                conflict = any(
                    (current_time < end and current_time + duration > start)
                    for start, end in slots
                )
                if not conflict:
                    slots.append((current_time, current_time + duration))
                    schedule.append({
                        "task": task_name,
                        "description": task_name,  # Include full description here
                        "date": date_str,
                        "start_time": float_to_time(current_time),
                        "end_time": float_to_time(current_time + duration)
                    })
                    break
                current_time += 0.5
            else:
                date += timedelta(days=1)
                preferred_time = 9
                continue
            break

    print("Final Optimized Schedule:")
    for entry in schedule:
        print(entry)

    return schedule



import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
import os
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()


# Load and preprocess training data
def load_data(file_path='train.txt'):
    file_path = os.path.join(os.path.dirname(__file__), file_path)
    data, sentiments = [], []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                feedback, sentiment = line.strip().split(';')
                data.append(feedback)
                sentiments.append(sentiment)
            except ValueError:
                continue
    return data, sentiments

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return ' '.join(filtered)

# Train model
data, sentiments = load_data()
cleaned_data = [preprocess_text(d) for d in data]
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(cleaned_data)

model = LogisticRegression(class_weight='balanced', max_iter=1000)
model.fit(X, sentiments)

def predict_sentiment(text):
    processed = preprocess_text(text)
    features = vectorizer.transform([processed])
    return model.predict(features)[0]
