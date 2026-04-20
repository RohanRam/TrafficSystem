import numpy as np
import librosa
import tensorflow as tf
import tensorflow_hub as hub
import csv
import io
import urllib.request

class AudioDetector:
    def __init__(self):
        # Load YAMNet from TF Hub
        print("Loading YAMNet model...")
        self.model = hub.load('https://tfhub.dev/google/yamnet/1')
        print("Model loaded.")
        
        # Load YAMNet class names
        class_map_path = self.model.class_map_path().numpy().decode('utf-8')
        class_names = []
        with tf.io.gfile.GFile(class_map_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                class_names.append(row['display_name'])
        self.class_names = class_names
        
        # Target classes indicating an emergency vehicle
        target_keywords = ['Siren', 'Ambulance (siren)', 'Police car (siren)', 'Fire engine, fire truck (siren)']
        self.target_indices = [i for i, name in enumerate(class_names) if name in target_keywords]

    def process_audio_chunk(self, waveform, sr=16000):
        """
        Process a chunk of audio to detect sirens.
        waveform: 1D numpy array of audio samples.
        sr: Sample rate. YAMNet requires 16000 Hz.
        """
        if sr != 16000:
            waveform = librosa.resample(waveform, orig_sr=sr, target_sr=16000)
            
        # Ensure it's single precision float
        waveform = waveform.astype(np.float32)
        
        # Run inference
        scores, embeddings, spectrogram = self.model(waveform)
        
        # Average over all segments in this chunk
        scores_np = scores.numpy()
        mean_scores = np.mean(scores_np, axis=0)
        
        # Check if any target class has a high score
        is_emergency = False
        top_class_index = mean_scores.argmax()
        
        # Check against threshold
        for idx in self.target_indices:
            if mean_scores[idx] > 0.15: # Confidence threshold
                is_emergency = True
                break
                
        highest_scoring_class = self.class_names[top_class_index]
        return is_emergency, highest_scoring_class, mean_scores[top_class_index]
