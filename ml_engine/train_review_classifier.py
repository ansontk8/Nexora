import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os

def train_review_model():
    # Load dataset
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'review_dataset.csv')
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return

    df = pd.read_csv(dataset_path)
    
    # Preprocessing
    df['text'] = df['text'].fillna('')
    df['text_len'] = df['text'].apply(len)
    
    # Feature engineering: TF-IDF for text
    # We use n-grams to catch repetitive word patterns common in fake reviews
    vectorizer = TfidfVectorizer(max_features=500, stop_words='english', ngram_range=(1, 2))
    X_text = vectorizer.fit_transform(df['text'])
    
    # Combine TF-IDF features with numeric rating and text length
    from scipy.sparse import hstack
    X = hstack((X_text, df[['rating', 'text_len']].values))
    
    y = df['verdict']
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train - Using Random Forest as requested
    # We use max_depth and min_samples_leaf to prevent overfitting
    from sklearn.ensemble import RandomForestClassifier
    
    print("Training Random Forest Classifier...")
    clf = RandomForestClassifier(
        n_estimators=100, 
        max_depth=15, 
        min_samples_leaf=2,
        random_state=42
    )
    clf.fit(X_train, y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(model_dir, exist_ok=True)
    
    joblib.dump(clf, os.path.join(model_dir, 'review_classifier.joblib'))
    joblib.dump(vectorizer, os.path.join(model_dir, 'review_vectorizer.joblib'))
    
    print(f"\nModel and vectorizer saved to {model_dir}")

if __name__ == "__main__":
    train_review_model()
