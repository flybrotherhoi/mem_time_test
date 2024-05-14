import os
import glob
import tqdm
import time

import subprocess
import psutil
import GPUtil

def get_process_memory_usage(process):
    try:
        # 获取进程的峰值内存使用量（RSS）
        memory_info = process.memory_info()
        peak_memory = memory_info.rss
        return peak_memory
    except psutil.NoSuchProcess as e:
        print(f"Error: {e}")
        return 0

def get_GPU_memory_usage():
    GPUs = GPUtil.getGPUs()
    gpu = GPUs[0]
    return gpu.memoryUsed

def run_command_with_memory_tracking(cmd, show_output=False):
    if show_output:
        process = subprocess.Popen(cmd, shell=True)
    else:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    peak_CPU_mem = 0
    peak_GPU_mem = 0
    initial_GPU_memory = get_GPU_memory_usage()
    try:
        while process.poll() is None:
            memory_info = psutil.Process(process.pid).memory_full_info()
            
            process_tree = psutil.Process(process.pid).children(recursive=True)
            # print(process.pid)
            # print(process_tree)
            # 计算所有进程及其子进程的峰值内存之和
            total_memory_usage = memory_info.rss + sum(get_process_memory_usage(proc) for proc in process_tree)
            # print(len(process_tree))
            
            if total_memory_usage > peak_CPU_mem:
                peak_CPU_mem = total_memory_usage
            peak_GPU_mem = max(peak_GPU_mem, get_GPU_memory_usage() - initial_GPU_memory)
            
            psutil.cpu_percent(interval=0.1)  # 等待1秒钟，可以根据需要调整
            
    finally:
        process.terminate()
        process.wait()

    return peak_CPU_mem, peak_GPU_mem

data_path = glob.glob('./data_time_test/*.xyz')

cmd = '''python -u ./main.py \
--pc {data} \
--export_dir {output_dir}'''


mem_list = {}
for d in tqdm.tqdm(data_path[:]):
    model_name = d.split('/')[-1].split('.')[:-1]
    model_name = '.'.join(model_name)
    ram,vram = run_command_with_memory_tracking(cmd.format(data=d, output_dir='./output/result_time_test/'+model_name),show_output=False)
    mem_list[os.path.basename(d)] = {}
    mem_list[os.path.basename(d)]['ram'] = ram
    mem_list[os.path.basename(d)]['vram'] = vram
    print('{} {} {}'.format(model_name, ram, vram))

with open('memory_list.txt', 'w') as f:
    for k, v in mem_list.items():
        f.write('{} {} {}\n'.format(k, v['ram'], v['vram']))