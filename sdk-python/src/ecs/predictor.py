# coding=utf-8
import math
import time
import random
from copy import copy
from datetime import datetime

TIME_START = time.time()
TIME_LIMIT = 59
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TABLE_FLAVOR = {
    'flavor1': [1.0, 1.0],
    'flavor2': [1.0, 2.0],
    'flavor3': [1.0, 4.0],
    'flavor4': [2.0, 2.0],
    'flavor5': [2.0, 4.0],
    'flavor6': [2.0, 8.0],
    'flavor7': [4.0, 4.0],
    'flavor8': [4.0, 8.0],
    'flavor9': [4.0, 16.0],
    'flavor10': [8.0, 8.0],
    'flavor11': [8.0, 16.0],
    'flavor12': [8.0, 32.0],
    'flavor13': [16.0, 16.0],
    'flavor14': [16.0, 32.0],
    'flavor15': [16.0, 64.0]
}


class Server(object):
    def __init__(self, name):
        self.name = name
        self.cpu = 56.0
        self.mem = 128.0


class Node(object):
    def __init__(self, name, cpu, mem):
        self.name = name
        self.cpu = cpu
        self.mem = mem


def SAA(data, key):
    T = 10
    T_min = 1
    r = 0.9999
    nodes_min = list()
    for i in range(len(data)):
        while data[i]:
            name = 'flavor' + str(i + 1)
            nodes_min.append(
                Node(name, TABLE_FLAVOR[name][0], TABLE_FLAVOR[name][1]))
            data[i] -= 1
    servers_num_min = len(nodes_min) + 1
    dice = list()
    for i in range(len(nodes_min)):
        dice.append(i)
    info_min = list()
    num_min = len(nodes_min) + 1
    while T > T_min:
        info = [dict()]
        random.shuffle(dice)
        nodes = copy(nodes_min)
        nodes[dice[0]], nodes[dice[1]] = nodes[dice[1]], nodes[dice[0]]
        num = 1
        server = Server(num)
        servers = [server]
        for node in nodes:
            i = 0
            while i < len(servers):
                if servers[i].cpu >= node.cpu and servers[i].mem >= node.mem:
                    servers[i].cpu -= node.cpu
                    servers[i].mem -= node.mem
                    if node.name not in info[i]:
                        info[i][node.name] = 0
                    info[i][node.name] += 1
                    break
                i += 1
            if i == len(servers):
                num += 1
                server = Server(num)
                server.cpu -= node.cpu
                server.mem -= node.mem
                servers.append(server)
                info.append(dict())
                if node.name not in info[i]:
                    info[i][node.name] = 0
                info[i][node.name] += 1
        servers_num = 0
        if key == 'CPU':
            servers_num = len(servers) - servers[len(servers) - 1].cpu / 56
        else:
            servers_num = len(servers) - servers[len(servers) - 1].mem / 128
        if servers_num < servers_num_min or \
            math.exp((servers_num_min - servers_num) / T) > random.uniform(0, 100) / 100:
            servers_num_min = servers_num
            nodes_min = nodes
            info_min = info
            num_min = num
        T = r * T
        if time.time() - TIME_START > TIME_LIMIT:
            break
    result = [num_min]
    for i in range(len(info_min)):
        line = str(i + 1)
        for name in info_min[i]:
            line += ' {} {}'.format(name, info_min[i][name])
        result.append(line)
    return result


def count_nodes(nodes_train, node_name):
    nums = [0]
    last = nodes_train[0][1]
    for name, date in nodes_train:
        if date != last:
            last = date
            nums.append(0)
        if name == node_name:
            nums[-1] += 1
    return nums


def predict_nodes(nums, key):
    n = len(nums)
    a = nums[-7] if n > 7 else 0
    b = nums[-14] if n > 14 else 0
    c = nums[-21] if n > 21 else 0
    d = nums[-28] if n > 28 else 0
    if key == 'CPU':
        p = a * 0.89 + b * 0.26 + c * 0.155 + d * 0.21
    else:
        p = a * 0.91 + b * 0.18 + c * 0.15 + d * 0.2
    return round(p)


def predict_vm(ecs_lines, input_lines):
    result = list()
    if ecs_lines is None:
        print 'ecs information is none'
        return result
    if input_lines is None:
        print 'input file information is none'
        return result
    nodes_input = list()
    i = 3
    while i < len(input_lines):
        input_lines[i] = input_lines[i].split()
        if len(input_lines[i]) < 3:
            break
        k = input_lines[i][0].split('r')[1]
        nodes_input.append(k)
        i += 1
    key = input_lines[i + 1].strip()
    time_begin = datetime.strptime(input_lines[i + 3].strip(), TIME_FORMAT)
    time_end = datetime.strptime(input_lines[i + 4].strip(), TIME_FORMAT)
    time_delta = (time_end - time_begin).days
    nodes_train = list()
    for line in ecs_lines:
        line = line.split()
        if len(line) < 4:
            continue
        nodes_train.append((line[1].split('r')[1], line[2]))
    result_list = list()
    for i in nodes_input:
        nums = count_nodes(nodes_train, i)
        nums_mean = sum(nums) / float(len(nums))
        for k in range(len(nums)):
            if nums[k] - nums_mean > 25:
                nums[k] *= 0.51
        s = 0
        for k in range(time_delta):
            n = predict_nodes(nums, key)
            s += n
            nums.append(n)
        result_list.append(int(s))
    data = [0 for i in range(15)]
    for i, node in enumerate(nodes_input):
        data[int(node) - 1] = result_list[i]
    result.append(sum(data))
    for node in nodes_input:
        result.append('flavor' + node + ' ' + str(data[int(node) - 1]))
    result.append('')
    result += SAA(data, key)
    return result
