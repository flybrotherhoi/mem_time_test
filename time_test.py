import glob
import os
import tqdm.auto as tqdm
import time

data_path = glob.glob('./data_time_test/*.xyz')

cmd = '''python -u ./main.py \
--pc {data} \
--export_dir {output_dir} \
'''


time_list = {}
for d in tqdm.tqdm(data_path[:]):
    model_name = d.split('/')[-1].split('.')[:-1]
    model_name = '.'.join(model_name)
    start = time.time()
    os.system(cmd.format(data=d, output_dir='./output/result_time_test/'+model_name))
    end = time.time()
    time_list[os.path.basename(d)] = end - start

with open('time_list.txt', 'w') as f:
    for k, v in time_list.items():
        f.write('{} {}\n'.format(k, v))