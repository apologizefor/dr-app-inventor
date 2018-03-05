import os
import sys
import csv
import appInstructor as AI

sys.setrecursionlimit(2048)
dirs_aia = '../../../AI_files/proj'
# dirs_aia = '../../../AI_files/prueba'

dirs_list = os.listdir(dirs_aia)
aia_files = []

for f in dirs_list:
    if f.split('.')[-1] == 'aia':
        aia_files.append(f)

results = []
blocks = []

for aia in aia_files:
    total = 0
    data, bl = AI.extract_data('admin', aia)
    if data != 0:
        for key in data:
            total += data[key]
        data['total'] = total
        data['name'] = aia[:-4]
        results.append(data)
    if bl != 0:
        bl['name'] = aia[:-4]
        blocks.append(bl)

with open('results.csv', 'w') as csvfile:
    # fieldnames = results[0].keys()
    fieldnames = ['name', 'scr', 'naming', 'conditional', 'events', 'loop', 'proc',
            'lists', 'dp', 'sensors', 'media', 'social', 'connect', 'draw',
            'operator', 'ui', 'total']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for aia in results:
        writer.writerow(aia)

def block_types(d, types):
    for key in d.keys():
        if key not in types:
            types.append(key)
    return types

with open('blocks.csv', 'wb') as csvfile:
    fieldnames = ['name', 'number']
    for aia in blocks:
        fieldnames = block_types(aia, fieldnames)
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval=0)
    writer.writeheader()
    for aia in blocks:
        writer.writerow(aia)
