import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from weights_downloader import WeightsDownloader

def download_weight_files(weight_files):
    wd = WeightsDownloader()
    for weight_file in weight_files:
        wd.download_weights(weight_file)

def main(filenames):
    weight_files = []
    for filename in filenames:
        if filename.endswith('.txt'):
            with open(filename, 'r') as f:
                weight_files.extend(f.read().splitlines())
        else:
            weight_files.append(filename)
    download_weight_files(weight_files)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_weights.py <filename> [<filename> ...] or python get_weights.py <weights.txt>")
        sys.exit(1)
    filenames = sys.argv[1:]
    main(filenames)
