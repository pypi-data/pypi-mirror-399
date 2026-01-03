import os
import numpy as np
from PIL import Image
import pickle
import time

LEARNING_RATE = 0.1
MAX_ITER = 100000
TARGET_ERROR = 0.02
MODEL_FILE = "../../model.pkl"

with open("CONFIG", "r") as f:
    config = f.read().strip().split("\n")
    LEARNING_RATE = float(config[0].split("=")[1])
    MAX_ITER = int(config[1].split("=")[1])
    TARGET_ERROR = float(config[2].split("=")[1])
    MODEL_FILE = '../../'+config[3].split("=")[1]

def get_label_map(filenames):
    labels = sorted(set(os.path.splitext(f)[0] for f in filenames))
    return {name: i for i, name in enumerate(labels)}

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

    return np.array([
        mean, std, aspect_ratio,
        horz_edges, vert_edges,
        row_diffs, col_diffs
    ])

def one_hot(index, size):
    vec = np.zeros(size)
    vec[index] = 1
    return vec

def sigmoid(x): return 1 / (1 + np.exp(-x))
def sigmoid_deriv(x): return x * (1 - x)

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        np.random.seed(1)
        self.w1 = 2 * np.random.rand(input_size, hidden_size) - 1
        self.w2 = 2 * np.random.rand(hidden_size, output_size) - 1

    def feedforward(self, x):
        self.z1 = sigmoid(np.dot(x, self.w1))
        self.z2 = sigmoid(np.dot(self.z1, self.w2))
        return self.z2

    def backprop(self, x, y):
        output_error = y - self.z2
        delta2 = output_error * sigmoid_deriv(self.z2)
        delta1 = delta2.dot(self.w2.T) * sigmoid_deriv(self.z1)
        self.w2 += LEARNING_RATE * np.outer(self.z1, delta2)
        self.w1 += LEARNING_RATE * np.outer(x, delta1)
        return np.mean(np.abs(output_error))

    def predict(self, x):
        return np.argmax(self.feedforward(x))
        
def main():
    folder = "../../train"
    files = [f for f in os.listdir(folder) if f.endswith(".png")]
    label_map = get_label_map(files)
    x_data, y_data = [], []
    
    for f in files:
        img = Image.open(os.path.join(folder, f)).convert('L')
        feat = extract_features(img)
        x_data.append(feat)
        label = os.path.splitext(f)[0]
        y_data.append(one_hot(label_map[label], len(label_map)))
    
    x = np.array(x_data)
    y = np.array(y_data)
    
    nn = NeuralNetwork(input_size=x.shape[1], hidden_size=16, output_size=len(label_map))
    
    start = time.time()
    for i in range(MAX_ITER):
        total_error = 0
        for xi, yi in zip(x, y):
            nn.feedforward(xi)
            total_error += nn.backprop(xi, yi)
        if i % 100 == 0:
            print(f"Iter {i} | Error: {total_error/len(x):.5f}")
        if total_error / len(x) < TARGET_ERROR:
            break
    print(f"Training complete in {int(time.time() - start)}s")
    
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump({
            'w1': nn.w1,
            'w2': nn.w2,
            'label_map': label_map
        }, f)
    
    print("Model saved.")


