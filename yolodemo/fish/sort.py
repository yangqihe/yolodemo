# sort.py
from filterpy.kalman import KalmanFilter
import numpy as np
from collections import deque

class Track:
    count = 0

    def __init__(self, bbox):
        self.kf = KalmanFilter(dim_x=7, dim_z=4)
        self.kf.F = np.array([[1, 0, 0, 0, 1, 0, 0],
                              [0, 1, 0, 0, 0, 1, 0],
                              [0, 0, 1, 0, 0, 0, 1],
                              [0, 0, 0, 1, 0, 0, 0],
                              [0, 0, 0, 0, 1, 0, 0],
                              [0, 0, 0, 0, 0, 1, 0],
                              [0, 0, 0, 0, 0, 0, 1]])
        self.kf.H = np.array([[1, 0, 0, 0, 0, 0, 0],
                              [0, 1, 0, 0, 0, 0, 0],
                              [0, 0, 1, 0, 0, 0, 0],
                              [0, 0, 0, 1, 0, 0, 0]])
        self.kf.R *= 10.
        self.kf.P *= 10.
        self.kf.Q *= 0.01
        self.kf.x[:4] = np.array(bbox).reshape((4, 1))
        self.id = Track.count
        Track.count += 1
        self.hits = 0
        self.no_losses = 0

class Sort:
    def __init__(self, max_age=5, min_hits=1):
        self.max_age = max_age
        self.min_hits = min_hits
        self.tracks = []

    def update(self, detections):
        matched = []
        unmatched_tracks = []
        unmatched_dets = []

        # Predict new positions
        for track in self.tracks:
            track.kf.predict()

        for t, track in enumerate(self.tracks):
            if len(detections) == 0:
                unmatched_tracks.append(t)
                continue

            distances = [np.linalg.norm(track.kf.x[:2].ravel() - det[:2]) for det in detections]
            min_index = np.argmin(distances)
            if distances[min_index] < 50:
                track.kf.update(detections[min_index])
                track.hits += 1
                track.no_losses = 0
                matched.append((t, min_index))
                detections.pop(min_index)
            else:
                unmatched_tracks.append(t)

        for det in detections:
            self.tracks.append(Track(det))

        # Age old tracks
        for t in unmatched_tracks:
            self.tracks[t].no_losses += 1

        # Remove dead tracks
        self.tracks = [t for t in self.tracks if t.no_losses < self.max_age]

        results = []
        for track in self.tracks:
            if track.hits >= self.min_hits:
                results.append((track.kf.x[:4].ravel(), track.id))
        return results
