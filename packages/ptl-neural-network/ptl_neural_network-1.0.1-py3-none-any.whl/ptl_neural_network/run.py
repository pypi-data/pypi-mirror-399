import numpy as np
from PIL import Image
import pickle

def sigmoid(x): return 1 / (1 + np.exp(-x))

class NeuralNetwork:
    def __init__(self, w1, w2):
        self.w1 = w1
        self.w2 = w2

    def predict(self, x):
        z1 = sigmoid(np.dot(x, self.w1))
        z2 = sigmoid(np.dot(z1, self.w2))
        return np.argmax(z2)

def extract_features(img):
    arr = np.array(img, dtype=np.float32) / 255.0
    h, w = arr.shape
    mean = np.mean(arr)
    std = np.std(arr)
    aspect_ratio = w / h
    horz_edges = np.sum(np.abs(arr[:, 1:] - arr[:, :-1])) / (h * (w - 1))
    vert_edges = np.sum(np.abs(arr[1:, :] - arr[:-1, :])) / ((h - 1) * w)
    row_diffs = np.mean(np.abs(np.diff(arr, axis=0)))
    col_diffs = np.mean(np.abs(np.diff(arr, axis=1)))
    return np.array([mean, std, aspect_ratio, horz_edges, vert_edges, row_diffs, col_diffs])

def main():
    with open("../../CONFIG", "r") as f:
        config = f.read().strip().split("\n")
        MODEL_FILE = config[3].split("=")[1]
    
    with open('../../'+MODEL_FILE, "rb") as f:
        data = pickle.load(f)
    
    w1, w2 = data['w1'], data['w2']
    label_map = data['label_map']
    reverse_map = {v: k for k, v in label_map.items()}
    nn = NeuralNetwork(w1, w2)
    
    while True:
        path = input("Enter path to PNG image (or press Enter to quit): ").strip()
        if not path:
            break
        try:
            img = Image.open(path).convert('L')
            features = extract_features(img)
            pred = nn.predict(features)
            print(f"Predicted object: {reverse_map[pred]}")
        except Exception as e:
            print(f"Error: {e}")
