import json
import os
import pickle
import warnings
from datetime import datetime

import numpy as np
from dateutil import parser

import torch

import configs
from ReadData import read_raw_data_in_batch, read_processed_data


# 将这几个read函数都放到ReadData下。

# def read_raw_data(task, page, index_list):
#     data_list = []
#     for file_name in index_list:
#         print(file_name)
#         with open(f"data/{task}/{page}/{file_name}.json", encoding="utf-8") as file:
#             data = json.load(file)
#         data_list.append(data)
#     return data_list


# def read_gpt_and_tasksheet(task):
#     gpt_file_list = os.listdir(f"data/{task}/gpt_rawdata")
#     tasksheet_file_list = os.listdir(f"data/{task}/tasksheet_rawdata")
#     gpt_file_list = [file.split(".")[0] for file in gpt_file_list]
#     tasksheet_file_list = [file.split(".")[0] for file in tasksheet_file_list]
#
#     intersection = set(gpt_file_list).intersection(set(tasksheet_file_list))
#     intersection = list(intersection)
#     intersection.sort()
#
#     gpt_raw_data_list = read_raw_data(task, "gpt_rawdata", intersection)
#     tasksheet_raw_data_list = read_raw_data(task, "tasksheet_rawdata", intersection)
#
#     return gpt_raw_data_list, tasksheet_raw_data_list, intersection
#
#
# def read_raw_data_in_batch():
#     task_1_gpt, task_1_tasksheet, task_1_intersection = read_gpt_and_tasksheet("task_1")
#     task_2_gpt, task_2_tasksheet, task_2_intersection = read_gpt_and_tasksheet("task_2")
#     task_3_gpt, task_3_tasksheet, task_3_intersection = read_gpt_and_tasksheet("task_3")
#
#     gpt_raw_data_list = [task_1_gpt, task_2_gpt, task_3_gpt]
#     tasksheet_raw_data_list = [task_1_tasksheet, task_2_tasksheet, task_3_tasksheet]
#     intersection_list = [task_1_intersection, task_2_intersection, task_3_intersection]
#
#     return gpt_raw_data_list, tasksheet_raw_data_list, intersection_list


# def read_processed_data(page_type):
#     task_list = os.listdir("data")
#     task_list.sort()
#
#     raw_data_list = []
#
#     for task_index in range(len(task_list)):
#         raw_data_list_1 = []
#         file_list = os.listdir(f"data/{task_list[task_index]}/{page_type}_data")
#         file_list.sort()
#         for file_index in range(len(file_list)):
#             with open(f"data/{task_list[task_index]}/{page_type}_data/{file_list[file_index]}", encoding="utf-8") as f:
#                 json_file = json.load(f)
#                 raw_data_list_1.append(json_file)
#         raw_data_list.append(raw_data_list_1)
#
#     return raw_data_list


def get_all_action_type(raw_data_list):
    action_type_dict = {}
    for task_index in range(len(raw_data_list)):
        for file_index in range(len(raw_data_list[task_index])):
            for log_index in range(len(raw_data_list[task_index][file_index])):
                action_type = raw_data_list[task_index][file_index][log_index]["type"]
                if action_type not in action_type_dict:
                    action_type_dict[action_type] = []
                else:
                    action_type_dict[action_type].append(raw_data_list[task_index][file_index][log_index])
    return action_type_dict


# def transform_json_to_vector(raw_data_list, gpt_action_type_dict, tasksheet_action_type_dict):
#     gpt_action_type_key_set = set(gpt_action_type_dict.keys())
#     tasksheet_action_type_key_set = set(tasksheet_action_type_dict.keys())
#     action_type_key_set = gpt_action_type_key_set.union(tasksheet_action_type_key_set)
#     # drop "firstNotNull" and "messageInterval"
#     action_type_key_set.remove("firstNotNull")
#     action_type_key_set.remove("messageInterval")
#
#     # turn action_type_key_set to dict
#     action_type_key_dict = {}
#     for index, action_type in enumerate(action_type_key_set):
#         action_type_key_dict[action_type] = index
#
#     print(action_type_key_dict)
#
#     vector_list = []
#     timestamp_second_list = []
#
#     for file_index in range(len(raw_data_list)):
#         vector_list_1 = []
#         timestamp_second_list_1 = []
#         for log_index in range(len(raw_data_list[file_index])):
#             current_data = raw_data_list[file_index][log_index]
#             data_type = current_data["type"]
#             if data_type == "firstNotNull" or data_type == "messageInterval":
#                 continue
#
#             data_vector = [-1] * 17
#             relative_time = current_data["relative_time"]
#             data_vector[0] = action_type_key_dict[data_type]
#             data_vector[1] = relative_time
#
#             timestamp_second = current_data["timestamp_second"]
#
#             if data_type == "mouseMovement":
#                 duration = current_data["duration"]
#                 totalMouseMovement = current_data["totalMouseMovement"]
#                 data_vector[2] = duration
#                 data_vector[7] = totalMouseMovement
#
#             if data_type == "mousewheel":
#                 duration = current_data["duration"]
#                 deltaY = current_data["deltaY"]
#                 yDirection = current_data["yDirection"]
#                 data_vector[3] = duration
#                 data_vector[8] = deltaY
#                 data_vector[9] = yDirection
#
#             if data_type == "idle":
#                 duration = current_data["duration"]
#                 data_vector[4] = duration
#
#             if data_type == "scroll":
#                 deltaY = current_data["deltaY"]
#                 yDirection = current_data["yDirection"]
#                 data_vector[10] = deltaY
#                 data_vector[11] = yDirection
#
#             if data_type == "keypress":
#                 duration = current_data["duration"]
#                 key_count = current_data["key_count"]
#                 data_vector[5] = duration
#                 data_vector[12] = key_count
#
#             if data_type == "deleteAction":
#                 duration = current_data["duration"]
#                 key_count = current_data["key_count"]
#                 data_vector[6] = duration
#                 data_vector[13] = key_count
#
#             if data_type == "copy":
#                 textLength = current_data["textLength"]
#                 data_vector[14] = textLength
#
#             if data_type == "paste":
#                 textLength = current_data["textLength"]
#                 data_vector[15] = textLength
#
#             if data_type == "highlight":
#                 highlightedTextLength = current_data["highlightedTextLength"]
#                 data_vector[16] = highlightedTextLength
#
#             vector_list_1.append(data_vector)
#             timestamp_second_list_1.append(timestamp_second)
#         vector_list.append(vector_list_1)
#         timestamp_second_list.append(timestamp_second_list_1)
#     return vector_list, timestamp_second_list


def transform_json_to_vector(raw_data_list, gpt_action_type_dict, tasksheet_action_type_dict):
    # gpt_action_type_key_set = set(gpt_action_type_dict.keys())
    # tasksheet_action_type_key_set = set(tasksheet_action_type_dict.keys())
    # action_type_key_set = gpt_action_type_key_set.union(tasksheet_action_type_key_set)
    # # drop "firstNotNull" and "messageInterval"
    # action_type_key_set.remove("firstNotNull")
    # action_type_key_set.remove("messageInterval")
    #
    # # turn action_type_key_set to dict
    # action_type_key_dict = {}
    # for index, action_type in enumerate(action_type_key_set):
    #     action_type_key_dict[action_type] = index
    #

    action_type_key_dict = configs.action_types
    print(action_type_key_dict)

    vector_list = []
    timestamp_second_list = []
    start_index_list = []

    for file_index in range(len(raw_data_list)):
        vector_list_1 = []
        timestamp_second_list_1 = []
        start_index_list_1 = []
        for log_index in range(len(raw_data_list[file_index])):
            current_data = raw_data_list[file_index][log_index]
            data_type = current_data["type"]
            page = current_data["page"]

            # if data_type == "firstNotNull" or data_type == "messageInterval":
            #     continue

            data_vector = [-1] * configs.input_dim
            relative_time = current_data["relative_time"]
            data_vector[0] = action_type_key_dict[data_type]
            data_vector[1] = relative_time

            timestamp_second = current_data["timestamp_second"]

            if data_type == "mouseMovement":
                duration = current_data["duration"]
                totalMouseMovement = current_data["totalMouseMovement"]
                data_vector[2] = duration
                data_vector[7] = totalMouseMovement

            if data_type == "mousewheel":
                duration = current_data["duration"]
                deltaY = current_data["deltaY"]
                yDirection = current_data["yDirection"]
                data_vector[3] = duration
                data_vector[8] = deltaY
                data_vector[15] = yDirection

            if data_type == "idle":
                duration = current_data["duration"]
                data_vector[4] = duration

            if data_type == "scroll":
                deltaY = current_data["deltaY"]
                yDirection = current_data["yDirection"]
                data_vector[9] = deltaY
                data_vector[16] = yDirection

            if data_type == "keypress":
                duration = current_data["duration"]
                key_count = current_data["key_count"]
                data_vector[5] = duration
                data_vector[10] = key_count

            if data_type == "deleteAction":
                duration = current_data["duration"]
                key_count = current_data["key_count"]
                data_vector[6] = duration
                data_vector[11] = key_count

            if data_type == "copy":
                textLength = current_data["textLength"]
                data_vector[12] = textLength

            if data_type == "paste":
                textLength = current_data["textLength"]
                data_vector[13] = textLength

            if data_type == "highlight":
                highlightedTextLength = current_data["highlightedTextLength"]
                data_vector[14] = highlightedTextLength

            if page == "gpt": # 参考configs.page_types
                data_vector[17] = 0
            else:
                data_vector[17] = 1

            start_index = current_data["index"]

            vector_list_1.append(data_vector)
            timestamp_second_list_1.append(timestamp_second)
            start_index_list_1.append(start_index)
        vector_list.append(vector_list_1)
        timestamp_second_list.append(timestamp_second_list_1)
        start_index_list.append(start_index_list_1)
    return vector_list, timestamp_second_list, start_index_list


# def transform_json_to_vector_in_batch(gpt_raw_data_list, tasksheet_raw_data_list, gpt_action_type_dict, tasksheet_action_type_dict):
#     gpt_vector_list = []
#     gpt_timestamp_second_list = []
#     tasksheet_vector_list = []
#     tasksheet_timestamp_second_list = []
#
#     for task_index in range(len(gpt_raw_data_list)):
#         gpt_vector_list_1, gpt_timestamp_second_list_1 = transform_json_to_vector(gpt_raw_data_list[task_index], gpt_action_type_dict, tasksheet_action_type_dict)
#         tasksheet_vector_list_1, tasksheet_timestamp_second_list_1 = transform_json_to_vector(tasksheet_raw_data_list[task_index], gpt_action_type_dict, tasksheet_action_type_dict)
#
#         gpt_vector_list.append(gpt_vector_list_1)
#         gpt_timestamp_second_list.append(gpt_timestamp_second_list_1)
#         tasksheet_vector_list.append(tasksheet_vector_list_1)
#         tasksheet_timestamp_second_list.append(tasksheet_timestamp_second_list_1)
#
#     return gpt_vector_list, gpt_timestamp_second_list, tasksheet_vector_list, tasksheet_timestamp_second_list


# def transform_json_to_vector_in_batch(gpt_raw_data_list, tasksheet_raw_data_list, gpt_action_type_dict, tasksheet_action_type_dict):
#     gpt_vector_list = []
#     gpt_timestamp_second_list = []
#     gpt_start_index_list = []
#     tasksheet_vector_list = []
#     tasksheet_timestamp_second_list = []
#     tasksheet_start_index_list = []
#
#     for task_index in range(len(gpt_raw_data_list)):
#         gpt_vector_list_1, gpt_timestamp_second_list_1, gpt_start_index_list_1 = transform_json_to_vector(gpt_raw_data_list[task_index], gpt_action_type_dict, tasksheet_action_type_dict)
#         tasksheet_vector_list_1, tasksheet_timestamp_second_list_1, tasksheet_start_index_list_1 = transform_json_to_vector(tasksheet_raw_data_list[task_index], gpt_action_type_dict, tasksheet_action_type_dict)
#
#         gpt_vector_list.append(gpt_vector_list_1)
#         gpt_timestamp_second_list.append(gpt_timestamp_second_list_1)
#         gpt_start_index_list.append(gpt_start_index_list_1)
#         tasksheet_vector_list.append(tasksheet_vector_list_1)
#         tasksheet_timestamp_second_list.append(tasksheet_timestamp_second_list_1)
#         tasksheet_start_index_list.append(tasksheet_start_index_list_1)
#
#     return gpt_vector_list, gpt_timestamp_second_list, gpt_start_index_list, tasksheet_vector_list, tasksheet_timestamp_second_list, tasksheet_start_index_list


def transform_json_to_vector_in_batch(raw_data_list):
    vector_list = []
    timestamp_second_list = []
    start_index_list = []

    for task_index in range(len(raw_data_list)):
        vector_list_1, timestamp_second_list_1, start_index_list_1 = transform_json_to_vector(raw_data_list[task_index], None, None)
        vector_list.append(vector_list_1)
        timestamp_second_list.append(timestamp_second_list_1)
        start_index_list.append(start_index_list_1)

    return vector_list, timestamp_second_list, start_index_list



# def split_vector_list_using_time(vector_list, timestamp_second_list, window, stride):
#     new_vector_list = []
#     start_index_list = []
#     for file_index in range(len(vector_list)):
#         new_vector_list_1 = []
#         start_index_list_1 = []
#         vector_list_1 = vector_list[file_index]
#         iterative_index = 0
#         while iterative_index < len(vector_list_1):
#             probe_index = iterative_index + 1
#             start_time = timestamp_second_list[file_index][iterative_index]
#
#             while probe_index < len(vector_list_1):
#                 end_time = timestamp_second_list[file_index][probe_index]
#                 if end_time - start_time < window:
#                     probe_index += 1
#                 else:
#                     break
#             new_vector_list_2 = []
#             for index in range(iterative_index, probe_index):
#                 new_vector_list_2.append(vector_list_1[index])
#             new_vector_list_1.append(new_vector_list_2)
#             start_index_list_1.append(iterative_index)
#
#             probe_index = iterative_index + 1
#             while probe_index < len(vector_list_1):
#                 if timestamp_second_list[file_index][probe_index] - start_time >= stride:
#                     break
#                 probe_index += 1
#             iterative_index = probe_index
#         new_vector_list.append(new_vector_list_1)
#         start_index_list.append(start_index_list_1)
#     return new_vector_list, start_index_list


def split_vector_list_using_time(vector_list, timestamp_second_list, raw_start_index_list, window, stride):
    new_vector_list = []
    start_index_list = []
    for file_index in range(len(vector_list)):
        new_vector_list_1 = []
        start_index_list_1 = []
        vector_list_1 = vector_list[file_index]
        iterative_index = 0
        while iterative_index < len(vector_list_1):
            probe_index = iterative_index + 1
            start_time = timestamp_second_list[file_index][iterative_index]

            while probe_index < len(vector_list_1):
                end_time = timestamp_second_list[file_index][probe_index]
                if end_time - start_time < window:
                    probe_index += 1
                else:
                    break
            new_vector_list_2 = []
            for index in range(iterative_index, probe_index):
                new_vector_list_2.append(vector_list_1[index])
            new_vector_list_1.append(new_vector_list_2)
            start_index = raw_start_index_list[file_index][iterative_index]
            start_index_list_1.append(start_index)

            probe_index = iterative_index + 1
            while probe_index < len(vector_list_1):
                if timestamp_second_list[file_index][probe_index] - start_time >= stride:
                    break
                probe_index += 1
            iterative_index = probe_index
        new_vector_list.append(new_vector_list_1)
        start_index_list.append(start_index_list_1)
    return new_vector_list, start_index_list


# def split_vector_list_using_time_in_batch():
#     gpt_split_vector_list = []
#     tasksheet_split_vector_list = []
#     gpt_start_index_list = []
#     tasksheet_start_index_list = []
#
#     window = configs.split_window
#     stride = configs.split_stride
#
#     for task_index in range(len(gpt_vector_list)):
#         gpt_split_vector_list_1, gpt_start_index_list_1 = split_vector_list_using_time(gpt_vector_list[task_index], gpt_timestamp_second_list[task_index], window, stride)
#         tasksheet_split_vector_list_1, tasksheet_start_index_list_1 = split_vector_list_using_time(tasksheet_vector_list[task_index], tasksheet_timestamp_second_list[task_index], window, stride)
#
#         gpt_split_vector_list.append(gpt_split_vector_list_1)
#         tasksheet_split_vector_list.append(tasksheet_split_vector_list_1)
#         gpt_start_index_list.append(gpt_start_index_list_1)
#         tasksheet_start_index_list.append(tasksheet_start_index_list_1)
#     return gpt_split_vector_list, tasksheet_split_vector_list, gpt_start_index_list, tasksheet_start_index_list


# def split_vector_list_using_time_in_batch(gpt_vector_list, gpt_timestamp_second_list, raw_gpt_start_index_list, tasksheet_vector_list, tasksheet_timestamp_second_list, raw_tasksheet_start_index_list):
#     gpt_split_vector_list = []
#     tasksheet_split_vector_list = []
#     gpt_start_index_list = []
#     tasksheet_start_index_list = []
#
#     window = configs.split_window
#     stride = configs.split_stride
#
#     for task_index in range(len(gpt_vector_list)):
#         gpt_split_vector_list_1, gpt_start_index_list_1 = split_vector_list_using_time(gpt_vector_list[task_index], gpt_timestamp_second_list[task_index], raw_gpt_start_index_list[task_index], window, stride)
#         tasksheet_split_vector_list_1, tasksheet_start_index_list_1 = split_vector_list_using_time(tasksheet_vector_list[task_index], tasksheet_timestamp_second_list[task_index], raw_tasksheet_start_index_list[task_index], window, stride)
#
#         gpt_split_vector_list.append(gpt_split_vector_list_1)
#         tasksheet_split_vector_list.append(tasksheet_split_vector_list_1)
#         gpt_start_index_list.append(gpt_start_index_list_1)
#         tasksheet_start_index_list.append(tasksheet_start_index_list_1)
#     return gpt_split_vector_list, tasksheet_split_vector_list, gpt_start_index_list, tasksheet_start_index_list


def split_vector_list_using_time_in_batch(vector_list, timestamp_second_list, raw_start_index_list):
    split_vector_list = []
    start_index_list = []

    window = configs.split_window
    stride = configs.split_stride

    for task_index in range(len(vector_list)):
        split_vector_list_1, start_index_list_1 = split_vector_list_using_time(vector_list[task_index], timestamp_second_list[task_index], raw_start_index_list[task_index], window, stride)
        split_vector_list.append(split_vector_list_1)
        start_index_list.append(start_index_list_1)

    return split_vector_list, start_index_list


def save_vector_list_as_tensor(split_vector_list, start_index_list, intersection, save_file_path):
    for file_index in range(len(intersection)):
        save_path_prefix = f"{save_file_path}-window_{configs.split_window}-stride_{configs.split_stride}"

        if not os.path.exists(save_path_prefix):
            os.makedirs(save_path_prefix)

        torch_file_list = []
        for split_index in range(len(split_vector_list[file_index])):
            name_index = start_index_list[file_index][split_index]
            torch_file_list.append([name_index, split_vector_list[file_index][split_index]])
        file_path = f"{save_path_prefix}/{intersection[file_index]}.pkl"
        with open(file_path, "wb") as f:
            pickle.dump(torch_file_list, f)
        print(f"saving {file_path}")


# def save_vector_list_as_tensor_in_batch(intersection_list, gpt_split_vector_list, gpt_start_index_list, tasksheet_split_vector_list, tasksheet_start_index_list):
#     for task_index in range(len(gpt_split_vector_list)):
#         save_vector_list_as_tensor(gpt_split_vector_list[task_index], gpt_start_index_list[task_index], intersection_list[task_index], f"data/task_{task_index + 1}/gpt_tensor_data")
#         save_vector_list_as_tensor(tasksheet_split_vector_list[task_index], tasksheet_start_index_list[task_index], intersection_list[task_index], f"data/task_{task_index + 1}/tasksheet_tensor_data")


def save_vector_list_as_tensor_in_batch(intersection_list, split_vector_list, start_index_list, page_type):
    for task_index in range(len(split_vector_list)):
        save_vector_list_as_tensor(split_vector_list[task_index], start_index_list[task_index], intersection_list[task_index], f"data/task_{task_index + 1}/{page_type}_tensor_data")


def combine_gpt_and_tasksheet(gpt_data_list, tasksheet_data_list):
    '''
    将gpt和tasksheet的数据合并，按照时间顺序排列。同时把时间转化为同一个格式（%Y-%m-%dT%H:%M:%S.%fZ），且都存储到timestamp中。
    :param gpt_data_list:
    :param tasksheet_data_list:
    :return:
    '''
    combined_data_list = []
    for task_index in range(len(gpt_data_list)):
        combined_data_list_1 = []
        for file_index in range(len(gpt_data_list[task_index])):
            gpt_data = gpt_data_list[task_index][file_index]
            tasksheet_data = tasksheet_data_list[task_index][file_index]
            combined_data_list_2 = []

            gpt_index = 0
            tasksheet_index = 0

            while gpt_index < len(gpt_data) and tasksheet_index < len(tasksheet_data):
                gpt_datatype = gpt_data[gpt_index]["type"]
                tasksheet_datatype = tasksheet_data[tasksheet_index]["type"]

                print(task_index, file_index, gpt_index, tasksheet_index)
                gpt_time = convert_timestamp_to_time(gpt_data, gpt_index, gpt_datatype)
                tasksheet_time = convert_timestamp_to_time(tasksheet_data, tasksheet_index, tasksheet_datatype)

                if gpt_time < tasksheet_time:
                    gpt_data[gpt_index]["page"] = "gpt"
                    combined_data_list_2.append(gpt_data[gpt_index])
                    gpt_index += 1
                else:
                    tasksheet_data[tasksheet_index]["page"] = "tasksheet"
                    combined_data_list_2.append(tasksheet_data[tasksheet_index])
                    tasksheet_index += 1

            while gpt_index < len(gpt_data):
                gpt_data[gpt_index]["page"] = "gpt"
                gpt_datatype = gpt_data[gpt_index]["type"]
                convert_timestamp_to_time(gpt_data, gpt_index, gpt_datatype)

                combined_data_list_2.append(gpt_data[gpt_index])
                gpt_index += 1

            while tasksheet_index < len(tasksheet_data):
                tasksheet_data[tasksheet_index]["page"] = "tasksheet"
                tasksheet_datatype = tasksheet_data[tasksheet_index]["type"]
                convert_timestamp_to_time(tasksheet_data, tasksheet_index, tasksheet_datatype)

                combined_data_list_2.append(tasksheet_data[tasksheet_index])
                tasksheet_index += 1

            combined_data_list_1.append(combined_data_list_2)
        combined_data_list.append(combined_data_list_1)

    return combined_data_list


def convert_timestamp_to_time(data_list, log_index, data_type):
    '''
    由于在最新的代码中，所有时间数据都在被纠正且存储在timestamp中了，因此这里直接读取data["timestamp"]即可。
    :param data_list:
    :param log_index:
    :param data_type:
    :return:
    '''

    data = data_list[log_index]
    # if data_type == "firstNotNull" or data_type == "messageInterval":
    #     if data_type == "firstNotNull":
    #         data_timestamp = data["time"]
    #     else:
    #         data_timestamp = data["startTime"]
    # else:
    #     data_timestamp = data["timestamp"]
    data_timestamp = data["timestamp"]
    try:
        data_time = parser.parse(data_timestamp)
    except ValueError:
        print(f"error: {data_timestamp}")

    formatted_timestamp = data_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ") # 将 datetime对象重新格式化为字符串
    data_time_reparse = datetime.strptime(formatted_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ") # 使用 datetime.strptime 解析格式化后的字符串
    data_list[log_index]["timestamp"] = formatted_timestamp

    return data_time_reparse


def compute_timestamp_second_and_relative_time(combined_data_list):
    second_one_half_hour = configs.second_one_half_hour

    for task_index in range(len(combined_data_list)):
        for file_index in range(len(combined_data_list[task_index])):
            start_timestamp = combined_data_list[task_index][file_index][0]["timestamp"]
            start_time = datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

            for log_index in range(len(combined_data_list[task_index][file_index])):
                current_data = combined_data_list[task_index][file_index][log_index]
                try:
                    current_timestamp = current_data["timestamp"]
                except KeyError:
                    print(task_index, file_index, log_index, current_data)
                    return
                current_time = datetime.strptime(current_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

                time_second = (current_time - start_time).total_seconds()
                relative_time = time_second / second_one_half_hour
                current_data["timestamp_second"] = time_second
                current_data["relative_time"] = relative_time * 100 # 避免相对值过小，所以扩大100倍。

    return combined_data_list


def save_combined_data_list(intersection_list, combined_data_list):
    for task_index in range(len(intersection_list)):
        if not os.path.exists(f"data/task_{task_index + 1}/combined_data"):
            os.makedirs(f"data/task_{task_index + 1}/combined_data")

        for file_index in range(len(intersection_list[task_index])):
            with open(f"data/task_{task_index + 1}/combined_data/{intersection_list[task_index][file_index]}.json", "w", encoding="utf-8") as file:
                json.dump(combined_data_list[task_index][file_index], file, ensure_ascii=False, indent=4)


def process_interval_too_long(data_list):
    # 确认前后两项的时间差不会出现过于夸张的情况。如果出现，且类型为 "firstNotNull" 或者 "messageInterval"，则删除后一项。
    for task_index in range(len(data_list)):
        for file_index in range(len(data_list[task_index])):
            log_index = 0
            while log_index < len(data_list[task_index][file_index]):
                if log_index + 1 < len(data_list[task_index][file_index]):
                    if abs(data_list[task_index][file_index][log_index + 1]["timestamp_second"] - data_list[task_index][file_index][log_index]["timestamp_second"]) > 1800:
                        data_type = data_list[task_index][file_index][log_index + 1]["type"]
                        if data_type != "firstNotNull" and data_type != "messageInterval":
                            print("excessively long interval!", task_index, file_index, log_index, data_list[task_index][file_index][log_index], data_list[task_index][file_index][log_index + 1])
                            # log_index += 1
                            # raise ValueError("interval too long")
                        # else:
                        #     del data_list[task_index][file_index][log_index + 1]
                        # continue
                log_index += 1


def remove_firstNotNull_and_messageInterval(data_list):
    for task_index in range(len(data_list)):
        for file_index in range(len(data_list[task_index])):
            log_index = 0
            while log_index < len(data_list[task_index][file_index]):
                data_type = data_list[task_index][file_index][log_index]["type"]
                if data_type == "firstNotNull" or data_type == "messageInterval":
                    del data_list[task_index][file_index][log_index]
                else:
                    log_index += 1


def combined_gpt_tasksheet_and_save():
    # 导入原始数据
    _, _, intersection_list = read_raw_data_in_batch()

    gpt_raw_data_list = read_processed_data("gpt_processed")
    tasksheet_raw_data_list = read_processed_data("tasksheet_processed")

    # 由于firstNotNull和messageInterval的时间存在巨大问题，因此直接将这两种类型的条目remove掉。
    # remove_firstNotNull_and_messageInterval(gpt_raw_data_list)
    # remove_firstNotNull_and_messageInterval(tasksheet_raw_data_list)

    # gpt_action_type_dict = get_all_action_type(gpt_raw_data_list)
    # tasksheet_action_type_dict = get_all_action_type(tasksheet_raw_data_list)

    # 将gpt与tasksheet数据进行合并（根据timestamp）；同时，将所有数据的时间戳都整合到timestamp这个key下。
    combined_data_list = combine_gpt_and_tasksheet(gpt_raw_data_list, tasksheet_raw_data_list)

    # 根据合并后的timestamp，计算timestamp_second和relative_time。
    combined_data_list = compute_timestamp_second_and_relative_time(combined_data_list)

    # 保证合并后仍然没有过于夸张的时间。
    process_interval_too_long(combined_data_list)

    # 将所有数据的index进行重新编号。
    for task_index in range(len(combined_data_list)):
        for file_index in range(len(combined_data_list[task_index])):
            for log_index in range(len(combined_data_list[task_index][file_index])):
                combined_data_list[task_index][file_index][log_index]["index"] = log_index

    # 保存结果
    save_combined_data_list(intersection_list, combined_data_list)


def preprocess_and_save_gpt_and_tasksheet():
    _, _, intersection_list = read_raw_data_in_batch()
    gpt_raw_data_list = read_processed_data("gpt_processed")
    tasksheet_raw_data_list = read_processed_data("tasksheet_processed")
    # gpt_action_type_dict = get_all_action_type(gpt_raw_data_list)
    # tasksheet_action_type_dict = get_all_action_type(tasksheet_raw_data_list)
    # gpt_vector_list, gpt_timestamp_second_list, raw_gpt_start_index_list, tasksheet_vector_list, tasksheet_timestamp_second_list, raw_tasksheet_start_index_list = transform_json_to_vector_in_batch(gpt_raw_data_list, tasksheet_raw_data_list, gpt_action_type_dict, tasksheet_action_type_dict)
    gpt_vector_list, gpt_timestamp_second_list, raw_gpt_start_index_list = transform_json_to_vector_in_batch(gpt_raw_data_list)
    tasksheet_vector_list, tasksheet_timestamp_second_list, raw_tasksheet_start_index_list = transform_json_to_vector_in_batch(tasksheet_raw_data_list)
    # gpt_split_vector_list, tasksheet_split_vector_list, gpt_start_index_list, tasksheet_start_index_list = split_vector_list_using_time_in_batch(gpt_vector_list, gpt_timestamp_second_list,
    #                                                                                                                                              raw_gpt_start_index_list, tasksheet_vector_list,
    #                                                                                                                                              tasksheet_timestamp_second_list,
    #                                                                                                                                              raw_tasksheet_start_index_list)
    gpt_split_vector_list, gpt_start_index_list = split_vector_list_using_time_in_batch(gpt_vector_list, gpt_timestamp_second_list, raw_gpt_start_index_list)
    tasksheet_split_vector_list, tasksheet_start_index_list = split_vector_list_using_time_in_batch(tasksheet_vector_list, tasksheet_timestamp_second_list, raw_tasksheet_start_index_list)
    # save_vector_list_as_tensor_in_batch(intersection_list, gpt_split_vector_list, gpt_start_index_list, tasksheet_split_vector_list, tasksheet_start_index_list)
    save_vector_list_as_tensor_in_batch(intersection_list, gpt_split_vector_list, gpt_start_index_list, "gpt")
    save_vector_list_as_tensor_in_batch(intersection_list, tasksheet_split_vector_list, tasksheet_start_index_list, "tasksheet")


def scale_data(data_list):
    for task_index in range(len(data_list)):
        for file_index in range(len(data_list[task_index])):
            for log_index in range(len(data_list[task_index][file_index])):
                try:
                    for input_index in range(1, configs.input_dim - 3): # 开头第一位是类型分类，倒数第三位是mousewheel方向，倒数第二位是scroll方向，倒数第一位是page类型。
                        data_list[task_index][file_index][log_index][input_index] = np.log(data_list[task_index][file_index][log_index][input_index] + 2) # 原来数值的大小都大于0，但用了-1作为默认值（用于表示该类别不存在此attribute值），为了避免出现0值，所以+2后再取log。所以处理后的数值应该都大于等于0。
                    for input_index in range(configs.input_dim - 3, configs.input_dim - 1): # 对于倒数第三位和倒数第二位，如果是-1，则转化为0。与上面处理中对默认项的处理保持一致。
                        if data_list[task_index][file_index][log_index][input_index] == -1:
                            data_list[task_index][file_index][log_index][input_index] = 0
                except:
                    print(task_index, file_index, log_index, data_list[task_index][file_index][log_index])
                    raise ValueError("error in scale_data")
    return data_list


def preprocess_combined_and_save_tensor():
    _, _, intersection_list = read_raw_data_in_batch()
    combined_data_list = read_processed_data("combined")
    combined_vector_list, combined_timestamp_second_list, combined_start_index_list = transform_json_to_vector_in_batch(combined_data_list)
    scale_data(combined_vector_list)
    combined_split_vector_list, combined_start_index_list = split_vector_list_using_time_in_batch(combined_vector_list, combined_timestamp_second_list, combined_start_index_list)
    save_vector_list_as_tensor_in_batch(intersection_list, combined_split_vector_list, combined_start_index_list, "combined")


if __name__ == "__main__":
    preprocess_and_save_gpt_and_tasksheet()
    combined_gpt_tasksheet_and_save()
    # warnings.simplefilter("error", RuntimeWarning)
    preprocess_combined_and_save_tensor()
    pass


