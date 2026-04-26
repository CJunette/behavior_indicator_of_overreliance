import json
import multiprocessing
import os
import pickle
import time

import pandas as pd
import torch

import configs
import random


# def read_tensor_single(file_path):
#     print("start loading")
#     tensor_list = []
#     for tensor_index in range(len(file_path)):
#         print(f"loading {file_path[tensor_index]}")
#         tensor = torch.load(file_path[tensor_index])
#         tensor_list.append(tensor)
#     return tensor_list


def read_tensor_single(file_path):
    # while not file_path_queue.empty():
    #     with lock:  # 确保队列操作的原子性
    #         if file_path_queue.empty():  # 双重检查
    #             break
    #         file_path = file_path_queue.get()  # 从队列中读取数据
    #     print(f"start loading {file_path}")
    #
    #     # tensor = torch.load(file_path)
    #     with open(file_path, "rb") as file:
    #         data = pickle.load(file)
    #
    #     result_list_1 = []
    #     start_index_list_1 = []
    #
    #     for tensor_index in range(len(data)):
    #         start_index = data[tensor_index][0]
    #         tensor = torch.tensor(data[tensor_index][1], dtype=torch.float32)
    #         start_index_list_1.append(start_index)
    #         result_list_1.append(tensor)
    #
    #     # 保存处理结果
    #     with lock:  # 确保写入结果时的安全性
    #         result_list.append(result_list_1)
    #         start_index_list.append(start_index_list_1)

    print(f"start loading {file_path}")
    with open(file_path, "rb") as file:
        data = pickle.load(file)

    result_list = []
    start_index_list = []
    for tensor_index in range(len(data)):
        start_index = data[tensor_index][0]
        tensor = torch.tensor(data[tensor_index][1], dtype=torch.float32)
        start_index_list.append(start_index)
        result_list.append(tensor)

    return [result_list, start_index_list]




def read_tensor(file_path):
    # # 以下为单进程读取。
    # tensor_list_1 = []
    # file_list = os.listdir(file_path)
    # for file_index in range(len(file_list)):
    #     print(f"loading {file_path}/{file_list[file_index]}")
    #     tensor_list_2 = []
    #     tensor_file_list = os.listdir(f"{file_path}/{file_list[file_index]}")
    #     for tensor_index in range(len(tensor_file_list)):
    #         # print(f"loading {file_path}/{file_list[file_index]}/{tensor_file_list[tensor_index]}")
    #         tensor = torch.load(f"{file_path}/{file_list[file_index]}/{tensor_file_list[tensor_index]}")
    #         tensor_list_2.append(tensor)
    #     tensor_list_1.append(tensor_list_2)
    # return tensor_list_1

    # 这里不做任何读取，因为单进程读取速度太慢，多进程又容易出现内存问题。
    tensor_path_list = []
    file_list = os.listdir(file_path)
    for file_index in range(len(file_list)):
        tensor_path_list_1 = []
        tensor_file_list = os.listdir(f"{file_path}/{file_list[file_index]}")
        tensor_file_list.sort()
        for tensor_index in range(len(tensor_file_list)):
            tensor_path_list_1.append(f"{file_path}/{file_list[file_index]}/{tensor_file_list[tensor_index]}")
        tensor_path_list.append(tensor_path_list_1)

    return


def read_tensor_in_batch():
    gpt_tensor_list = []
    tasksheet_tensor_list = []
    task_file_path = os.listdir(f'{configs.data_prefix}data')
    for task_index in range(len(task_file_path)):
        gpt_tensor_list_1 = read_tensor(f"{configs.data_prefix}data/{task_file_path[task_index]}/gpt_tensor_data")
        tasksheet_tensor_list_1 = read_tensor(f"{configs.data_prefix}data/{task_file_path[task_index]}/tasksheet_tensor_data")
        gpt_tensor_list.append(gpt_tensor_list_1)
        tasksheet_tensor_list.append(tasksheet_tensor_list_1)
    return gpt_tensor_list, tasksheet_tensor_list


def read_certain_page_tensor_in_batch(page_type):
    task_file_path = os.listdir(f'{configs.data_prefix}data')
    task_file_path.sort()
    file_path_queue = multiprocessing.Queue()
    # file_num_list = []
    subject_name_list = []
    file_path_list = []

    for task_index in range(len(task_file_path)):
        file_list = os.listdir(f"{configs.data_prefix}data/{task_file_path[task_index]}/{page_type}_tensor_data-window_{configs.split_window}-stride_{configs.split_stride}")
        file_list.sort()
        subject_name_list_1 = []
        file_path_list_1 = []
        for file_index in range(len(file_list)):
            file_path_queue.put(f"{configs.data_prefix}data/{task_file_path[task_index]}/{page_type}_tensor_data-window_{configs.split_window}-stride_{configs.split_stride}/{file_list[file_index]}")
            file_path_list_1.append(f"{configs.data_prefix}data/{task_file_path[task_index]}/{page_type}_tensor_data-window_{configs.split_window}-stride_{configs.split_stride}/{file_list[file_index]}")
            subject_name_list_1.append(file_list[file_index].split(".")[0])
        file_path_list.append(file_path_list_1)
        subject_name_list.append(subject_name_list_1)

    results = []
    for task_index in range(len(file_path_list)):
        results_1 = []
        for file_index in range(len(file_path_list[task_index])):
            results_1.append(read_tensor_single(file_path_list[task_index][file_index]))
        results.append(results_1)

    result_list = []
    start_index_list = []
    for task_index in range(len(results)):
        result_list_1 = []
        start_index_list_1 = []
        for file_num_index in range(len(results[task_index])):
            result_list_1.append(results[task_index][file_num_index][0])
            start_index_list_1.append(results[task_index][file_num_index][1])
        result_list.append(result_list_1)
        start_index_list.append(start_index_list_1)

    return result_list, start_index_list, subject_name_list


def flatten_raw_data_list(raw_data_list, start_index_list, subject_name_list, score_list):
    data_list_1d = []
    label_list_1d = []
    score_list_1d = []
    for task_index in range(len(raw_data_list)):
        for subject_index in range(len(raw_data_list[task_index])):
            subject_name = subject_name_list[task_index][subject_index]
            score = score_list[task_index][subject_index]
            for tensor_index in range(len(raw_data_list[task_index][subject_index])):
                start_index = start_index_list[task_index][subject_index][tensor_index]
                data_list_1d.append(raw_data_list[task_index][subject_index][tensor_index])
                label_list_1d.append(f"{configs.model_task_corresponding_dict[configs.model_index][task_index]}_{subject_name}_{start_index}")
                score_list_1d.append(score)
    return data_list_1d, label_list_1d, score_list_1d


def read_raw_data(task, page, index_list):
    data_list = []
    for file_name in index_list:
        print(file_name)
        with open(f"{configs.data_prefix}data/{task}/{page}/{file_name}.json", encoding="utf-8") as file:
            data = json.load(file)
        data_list.append(data)
    return data_list


def read_gpt_and_tasksheet(task):
    gpt_file_list = os.listdir(f"{configs.data_prefix}data/{task}/gpt_rawdata")
    tasksheet_file_list = os.listdir(f"{configs.data_prefix}data/{task}/tasksheet_rawdata")
    gpt_file_list = [file.split(".")[0] for file in gpt_file_list]
    tasksheet_file_list = [file.split(".")[0] for file in tasksheet_file_list]

    intersection = set(gpt_file_list).intersection(set(tasksheet_file_list))
    intersection = list(intersection)
    intersection.sort()

    gpt_raw_data_list = read_raw_data(task, "gpt_rawdata", intersection)
    tasksheet_raw_data_list = read_raw_data(task, "tasksheet_rawdata", intersection)

    return gpt_raw_data_list, tasksheet_raw_data_list, intersection


def read_raw_data_in_batch():
    task_1_gpt, task_1_tasksheet, task_1_intersection = read_gpt_and_tasksheet("task_1")
    task_2_gpt, task_2_tasksheet, task_2_intersection = read_gpt_and_tasksheet("task_2")
    task_3_gpt, task_3_tasksheet, task_3_intersection = read_gpt_and_tasksheet("task_3")

    gpt_raw_data_list = [task_1_gpt, task_2_gpt, task_3_gpt]
    tasksheet_raw_data_list = [task_1_tasksheet, task_2_tasksheet, task_3_tasksheet]
    intersection_list = [task_1_intersection, task_2_intersection, task_3_intersection]

    return gpt_raw_data_list, tasksheet_raw_data_list, intersection_list


def read_processed_data(page_type):
    task_list = os.listdir(f"{configs.data_prefix}data")
    task_list.sort()

    raw_data_list = []

    for task_index in range(len(task_list)):
        raw_data_list_1 = []
        file_list = os.listdir(f"{configs.data_prefix}data/{task_list[task_index]}/{page_type}_data")
        file_list.sort()
        for file_index in range(len(file_list)):
            with open(f"{configs.data_prefix}data/{task_list[task_index]}/{page_type}_data/{file_list[file_index]}", encoding="utf-8") as f:
                json_file = json.load(f)
                raw_data_list_1.append(json_file)
        raw_data_list.append(raw_data_list_1)

    return raw_data_list


def read_score(task_type, intersection_list_1):
    score_file_path = f"{configs.data_prefix}data/{task_type}/score/score-{task_type}.csv"
    df_score = pd.read_csv(score_file_path)
    score_list = []

    for index in range(len(intersection_list_1)):
        try:
            score = df_score[df_score["index"] == int(intersection_list_1[index])].iloc[0]["score"]
            score_list.append(score)
        except:
            print(f"Error score missing: {task_type} {intersection_list_1[index]}")

    min_value = min(score_list)
    max_value = max(score_list)
    # score_list_normalized = [(score - min_value) / (max_value - min_value) + float(task_type.split("_")[1]) for score in score_list]
    score_list_normalized = [(score - min_value) / (max_value - min_value) for score in score_list]

    return score_list_normalized


def read_score_in_batch(intersection_list):
    score_task_1 = read_score("task_1", intersection_list[0])
    score_task_2 = read_score("task_2", intersection_list[1])
    score_task_3 = read_score("task_3", intersection_list[2])
    score_list = [score_task_1, score_task_2, score_task_3]

    return score_list


def read_intermediate_feature_and_score():
    feature_file_path = f"{configs.data_prefix}intermediate_data/combined_feature_and_score/feature_{configs.split_window}_{configs.split_stride}_{configs.model_index}.json"
    cluster_file_path = f"{configs.data_prefix}intermediate_data/combined_feature_and_score/cluster_{configs.split_window}_{configs.split_stride}_{configs.model_index}.json"
    score_file_path = f"{configs.data_prefix}intermediate_data/combined_feature_and_score/score_{configs.split_window}_{configs.split_stride}_{configs.model_index}.json"

    with open(feature_file_path, "r") as file:
        feature_data = json.load(file)
    with open(cluster_file_path, "r") as file:
        cluster_data = json.load(file)
    with open(score_file_path, "r") as file:
        score_data = json.load(file)

    gpt_stay_duration_list = feature_data["gpt_stay_duration"]
    tasksheet_stay_duration_list = feature_data["tasksheet_stay_duration"]
    switch_list = feature_data["switch_count"]
    length_list = feature_data["sequence_length"]
    action_frequency_dict_new = feature_data["action_frequency"]
    combined_attribute_dict = feature_data["attribute_mean"]

    gpt_stay_duration_score_list = score_data["gpt_stay_duration"]
    tasksheet_stay_duration_score_list = score_data["tasksheet_stay_duration"]
    switch_score_list = score_data["switch_count"]
    length_score_list = score_data["sequence_length"]
    action_frequency_score_dict = score_data["action_frequency"]
    combined_attribute_score_dict = score_data["attribute_mean"]

    gpt_duration_cluster_list = cluster_data["gpt_stay_duration"]
    tasksheet_duration_cluster_list = cluster_data["tasksheet_stay_duration"]
    switch_cluster_list = cluster_data["switch_count"]
    length_cluster_list = cluster_data["sequence_length"]
    action_frequency_cluster_dict = cluster_data["action_frequency"]
    combined_attribute_cluster_dict = cluster_data["attribute_mean"]

    return (gpt_stay_duration_list, tasksheet_stay_duration_list, switch_list, length_list, action_frequency_dict_new, combined_attribute_dict,
            gpt_stay_duration_score_list, tasksheet_stay_duration_score_list, switch_score_list, length_score_list, action_frequency_score_dict, combined_attribute_score_dict,
            gpt_duration_cluster_list, tasksheet_duration_cluster_list, switch_cluster_list, length_cluster_list, action_frequency_cluster_dict, combined_attribute_cluster_dict)


def prepare_data_given_model_index(page_type):
    torch.manual_seed(configs.seed)
    random.seed(configs.seed)
    torch.manual_seed(configs.seed)

    _, _, intersection_list = read_raw_data_in_batch()
    score_list = read_score_in_batch(intersection_list)
    tensor_list, start_index_list, subject_name_list = read_certain_page_tensor_in_batch(page_type)

    new_intersection_list = []
    new_score_list = []
    new_tensor_list = []
    new_start_index_list = []
    new_subject_name_list = []
    for i in range(len(configs.model_task_corresponding_dict[configs.model_index])):
        task_index = configs.model_task_corresponding_dict[configs.model_index][i]
        new_intersection_list.append(intersection_list[task_index])
        new_score_list.append(score_list[task_index])
        new_tensor_list.append(tensor_list[task_index])
        new_start_index_list.append(start_index_list[task_index])
        new_subject_name_list.append(subject_name_list[task_index])
    intersection_list = new_intersection_list
    score_list = new_score_list
    tensor_list = new_tensor_list
    start_index_list = new_start_index_list
    subject_name_list = new_subject_name_list

    return intersection_list, score_list, tensor_list, start_index_list, subject_name_list


def read_data_after_cluster():
    file_path = f"{configs.data_prefix}intermediate_data/data_after_cluster/data_after_cluster_{configs.split_window}_{configs.split_stride}_{configs.model_index}.pkl"
    with open(file_path, "rb") as file:
        data = pickle.load(file)

        combined_labels = data["combined_labels"]
        combined_label_count_dict = data["combined_label_count_dict"]
        combined_data_dict = data["combined_data_dict"]
        evaluation_score = data["evaluation_score"]
        attribute_dict = data["attribute_dict"]
        attribute_mean_dict = data["attribute_mean_dict"]
        attribute_flatten_dict = data["attribute_flatten_dict"]
        sequence_length_dict = data["sequence_length_dict"]
        task_dict = data["task_dict"]
        subject_index_dict = data["subject_index_dict"]
        action_count_dict = data["action_count_dict"]
        action_frequency_dict = data["action_frequency_dict"]

    return combined_labels, combined_label_count_dict, combined_data_dict, evaluation_score, attribute_dict, attribute_mean_dict, attribute_flatten_dict, sequence_length_dict, task_dict, subject_index_dict, action_count_dict, action_frequency_dict


def read_cluster_filtering_result(model_index_list):
    data_dict = {}
    file_prefix = f"{configs.data_prefix}output/overreliance_score_prediction"
    for model_index in model_index_list:
        file_path = f"{file_prefix}/criteria-model_{model_index}.pkl"
        with open(file_path, "rb") as file:
            data = pickle.load(file)
            data_dict[model_index] = data
    return data_dict
