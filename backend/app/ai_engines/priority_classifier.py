import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

class EmergencyPriorityClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.is_trained = False
        self._train_default_model()

    def _train_default_model(self):
        """Train a lightweight Random Forest model on synthetic emergency triage feature data."""
        np.random.seed(42)
        # Features: [age, chest_pain (0/1), shortness_of_breath (0/1), loss_of_consciousness (0/1), severe_bleeding (0/1), heart_rate, systolic_bp]
        X = []
        y = [] # 0: LOW, 1: MODERATE, 2: HIGH, 3: CRITICAL

        for _ in range(500):
            age = np.random.randint(18, 90)
            chest_pain = np.random.choice([0, 1], p=[0.7, 0.3])
            sob = np.random.choice([0, 1], p=[0.6, 0.4])
            loc = np.random.choice([0, 1], p=[0.85, 0.15])
            bleeding = np.random.choice([0, 1], p=[0.8, 0.2])
            hr = np.random.randint(50, 160)
            sbp = np.random.randint(70, 190)

            # Heuristic assignment for synthetic training labels
            if loc == 1 or (chest_pain == 1 and sob == 1 and age > 50) or hr > 140 or sbp < 80:
                label = 3 # CRITICAL
            elif chest_pain == 1 or bleeding == 1 or sob == 1:
                label = 2 # HIGH
            elif hr > 110 or sbp > 150:
                label = 1 # MODERATE
            else:
                label = 0 # LOW

            X.append([age, chest_pain, sob, loc, bleeding, hr, sbp])
            y.append(label)

        self.model.fit(np.array(X), np.array(y))
        self.is_trained = True

    def classify_emergency(self, age: int, emergency_type: str, chest_pain: bool, 
                           shortness_of_breath: bool, loss_of_consciousness: bool, 
                           severe_bleeding: bool, heart_rate: int = 80, 
                           systolic_bp: int = 120):
        """
        Classifies an emergency into priority levels: CRITICAL, HIGH, MODERATE, LOW
        and calculates a priority severity score between 0 and 100.
        """
        features = np.array([[
            age,
            int(chest_pain),
            int(shortness_of_breath),
            int(loss_of_consciousness),
            int(severe_bleeding),
            heart_rate,
            systolic_bp
        ]])

        probs = self.model.predict_proba(features)[0]
        predicted_class_idx = np.argmax(probs)
        
        mapping = {0: "LOW", 1: "MODERATE", 2: "HIGH", 3: "CRITICAL"}
        priority = mapping.get(predicted_class_idx, "HIGH")

        # Safety Overrides for critical conditions
        if emergency_type in ["Heart Attack", "Stroke", "Major Trauma"] and (chest_pain or loss_of_consciousness):
            priority = "CRITICAL"
        elif emergency_type in ["Heart Attack", "Stroke"]:
            if priority in ["LOW", "MODERATE"]:
                priority = "HIGH"

        # Calculate Priority Score (0 - 100)
        base_score = 50
        if priority == "CRITICAL":
            base_score = 90 + int(loss_of_consciousness) * 5 + int(chest_pain) * 5
        elif priority == "HIGH":
            base_score = 75 + int(shortness_of_breath) * 5 + int(severe_bleeding) * 5
        elif priority == "MODERATE":
            base_score = 55
        else:
            base_score = 35

        score = float(min(100.0, max(10.0, base_score)))

        return {
            "priority": priority,
            "priority_score": score,
            "probability_distribution": {
                mapping[i]: round(float(probs[i]), 3) for i in range(len(probs))
            }
        }

# Global Instance
classifier_instance = EmergencyPriorityClassifier()
