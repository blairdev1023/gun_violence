import os
import pandas as pd

def assembler(path_to_data):
    filenames = [e for e in os.listdir(path_to_data) if e[-3:] == 'csv']
    df = pd.read_csv(path_to_data + filenames.pop())
    for filename in filenames:
        df = pd.concat([df, pd.read_csv(path_to_data + filename)])
    return df

if __name__ == '__main__':
    path_to_data = '../data/known_ids/'
    df = assembler(path_to_data)
