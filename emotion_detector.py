from transformers import pipeline

class EmotionDetector:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification", 
            model="j-hartmann/emotion-english-distilroberta-base"
        )
        
        self.emojimap = {
            "joy": "😄", "anger": "😠", "sadness": "😢", 
            "fear": "😨", "surprise": "😲", "disgust": "🤢", "neutral": "😐"
        }
        
        # Consolidating mapping logic into the Emotion API module
        self.params_map = {
            "joy": {"speed": 1.3, "volume": 6.0, "pitch": 4, "pause_ms": 150},
            "anger": {"speed": 1.4, "volume": 8.0, "pitch": 2, "pause_ms": 80},
            "sadness": {"speed": 0.75, "volume": -3.0, "pitch": -4, "pause_ms": 400},
            "fear": {"speed": 1.2, "volume": -2.0, "pitch": 1, "pause_ms": 100},
            "surprise": {"speed": 1.35, "volume": 5.0, "pitch": 5, "pause_ms": 120},
            "disgust": {"speed": 0.85, "volume": 0.0, "pitch": -2, "pause_ms": 250},
            "neutral": {"speed": 1.0, "volume": 0.0, "pitch": 0, "pause_ms": 200}
        }

    def detect_emotion(self, text):
        results = self.classifier(text)
        best_result = results[0]
        
        emotion = best_result['label'].lower()
        confidence = best_result['score']
        
        params = self.params_map.get(emotion, self.params_map["neutral"])
        
        return {
            "emotion": emotion,
            "confidence": confidence,
            "speed": params["speed"],
            "volume": params["volume"],
            "pitch": params["pitch"],
            "pause_ms": params["pause_ms"],
            "emoji": self.emojimap.get(emotion, "😐")
        }
