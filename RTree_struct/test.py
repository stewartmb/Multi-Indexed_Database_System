import RTreeFile_Final as index
import os
import csv

table_format = {"zip_code": "i", "latitude": "d", "longitude": "d", "city": "20s", "state": "2s", "county": "20s"}
keys = ["latitude","longitude"]

def test_import_csv(csv_path, index_file = "info/index.bin", data_file = "info/data.bin"):
    try:
        os.remove(index_file)
        os.remove(data_file)
    except FileNotFoundError:
        pass

    rtree = index.RTreeFile(table_format, keys)
    with open(csv_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            rtree.insert(row)     
            pri