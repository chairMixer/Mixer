import scipy.io as sio
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('mat_file', type=str, help='an integer for the accumulator')
    args = parser.parse_args()
    mat_dict = sio.loadmat(args.mat_file)
    print(mat_dict)
