import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODEL_DIR, exist_ok=True)

def load_contract_data():
    """Load federal contract data from USASpending."""
    path = os.path.join(DATA_DIR, 'federal_contracts_all.csv')
    if not os.path.exists(path):
        path = os.path.join(DATA_DIR, 'federal_it_contracts.csv')
    if not os.path.exists(path):
        print(f"ERROR: No contract data found. Run download_federal_contracts.py first.")
        return None
    return pd.read_csv(path)

def build_risk_features(df):
    """Build features from contract characteristics."""
    # Encode categorical features
    le_agency = LabelEncoder()
    le_naics = LabelEncoder()
    
    # Fill NAs
    df['agency'] = df['agency'].fillna('Unknown').astype(str)
    df['naics_code'] = df['naics_code'].fillna('Unknown').astype(str)
    df['award_amount'] = pd.to_numeric(df['award_amount'], errors='coerce').fillna(0)
    df['duration_days'] = pd.to_numeric(df['duration_days'], errors='coerce')
    
    df['agency_encoded'] = le_agency.fit_transform(df['agency'])
    df['naics_encoded'] = le_naics.fit_transform(df['naics_code'])
    
    # Log transform award amount (contracts span orders of magnitude)
    df['log_amount'] = np.log1p(df['award_amount'])
    
    # Target: long-duration contract (> 3 years = 1095 days)
    df['is_long_duration'] = (df['duration_days'] > 1095).astype(int)
    
    # High value flag (top 25%)
    amount_threshold = df['award_amount'].quantile(0.75)
    df['is_high_value'] = (df['award_amount'] > amount_threshold).astype(int)
    
    return df, le_agency, le_naics

def train_risk_classifier(df):
    """Train RandomForest to predict long-duration contracts."""
    print("=" * 60)
    print("Federal Contract Risk Classifier")
    print("=" * 60)
    
    features = ['agency_encoded', 'naics_encoded', 'log_amount', 'is_high_value']
    
    # Only use rows with valid duration
    valid_df = df[df['duration_days'].notna()].copy()
    
    if len(valid_df) < 20:
        print(f"ERROR: Only {len(valid_df)} valid contracts with duration data. Need at least 20.")
        return None, None
    
    X = valid_df[features]
    y = valid_df['is_long_duration']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} contracts")
    print(f"Test set: {len(X_test)} contracts")
    print(f"Long-duration rate: {y.mean():.1%}")
    
    # Train RandomForest
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    clf.fit(X_train, y_train)
    
    # Evaluate
    y_pred = clf.predict(X_test)
    
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Short', 'Long']))
    
    # Feature importance
    print(f"\nFeature Importance:")
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': clf.feature_importances_
    }).sort_values('importance', ascending=False)
    for _, row in feature_importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.3f}")
    
    # Agency risk scores
    print(f"\nAgency Risk Scores (probability of long-duration contract):")
    agency_risk = valid_df.groupby('agency').agg({
        'is_long_duration': 'mean',
        'is_high_value': 'mean',
        'award_id': 'count'
    }).rename(columns={'award_id': 'total_contracts'}).sort_values('is_long_duration', ascending=False)
    for agency, row in agency_risk.head(10).iterrows():
        print(f"  {agency}: {row['is_long_duration']:.1%} long-duration, {row['is_high_value']:.1%} high-value ({int(row['total_contracts'])} contracts)")
    
    # Save model
    import joblib
    model_path = os.path.join(MODEL_DIR, 'risk_classifier.pkl')
    joblib.dump(clf, model_path)
    print(f"\nModel saved to {model_path}")
    
    # Save agency risk lookup
    agency_risk.to_csv(os.path.join(DATA_DIR, 'agency_risk_scores.csv'))
    
    # Save metrics
    metrics = {
        'accuracy': float(np.mean(y_test == y_pred)),
        'feature_importance': feature_importance.to_dict('records'),
        'agency_risk': agency_risk.reset_index().to_dict('records'),
        'total_contracts': len(valid_df),
        'long_duration_rate': float(y.mean())
    }
    with open(os.path.join(MODEL_DIR, 'risk_classifier_metrics.json'), 'w') as f:
        json.dump(metrics, f, indent=2)
    
    return clf, agency_risk

def main():
    df = load_contract_data()
    if df is None:
        return
    
    df, le_agency, le_naics = build_risk_features(df)
    clf, agency_risk = train_risk_classifier(df)
    
    if clf is not None:
        print(f"\nRisk classifier trained on {len(df)} federal contracts.")
    return clf

if __name__ == '__main__':
    main()
