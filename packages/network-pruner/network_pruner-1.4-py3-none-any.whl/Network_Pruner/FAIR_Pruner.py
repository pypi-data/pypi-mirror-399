def hello():
    print('FAIR Pruner is working well.')


#############################################################
# from scipy.stats import wasserstein_distance
import torch
import itertools
import ot
import pickle
import os
import torch.nn as nn
import random
import torch.nn.functional as F
################################################################
def wasserstein_1d(x, y):
    """
    Compute 1D Wasserstein distance (Earth Mover's Distance) between x and y.
    Supports unequal lengths and GPU tensors.
    """
    # ✅ 转成 float32（或者 float64 都行）
    x = x.flatten().to(torch.float32)
    y = y.flatten().to(torch.float32)

    x = x.sort().values.to(torch.float32)
    y = y.sort().values.to(torch.float32)

    n, m = x.size(0), y.size(0)
    if n != m:
        q = torch.linspace(0, 1, steps=max(n, m), device=x.device)
        xq = torch.quantile(x, q)
        yq = torch.quantile(y, q)
        return torch.mean(torch.abs(xq - yq))
    else:
        return torch.mean(torch.abs(x - y))



def sliced_wasserstein_distance(X, Y, n_projections=128, p=1):
    """
    Approximate Sliced Wasserstein Distance between two point clouds X, Y.
    Supports unequal sample sizes and 1D fallback.
    """
    device = X.device
    X, Y = X.to(torch.float32), Y.to(torch.float32)
    D = X.shape[1]

    # 1D 特化
    if D == 1:
        return wasserstein_1d(X, Y)

    # 生成随机方向
    theta = torch.randn((D, n_projections), device=device)
    theta = F.normalize(theta, dim=0)

    proj_X = X @ theta
    proj_Y = Y @ theta

    proj_X_sorted, _ = torch.sort(proj_X, dim=0)
    proj_Y_sorted, _ = torch.sort(proj_Y, dim=0)

    #
    proj_X_sorted = proj_X_sorted.to(torch.float32)
    proj_Y_sorted = proj_Y_sorted.to(torch.float32)
    n = max(proj_X_sorted.size(0), proj_Y_sorted.size(0))
    q = torch.linspace(0, 1, n, device=device)

    #
    proj_X_q = torch.quantile(proj_X_sorted, q, dim=0)
    proj_Y_q = torch.quantile(proj_Y_sorted, q, dim=0)

    dist = torch.mean(torch.abs(proj_X_q - proj_Y_q) ** p)
    return dist ** (1.0 / p)




def get_prunedata(prune_datasetloader,batch_size,class_num,pruning_samples_num):
    #
    # prune_datasetloader : is （from torch.utils.data import DataLoader）.
    # class_num : is the number of categories in the dataset.
    # pruning_samples_num : is the upper limit of the sample size for each category used to calculate the distance.
    #
    class_data = {}
    for type in range(class_num):
        class_data[f'{type}'] = []
    n=[0]*class_num
    for inputs, targets in prune_datasetloader:
        if sum(1 for num in n if num > pruning_samples_num)==class_num:
            break
        class_idx = {}
        for type in range(class_num):
            if n[type]<=pruning_samples_num:
                class_idx[f'{type}'] = torch.where(targets == type)[0]
                class_data[f'{type}'].append(torch.index_select(inputs, 0, class_idx[f'{type}']))
                n[type]+=len(class_idx[f'{type}'])
    for type in range(class_num):
        class_data[f'{type}'] = torch.cat(class_data[f'{type}'], dim = 0)
    prune_data = {}
    for type in range(class_num):
        bnum = class_data[f'{type}'].shape[0]//batch_size
        prune_data[f'{type}']=[]
        for i in range(bnum):
            prune_data[f'{type}'].append(class_data[f'{type}'][(i * batch_size):((i + 1) * batch_size), :])
    print('The pruning data is collated')
    return prune_data


features = {}
# 定义一个钩子函数
def get_features(name):
    def hook(model, input, output):
        if  isinstance(model, nn.GRU):
            features[name] = output[0]
        else:
            features[name] = output
    return hook


# def get_Distance(model,prunedata,layer_num,device):
#     #
#     # model: is the model we want to prune.
#     # prunedata :is the output from get_prunedata.
#     # layer_num : it the aim layer we want to compute Distance.
#     # device: torch.device('cpu') or torch.device('cuda') .
#     #
#     model.to(device)
#     # 注册钩子到每一层
#     for i,(name, layer) in enumerate(model.named_modules()):
#         if i == layer_num:
#             handle = layer.register_forward_hook(get_features(f'{i}'))
#             break
# ##############################以下是收集输出########################################
#     model.eval()
#     with torch.no_grad():
#         output_res = {}
#         for type in range(len(prunedata)):
#             output_res[f'{type}'] = []
#             for num in range(len(prunedata[f'{type}'])):
#                 model(prunedata[f'{type}'][num].to(device))
#                 if features[f'{layer_num}'].dim() == 3:
#                     output_res[f'{type}'].append(features[f'{layer_num}'])
#                 else:
#                     output_res[f'{type}'].append(features[f'{layer_num}'].view(features[f'{layer_num}'].size(0), features[f'{layer_num}'].size(1), -1).contiguous())
#     #############################以下是计算距离########################################
#
#         if features[f'{layer_num}'].dim() == 4:
#             channel_num = features[f'{layer_num}'].shape[1]
#             all_distance = [0]*channel_num
#             for combo in itertools.combinations(range(len(prunedata)), 2):
#                 for channel in range(channel_num):
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res[f'{combo[0]}'])):
#                         xjbg0.append(output_res[f'{combo[0]}'][i][:,channel,:].contiguous())
#                     for i in range(len(output_res[f'{combo[1]}'])):
#                         xjbg1.append(output_res[f'{combo[1]}'][i][:,channel,:].contiguous())
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = ot.sliced.sliced_wasserstein_distance(xjbg0.cpu().detach().numpy(),
#                                                                      xjbg1.cpu().detach().numpy(),
#                                                                      n_projections =50)
#                     if distance > all_distance[channel]:
#                         all_distance[channel] = distance
#         elif features[f'{layer_num}'].dim() == 2:
#             neuron_num = features[f'{layer_num}'].shape[1]
#             all_distance = [0] *neuron_num
#             for combo in itertools.combinations(range(len(output_res)), 2):
#                 for neuron in range(neuron_num):
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res[f'{combo[0]}'])):
#                         xjbg0.append(output_res[f'{combo[0]}'][i][:,neuron,0].contiguous())
#                     for i in range(len(output_res[f'{combo[1]}'])):
#                         xjbg1.append(output_res[f'{combo[1]}'][i][:,neuron, 0].contiguous())
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = wasserstein_distance(xjbg0.cpu().detach().numpy(), xjbg1.cpu().detach().numpy())
#                     if distance > all_distance[neuron]:
#                         all_distance[neuron] = distance
#         elif features[f'{layer_num}'].dim() == 3:
#             hidden_num = features[f'{layer_num}'].shape[2]
#             all_distance = [0] * hidden_num
#             for combo in itertools.combinations(range(len(prunedata)), 2):
#                 for hidden in range(hidden_num):
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res[f'{combo[0]}'])):
#                         xjbg0.append(output_res[f'{combo[0]}'][i][:, :, hidden].contiguous())
#                     for i in range(len(output_res[f'{combo[1]}'])):
#                         xjbg1.append(output_res[f'{combo[1]}'][i][:, :, hidden].contiguous())
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = ot.sliced.sliced_wasserstein_distance(xjbg0.cpu().detach().numpy(),
#                                                                      xjbg1.cpu().detach().numpy(),
#                                                                      n_projections=50)
#                     if distance > all_distance[hidden]:
#                         all_distance[hidden] = distance
#
#     print(f'The Distance of the {layer_num}th layer is calculated.')
#     all_distance = torch.tensor(all_distance)
#     features.clear()
#     handle.remove()
#
#     return all_distance
#
#
# ###########################################################################################################
# ###########################################################################################################
#
# #v2：This version is the same as the previous version
# # （get_Distance）, and in order to reduce the pressure
# # on the video memory and memory, the data is saved on
# # the hard disk. Although it slows down the running
# # speed, it can be adopted in the graphics card and
# # insufficient memory space.
#
# def get_Distance2(model,prunedata,layer_num,device,path):
#     #
#     # model: is the model we want to prune
#     # prunedata :is the output from get_prunedata
#     # layer_num : it the aim layer we want to compute Distance
#     # device: torch.device('cpu') or 'cuda'
#     # path: A path to save the temporary file
#     #
#     model.to(device)
#     # 注册钩子到每一层
#     for i,(name, layer) in enumerate(model.named_modules()):
#         if i == layer_num:
#             handle = layer.register_forward_hook(get_features(f'{i}'))
#             break
# ##############################以下是收集输出########################################
#     model.eval()
#     with torch.no_grad():
#         for type in range(len(prunedata)):
#             output_res = []
#             for num in range(len(prunedata[f'{type}'])):
#                 model(prunedata[f'{type}'][num].to(device))
#                 output_res.append(features[f'{layer_num}'].view(features[f'{layer_num}'].size(0), features[f'{layer_num}'].size(1), -1).to(device))
#             with open(path+f'/layer{layer_num}_output_type{type}.pkl', 'wb') as file:
#                 pickle.dump(output_res, file)
#     #############################以下是计算距离########################################
#         if features[f'{layer_num}'].dim() == 4:
#             channel_num = features[f'{layer_num}'].shape[1]
#             all_distance = [0]*channel_num
#             for combo in itertools.combinations(range(len(prunedata)), 2):
#                 with open(path+f'/layer{layer_num}_output_type{combo[0]}.pkl', 'rb') as file:
#                     output_res0 = pickle.load(file)
#                 with open(path+f'/layer{layer_num}_output_type{combo[1]}.pkl', 'rb') as file:
#                     output_res1 = pickle.load(file)
#                 for channel in range(channel_num):
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res0)):
#                         xjbg0.append(output_res0[i][:,channel,:])
#                     for i in range(len(output_res1)):
#                         xjbg1.append(output_res1[i][:,channel,:])
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = ot.sliced.sliced_wasserstein_distance(xjbg0.cpu().detach().numpy(),
#                                                                      xjbg1.cpu().detach().numpy(),
#                                                                      n_projections =50)
#                     if distance > all_distance[channel]:
#                         all_distance[channel] = distance
#
#         elif features[f'{layer_num}'].dim() == 2:
#             neuron_num = features[f'{layer_num}'].shape[1]
#             all_distance = [0] *neuron_num
#             for combo in itertools.combinations(range(len(output_res)), 2):
#                 with open(path+f'/layer{layer_num}_output_type{combo[0]}.pkl','rb') as file:
#                     output_res0 = pickle.load(file)
#                 with open(path+f'/layer{layer_num}_output_type{combo[1]}.pkl','rb') as file:
#                     output_res1 = pickle.load(file)
#                 for neuron in range(neuron_num):
#                     # print(f'第{neuron}个神经元正在计算距离')
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res0)):
#                         xjbg0.append(output_res0[i][:,neuron,0])
#                     for i in range(len(output_res1)):
#                         xjbg1.append(output_res1[i][:,neuron,0])
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = wasserstein_distance(xjbg0.cpu().detach().numpy(),
#                                                     xjbg1.cpu().detach().numpy())
#                     if distance > all_distance[neuron]:
#                         all_distance[neuron] = distance
#         elif features[f'{layer_num}'].dim() == 3:
#             hidden_num = features[f'{layer_num}'].shape[2]
#             all_distance = [0] * hidden_num
#             for combo in itertools.combinations(range(len(prunedata)), 2):
#                 with open(path+f'/layer{layer_num}_output_type{combo[0]}.pkl','rb') as file:
#                     output_res0 = pickle.load(file)
#                 with open(path+f'/layer{layer_num}_output_type{combo[1]}.pkl','rb') as file:
#                     output_res1 = pickle.load(file)
#                 for hidden in range(hidden_num):
#                     xjbg0 = []
#                     xjbg1 = []
#                     for i in range(len(output_res0)):
#                         xjbg0.append(output_res0[i][:, :, hidden])
#                     for i in range(len(output_res0)):
#                         xjbg1.append(output_res0[i][:, :, hidden])
#                     xjbg0 = torch.cat(xjbg0, dim=0)
#                     xjbg1 = torch.cat(xjbg1, dim=0)
#                     distance = ot.sliced.sliced_wasserstein_distance(xjbg0.cpu().detach().numpy(),
#                                                                      xjbg1.cpu().detach().numpy(),
#                                                                      n_projections=50)
#                     if distance > all_distance[hidden]:
#                         all_distance[hidden] = distance
#     print(f'The Distance of the {layer_num}th layer is calculated.')
#     all_distance = torch.tensor(all_distance)
#     features.clear()
#     handle.remove()
#     for type in range(len(prunedata)):
#         os.remove(path+f'/layer{layer_num}_output_type{type}.pkl')
#
#     return all_distance

###############################################################################################################
def build_comprehensive_index_cache(dataset, class_num=1000):
    """
    构建健壮的索引缓存，支持各种数据集类型
    """
    index_cache = {c: [] for c in range(class_num)}

    # 处理 Subset
    if isinstance(dataset, torch.utils.data.Subset):
        base_dataset = dataset.dataset
        indices = dataset.indices
    else:
        base_dataset = dataset
        indices = range(len(dataset))

    # 多种方式获取标签
    for new_idx, orig_idx in enumerate(indices):
        label = None

        # 方式1: 直接从样本获取
        if hasattr(base_dataset, 'samples'):
            _, label = base_dataset.samples[orig_idx]
        # 方式2: 从 targets 获取
        elif hasattr(base_dataset, 'targets'):
            if isinstance(base_dataset.targets, (list, tuple)):
                label = base_dataset.targets[orig_idx]
            else:  # tensor
                label = base_dataset.targets[orig_idx].item()
        # 方式3: 通过 __getitem__ 获取
        else:
            try:
                _, label = base_dataset[orig_idx]
            except (ValueError, IndexError):
                try:
                    sample = base_dataset[orig_idx]
                    if isinstance(sample, (list, tuple)) and len(sample) >= 2:
                        _, label = sample
                except:
                    continue

        if label is not None and 0 <= label < class_num:
            index_cache[label].append(new_idx)

    # 统计信息
    valid_classes = sum(1 for v in index_cache.values() if len(v) > 0)
    total_samples = sum(len(v) for v in index_cache.values())
    print(f"✅ Index cache built: {valid_classes} classes, {total_samples} samples")

    return index_cache


def sample_data_once(dataloader, index_cache, samples_per_class=50, max_classes=100):
    """
    一次性采样，返回所有选中的样本
    """
    # 选择类别
    if max_classes and len(index_cache) > max_classes:
        # class_sizes = {cls: len(indices) for cls, indices in index_cache.items()}
        # selected_classes = sorted(class_sizes, key=class_sizes.get, reverse=True)[:max_classes]
        selected_classes = random.sample(list(index_cache.keys()), max_classes)
    else:
        selected_classes = list(index_cache.keys())

    print(f"🎯 Sampling {samples_per_class} samples from {len(selected_classes)} classes...")

    # 收集样本
    class_samples = {}
    for cls in selected_classes:
        if cls in index_cache and len(index_cache[cls]) >= samples_per_class:
            selected_indices = random.sample(index_cache[cls], samples_per_class)
            samples = [dataloader.dataset[idx][0] for idx in selected_indices]
            class_samples[cls] = torch.stack(samples)
        else:
            print(f"⚠️ Class {cls} has insufficient samples: {len(index_cache.get(cls, []))}")

    print(f"✅ Sampling completed: {sum(len(s) for s in class_samples.values())} total samples")
    return class_samples


def get_layer_distance_memory_efficient(model, layer_num, class_samples, device):
    """
    内存高效版本：动态提取特征，不保存所有特征
    """
    model.to(device)

    # 注册当前层的钩子
    for i, (name, layer) in enumerate(model.named_modules()):
        if i == layer_num:
            handle = layer.register_forward_hook(get_features(f'{layer_num}'))
            break

    model.eval()

    # 获取特征维度信息（用第一个类别测试）
    first_cls = list(class_samples.keys())[0]
    test_sample = class_samples[first_cls][:1].to(device)
    with torch.no_grad():
        model(test_sample)
        feat = features.get(f'{layer_num}')
        if feat is None:
            print(f"⚠️ No features found for layer {layer_num}")
            handle.remove()
            return None

        # 确定特征维度
        if feat.dim() == 4:  # CNN特征 [batch, channels, H, W]
            channel_num = feat.shape[1]
            all_distance = [0] * channel_num
            feat_type = 'cnn'
        elif feat.dim() == 2:  # 全连接特征 [batch, features]
            neuron_num = feat.shape[1]
            all_distance = [0] * neuron_num
            feat_type = 'fc'
        elif feat.dim() == 3:  # RNN特征 [batch, seq_len, hidden]
            hidden_num = feat.shape[2]
            all_distance = [0] * hidden_num
            feat_type = 'rnn'
        else:
            print(f"⚠️ Unsupported feature dimension {feat.dim()}")
            handle.remove()
            return None

    print(f"  Processing {len(all_distance)} units ({feat_type} features)")

    # 获取类别列表并排序
    class_list = sorted(class_samples.keys())
    total_pairs = len(class_list) * (len(class_list) - 1) // 2

    print(f"  Computing {total_pairs} class pairs...")

    # 外层循环：k1 从 1 到 K-1（实际索引从第二个开始）
    for i in range(1, len(class_list)):
        k1 = class_list[i]

        # 🎯 提取 k1 的特征（只提取一次，用于所有与 k2 的配对）
        features_k1 = extract_class_features(
            model, class_samples[k1], device, layer_num, feat_type)

        if features_k1 is None:
            continue

        # 内层循环：k2 从 0 到 i-1
        for j in range(i):
            k2 = class_list[j]

            # 🎯 提取 k2 的特征
            features_k2 = extract_class_features(
                model, class_samples[k2], device, layer_num, feat_type)

            if features_k2 is None:
                continue

            # 🎯 计算距离并更新最大值
            update_distances(all_distance, features_k1, features_k2,
                             feat_type, device)

            # 🎯 立即丢弃 k2 的特征
            del features_k2
            torch.cuda.empty_cache()

        # 🎯 处理完所有 k2 后，丢弃 k1 的特征
        del features_k1
        torch.cuda.empty_cache()

        # 进度显示
        if i % 200 == 0:
            completed_pairs = i * (i + 1) // 2
            print(f"    Progress: {completed_pairs}/{total_pairs} pairs "
                  f"({completed_pairs / total_pairs * 100:.1f}%)")

    # 清理
    features.clear()
    handle.remove()

    print(f"✅ Layer {layer_num} completed")
    return torch.tensor(all_distance)


def get_layer_distance(model, layer_num, class_samples, device,
                                   sample_classes=10, num_iterations=500):
    """
    蒙特卡洛版本：重复采样类别对，记录最大距离
    """
    model.to(device)

    # 注册当前层的钩子
    for i, (name, layer) in enumerate(model.named_modules()):
        if i == layer_num:
            handle = layer.register_forward_hook(get_features(f'{layer_num}'))
            break

    model.eval()

    # 获取特征维度信息
    first_cls = list(class_samples.keys())[0]
    test_sample = class_samples[first_cls][:1].to(device)
    with torch.no_grad():
        model(test_sample)
        feat = features.get(f'{layer_num}')
        if feat is None:
            print(f"⚠️ No features found for layer {layer_num}")
            handle.remove()
            return None

        # 确定特征维度
        if feat.dim() == 4:  # CNN特征
            channel_num = feat.shape[1]
            all_distance = [0] * channel_num
            feat_type = 'cnn'
        elif feat.dim() == 2:  # 全连接特征
            neuron_num = feat.shape[1]
            all_distance = [0] * neuron_num
            feat_type = 'fc'
        elif feat.dim() == 3:  # RNN特征
            hidden_num = feat.shape[2]
            all_distance = [0] * hidden_num
            feat_type = 'rnn'
        else:
            print(f"⚠️ Unsupported feature dimension {feat.dim()}")
            handle.remove()
            return None

    # print(
    #     f"  Processing {len(all_distance)} units, {sample_classes} classes per iteration, {num_iterations} iterations")

    # 所有可用类别
    all_classes = list(class_samples.keys())


    for iteration in range(num_iterations):
        # if iteration % 200 == 0:
        #     print(f"    Iteration {iteration + 1}/{num_iterations}")

        # 1. 随机采样类别
        sampled_classes = random.sample(all_classes, sample_classes)

        # 2. 计算这些类别中所有配对的距离
        for k1, k2 in itertools.combinations(sampled_classes, 2):
            # 提取特征
            features_k1 = extract_class_features(
                model, class_samples[k1], device, layer_num, feat_type)
            features_k2 = extract_class_features(
                model, class_samples[k2], device, layer_num, feat_type)

            if features_k1 is None or features_k2 is None:
                continue

            # 计算距离并更新最大值
            update_distances_max(all_distance, features_k1, features_k2, feat_type, device)

            # 清理
            del features_k1, features_k2
            torch.cuda.empty_cache()

    # 清理
    features.clear()
    handle.remove()

    print(f"✅ The Distance of layer {layer_num} is calculated.")
    return torch.tensor(all_distance)


def update_distances_max(all_distance, features1, features2, feat_type, device):
    """
    计算距离并只更新最大值（不累加）
    """
    features1_gpu = [f.to(device) for f in features1]
    features2_gpu = [f.to(device) for f in features2]

    if feat_type == 'cnn':
        channel_num = features1_gpu[0].shape[1]
        for channel in range(channel_num):
            x0 = torch.cat([f[:, channel, :] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, channel, :] for f in features2_gpu], dim=0)
            distance = sliced_wasserstein_distance(x0, x1, n_projections=128)
            if distance > all_distance[channel]:
                all_distance[channel] = distance

    elif feat_type == 'fc':
        neuron_num = features1_gpu[0].shape[1]
        for neuron in range(neuron_num):
            x0 = torch.cat([f[:, neuron, 0] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, neuron, 0] for f in features2_gpu], dim=0)
            distance = wasserstein_1d(x0, x1)
            if distance > all_distance[neuron]:
                all_distance[neuron] = distance

    elif feat_type == 'rnn':
        hidden_num = features1_gpu[0].shape[2]
        for hidden in range(hidden_num):
            x0 = torch.cat([f[:, :, hidden] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, :, hidden] for f in features2_gpu], dim=0)
            distance = sliced_wasserstein_distance(x0, x1, n_projections=64)
            if distance > all_distance[hidden]:
                all_distance[hidden] = distance

    # 清理GPU内存
    del features1_gpu, features2_gpu
    torch.cuda.empty_cache()


def extract_class_features(model, samples, device, layer_num, feat_type):
    """
    提取单个类别的特征
    """
    features_list = []
    batch_size = min(256, len(samples))
    with torch.no_grad():
        for i in range(0, len(samples), batch_size):
            batch = samples[i:i + batch_size].to(device)
            model(batch)

            feat = features.get(f'{layer_num}')
            if feat is not None:
                # 根据特征类型处理
                if feat_type == 'cnn':
                    # CNN: [batch, channels, H, W] -> [batch, channels, H*W]
                    feat_processed = feat.view(feat.size(0), feat.size(1), -1)
                elif feat_type == 'fc':
                    # FC: [batch, features] -> [batch, features, 1]
                    feat_processed = feat.unsqueeze(-1)
                elif feat_type == 'rnn':
                    # RNN: [batch, seq_len, hidden] 保持原样
                    feat_processed = feat
                else:
                    feat_processed = feat

                features_list.append(feat_processed)  # 移到CPU保存.cpu()

            del batch
            if device.type == 'cuda':
                torch.cuda.empty_cache()

    return features_list if features_list else None


def update_distances(all_distance, features1, features2, feat_type, device):
    """
    计算两个类别特征的距离并更新最大值
    """
    # 移动到GPU计算
    features1_gpu = [f.to(device) for f in features1]
    features2_gpu = [f.to(device) for f in features2]

    if feat_type == 'cnn':
        # CNN: 对每个通道计算距离
        channel_num = features1_gpu[0].shape[1]
        for channel in range(channel_num):
            x0 = torch.cat([f[:, channel, :] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, channel, :] for f in features2_gpu], dim=0)
            distance = sliced_wasserstein_distance(x0, x1, n_projections=128)
            if distance > all_distance[channel]:
                all_distance[channel] = distance

    elif feat_type == 'fc':
        # FC: 对每个神经元计算距离
        neuron_num = features1_gpu[0].shape[1]
        for neuron in range(neuron_num):
            x0 = torch.cat([f[:, neuron, 0] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, neuron, 0] for f in features2_gpu], dim=0)
            distance = wasserstein_1d(x0, x1)
            if distance > all_distance[neuron]:
                all_distance[neuron] = distance

    elif feat_type == 'rnn':
        # RNN: 对每个隐藏单元计算距离
        hidden_num = features1_gpu[0].shape[2]
        for hidden in range(hidden_num):
            x0 = torch.cat([f[:, :, hidden] for f in features1_gpu], dim=0)
            x1 = torch.cat([f[:, :, hidden] for f in features2_gpu], dim=0)
            distance = sliced_wasserstein_distance(x0, x1, n_projections=128)
            if distance > all_distance[hidden]:
                all_distance[hidden] = distance

    # 清理GPU内存
    del features1_gpu, features2_gpu
    torch.cuda.empty_cache()


###################################################################################################################
# 创建一个字典来存储每一层的梯度
gradients = {}
# 定义一个钩子函数来获取梯度
def get_grad(name):
    def hook(module, grad_input, grad_output):
        # grad_input是输入的梯度，grad_output是输出的梯度
        gradients[name] = grad_output[0]
    return hook

# 定义一个钩子函数来捕获GRU model权重的梯度
gru1_weight_ih_grad = None
gru1_weight_hh_grad = None

def hook_gru1_weight_ih(grad):
    global gru1_weight_ih_grad
    gru1_weight_ih_grad = grad

def hook_gru1_weight_hh(grad):
    global gru1_weight_hh_grad
    gru1_weight_hh_grad = grad

# def get_ReconstructionError(model,prune_datasetloader,layer_num,device,loss_function):
#     #
#     # model: is the model we want to prune.
#     # prune_datasetloader : is （from torch.utils.data import DataLoader）.
#     # layer_num : it the aim layer we want to compute Distance.
#     # device: torch.device('cpu') or torch.device('cuda') .
#     # loss_function: The loss function used for model training.
#     #
#
#     model.to(device)
#     model.train()
#     if isinstance(list(model.named_modules())[layer_num][1],nn.GRU):
#         the_wih = list(model.named_modules())[layer_num][1].weight_ih_l0.data
#         the_whh = list(model.named_modules())[layer_num][1].weight_hh_l0.data
#         the_Bias_ih = list(model.named_modules())[layer_num][1].bias_ih_l0.data
#         the_Bias_hh = list(model.named_modules())[layer_num][1].bias_hh_l0.data
#         loss_fun = loss_function
#         loss_fun.to(device)
#         gradient = torch.zeros(the_wih.shape[0]).to(device)  # shape[0]
#         hinden_num = the_wih.shape[0]
#         for inputs, targets in prune_datasetloader:
#             inputs = inputs.to(device)
#             targets = targets.to(device)
#             output = model(inputs)
#             loss = loss_fun(output, targets)
#             loss.backward()
#             gradient += torch.sum(list(model.named_modules())[layer_num][1].weight_ih_l0.grad * the_wih,dim=1)
#             gradient += torch.sum(list(model.named_modules())[layer_num][1].weight_hh_l0.grad * the_whh,dim=1)
#             gradient += list(model.named_modules())[layer_num][1].bias_ih_l0.grad * the_Bias_ih
#             gradient += list(model.named_modules())[layer_num][1].bias_hh_l0.grad * the_Bias_hh
#         gradient = gradient[0:int(hinden_num/3)] + gradient[int(hinden_num/3):int(hinden_num/3*2)] + gradient[int(hinden_num/3*2):]
#     else:
#         the_weight = list(model.named_modules())[layer_num][1].weight.data
#         dim = the_weight.dim()
#         the_bias = list(model.named_modules())[layer_num][1].bias.data.view(the_weight.shape[0], *([1] * (dim - 1)))
#         # print(the_weight.shape)
#         loss_fun = loss_function
#         loss_fun.to(device)
#         gradient = torch.zeros(the_weight.shape).to(device)#shape[0]
#         # print(gradients[f'{layer_num}'].shape)
#         for inputs, targets in prune_datasetloader:
#             inputs = inputs.to(device)
#             targets = targets.to(device)
#             output = model(inputs)
#             loss = loss_fun(output, targets)
#             loss.backward()
#             gradient += list(model.named_modules())[layer_num][1].weight.grad * the_weight
#             gradient += list(model.named_modules())[layer_num][1].bias.grad.view(the_weight.shape[0], *([1] * (dim - 1))) * the_bias
#         gradient = torch.sum(gradient,dim = list(range(1,gradient.dim())))
#     print(f'The Reconstruction Error of the {layer_num}th layer is calculated.')
#     gradients.clear()
#
#     return gradient
# ################################################
# ################################################
# # The only difference between the two versions is
# # whether the gradient is zeroed out on each
# # calculation, and empirically the first version
# #（get_ReconstructionError）works better
# def get_ReconstructionError2(model,prune_datasetloader,layer_num,device,loss_function):
#     #
#     # model: is the model we want to prune.
#     # prune_datasetloader : is （from torch.utils.data import DataLoader）.
#     # layer_num : it the aim layer we want to compute Distance.
#     # device: torch.device('cpu') or torch.device('cuda') .
#     # loss_function: The loss function used for model training.
#     #
#     model.to(device)
#     model.train()
#     if isinstance(list(model.named_modules())[layer_num][1],nn.GRU):
#         the_wih = list(model.named_modules())[layer_num][1].weight_ih_l0.data
#         the_whh = list(model.named_modules())[layer_num][1].weight_hh_l0.data
#         the_Bias_ih = list(model.named_modules())[layer_num][1].bias_ih_l0.data
#         the_Bias_hh = list(model.named_modules())[layer_num][1].bias_hh_l0.data
#         loss_fun = loss_function
#         loss_fun.to(device)
#         gradient = torch.zeros(the_wih.shape[0]).to(device)  # shape[0]
#         hinden_num = the_wih.shape[0]
#         for inputs, targets in prune_datasetloader:
#             inputs = inputs.to(device)
#             targets = targets.to(device)
#             output = model(inputs)
#             loss = loss_fun(output, targets)
#             loss.backward()
#             gradient += torch.sum(list(model.named_modules())[layer_num][1].weight_ih_l0.grad * the_wih,dim=1)
#             gradient += torch.sum(list(model.named_modules())[layer_num][1].weight_hh_l0.grad * the_whh,dim=1)
#             gradient += list(model.named_modules())[layer_num][1].bias_ih_l0.grad * the_Bias_ih
#             gradient += list(model.named_modules())[layer_num][1].bias_hh_l0.grad * the_Bias_hh
#         gradient = gradient[0:int(hinden_num/3)] + gradient[int(hinden_num/3):int(hinden_num/3*2)] + gradient[int(hinden_num/3*2):]
#     else:
#         the_weight = list(model.named_modules())[layer_num][1].weight.data
#         dim = the_weight.dim()
#         the_bias = list(model.named_modules())[layer_num][1].bias.data.view(the_weight.shape[0], *([1] * (dim- 1)))
#         loss_fun = nn.CrossEntropyLoss()
#         loss_fun.to(device)
#         model.zero_grad()
#         for inputs, targets in prune_datasetloader:
#             inputs = inputs.to(device)
#             targets = targets.to(device)
#             output = model(inputs)
#             loss = loss_fun(output, targets)
#             loss.backward()
#         gradient = (list(model.named_modules())[layer_num][1].weight.grad * the_weight +
#                     list(model.named_modules())[layer_num][1].bias.grad.view(the_weight.shape[0],*([1] * (dim - 1))) * the_bias)
#         gradient = torch.sum(gradient,dim = list(range(1,gradient.dim())))
#     print(f'The Reconstruction Error of the {layer_num}th layer is calculated.')
#     gradients.clear()
#
#     return gradient
###################################################################################################################################

def get_ReconstructionScore_fast(model, prune_loader, layer_num, device, loss_function):
    model.to(device)
    model.train()

    target_layer = list(model.named_modules())[layer_num][1]

    # 冻结其他层，只保留目标层梯度
    for name, param in model.named_parameters():
        param.requires_grad_(False)
    for param in target_layer.parameters():
        param.requires_grad_(True)

    grad_accum = None  # 🚨 不要用 Python 整数当初始值
    use_amp = (device.type == 'cuda')
    for inputs, targets in prune_loader:
        inputs = inputs.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        model.zero_grad(set_to_none=True)

        try: # PyTorch (>= 1.14)
            scaler = torch.amp.GradScaler(enabled=use_amp)
            output = model(inputs)
            loss = loss_function(output, targets)
            scaler.scale(loss).backward()
        except AttributeError:
            try: # PyTorch (>= 1.6)
                from torch.cuda.amp import GradScaler
                scaler = GradScaler(enabled=use_amp)
                output = model(inputs)
                loss = loss_function(output, targets)
                scaler.scale(loss).backward()
            except ImportError: # older,close AMP
                use_amp = False
                output = model(inputs)
                loss = loss_function(output, targets)
                loss.backward()

        grad_w = target_layer.weight.grad  # 不需要 grad
        contrib_w = (grad_w * target_layer.weight).sum(dim=list(range(1, grad_w.dim())))

        if target_layer.bias is not None:
            grad_b = target_layer.bias.grad
            contrib_b = grad_b * target_layer.bias

        # 2. ✅ 在 no_grad 里做累计 / 或者用 detach()
        with torch.no_grad():
            if target_layer.bias is not None:
                contrib = contrib_w + contrib_b
                if grad_accum is None:
                    grad_accum = contrib.clone()
                else:
                    grad_accum.add_(contrib)
            else:
                contrib = contrib_w
                if grad_accum is None:
                    grad_accum = contrib.clone()
                else:
                    grad_accum.add_(contrib)

        # 3. 及时释放中间变量
        del output, loss, contrib_w, contrib_b, contrib
        if device.type == 'cuda':
            torch.cuda.empty_cache()

    print(f"✅ The Reconstruction Score of layer {layer_num} is calculated.")

    # 4. 恢复 requires_grad
    for param in model.parameters():
        param.requires_grad_(True)

    # 5. 返回 CPU 上的绝对值
    return grad_accum.abs().detach().cpu()

########################################################################################################################

def get_k_list(results,the_list_of_layers_to_prune,ToD_level=0.005):
    #
    # results: resluts save from main
    # the_list_of_layers_to_compute_Distance: a list of the layer number which we want to get Distance
    # the_list_of_layers_to_prune: a list of the layer number which we want to get ReconstructionError
    # FDR_level

    results[f'D_{len(the_list_of_layers_to_prune) - 1}_s2b_idx'] = list(range(1000))
    k_list = []
    for j in range(len(the_list_of_layers_to_prune)):
        if (j + 1) == len(the_list_of_layers_to_prune):
            k_list.append(0)
            break
        neuron_number = len(results[f'D_{j}_s2b_idx'])
        # m = int((1-2*FDR_level)*neuron_number)
        for i in range(int(0.99 * neuron_number)):
            k = int(0.99 * neuron_number) - i
            intersection = list(
                set(results[f'D_{j}_s2b_idx'][:k]) & set(results[f'RE_{j}_hat_s2b_idx'][int(neuron_number - k):]))
            # print(len(intersection)/k)
            if len(intersection) / k <= ToD_level:
                print(f'The prunable set size for layer {the_list_of_layers_to_prune[j]}th is {k}')
                k_list.append(k)
                break
            if i == (int(0.99 * neuron_number) - 1):
                print(f'The {the_list_of_layers_to_prune[j]}th layer is inspected and does not need to be pruned')
                k_list.append(0)
                break
    return k_list


#######################################################################################################################

def FAIR_Pruner_get_results(model,prune_datasetloader,results_save_path,the_list_of_layers_to_prune,the_list_of_layers_to_compute_Distance,loss_function,device,class_num,the_samplesize_for_compute_distance=16,class_num_for_distance=None,num_iterations=1):
    # with open(data_path, 'rb') as f:
    #     prune_datasetloader = pickle.load(f)
    # model = torch.load(model_path)
    index_cache = build_comprehensive_index_cache(prune_datasetloader.dataset, class_num=class_num)
    if class_num_for_distance is None:
        class_num_for_distance = class_num
    class_samples = sample_data_once(prune_datasetloader, index_cache, the_samplesize_for_compute_distance, class_num)
    results = {}
    for layer_num in range(len(the_list_of_layers_to_compute_Distance)):
        results[f'RE_{layer_num}_hat'] = get_ReconstructionScore_fast(model, prune_datasetloader,
                                                                layer_num=the_list_of_layers_to_prune[layer_num],
                                                                device=device, loss_function=loss_function)
        results[f'RE_{layer_num}_hat_s2b_idx'] = torch.argsort(results[f'RE_{layer_num}_hat']).tolist()
        torch.cuda.empty_cache()
        results[f'D_{layer_num}'] = get_layer_distance(model,layer_num=the_list_of_layers_to_compute_Distance[layer_num],class_samples=class_samples, device=device, sample_classes=class_num_for_distance, num_iterations=num_iterations)
        results[f'D_{layer_num}_s2b_idx'] = torch.argsort(results[f'D_{layer_num}']).tolist()
        torch.cuda.empty_cache()
    with open(results_save_path, 'wb') as file:
        pickle.dump(results, file)
    return results

import copy
from typing import Optional

import torch
import torch.nn as nn
from torch.optim import SGD
from torch.utils.data import DataLoader


@torch.no_grad()
def _evaluate(model: nn.Module, val_loader: DataLoader, criterion: nn.Module, device: torch.device) -> float:
    """Return average validation loss."""
    model.eval()
    total_loss, total_n = 0.0, 0

    for batch in val_loader:
        # 默认 batch=(inputs, targets). 如果你的 batch 是 dict，在这里改取值方式
        inputs, targets = batch
        inputs = inputs.to(device, non_blocking=True)
        targets = targets.to(device, non_blocking=True)

        logits = model(inputs)  # [B, C]
        loss = criterion(logits, targets)

        bs = targets.size(0)
        total_loss += loss.item() * bs
        total_n += bs

    return total_loss / max(total_n, 1)


def finetune_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int,
    *,
    lr: float = 1e-2,
    momentum: float = 0.9,
    weight_decay: float = 0.0,
    nesterov: bool = False,
    device: Optional[str] = None,
    grad_clip_norm: Optional[float] = None,
    amp: bool = True,
    log_every: int = 50,
) -> nn.Module:
    """
    微调函数（多分类）：
    - Loss: CrossEntropyLoss
    - Optim: SGD
    - 返回：验证集上 val_loss 最佳的模型（权重已加载，不保存本地）
    """
    dev = torch.device(device) if device is not None else torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )
    model = model.to(dev)

    criterion = nn.CrossEntropyLoss()
    optimizer = SGD(
        model.parameters(),
        lr=lr,
        momentum=momentum,
        weight_decay=weight_decay,
        nesterov=nesterov,
    )

    use_amp = bool(amp and dev.type == "cuda")
    scaler = torch.cuda.amp.GradScaler(enabled=use_amp)

    best_state = copy.deepcopy(model.state_dict())
    best_val_loss = float("inf")

    for epoch in range(1, epochs + 1):
        model.train()
        run_loss, run_correct, run_n = 0.0, 0, 0

        for step, batch in enumerate(train_loader, start=1):
            inputs, targets = batch
            inputs = inputs.to(dev, non_blocking=True)
            targets = targets.to(dev, non_blocking=True)

            optimizer.zero_grad(set_to_none=True)

            with torch.cuda.amp.autocast(enabled=use_amp):
                logits = model(inputs)          # [B, C]
                loss = criterion(logits, targets)

            scaler.scale(loss).backward()

            if grad_clip_norm is not None:
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)

            scaler.step(optimizer)
            scaler.update()

            bs = targets.size(0)
            run_loss += loss.item() * bs
            run_correct += (logits.detach().argmax(dim=1) == targets).sum().item()
            run_n += bs

            if log_every > 0 and (step % log_every == 0):
                print(
                    f"[Epoch {epoch}/{epochs}] step {step}/{len(train_loader)} | "
                    f"train_loss={run_loss/max(run_n,1):.4f} train_acc={run_correct/max(run_n,1):.4f}"
                )

        # validate & track best
        val_loss = _evaluate(model, val_loader, criterion, dev)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = copy.deepcopy(model.state_dict())

        print(
            f"[Epoch {epoch}/{epochs}] "
            f"train_loss={run_loss/max(run_n,1):.4f} train_acc={run_correct/max(run_n,1):.4f} | "
            f"val_loss={val_loss:.4f} (best={best_val_loss:.4f})"
        )

    # load best weights (no local saving)
    model.load_state_dict(best_state)
    return model



def Generate_model_after_pruning(tiny_model_skeleton,original_model_path,tiny_model_save_path,results,k_list,the_list_of_layers_to_prune,finetune_pruned=False,finetune_epochs=10,finetunedata=None,valdata=None):
    tiny_model = tiny_model_skeleton
    original_model = torch.load(original_model_path)
    model_after_pruning_layername = {}
    for i, (name, layer) in enumerate(tiny_model.named_modules()):
        model_after_pruning_layername[f'{i}'] = layer
    layername = {}
    layer_idx = []
    covn2linear = 0
    for i, (name, layer) in enumerate(original_model.named_modules()):
        layername[f'{i}'] = layer
        if hasattr(layer, 'weight') and isinstance(layer.weight, torch.nn.Parameter):
            layer_idx.append(i)
        if isinstance(layer, nn.Linear) and covn2linear == 0:
            covn2linear = 1
            layer_num_conv2linear = layer_idx[-1]
    with torch.no_grad():
        for j, i in enumerate(the_list_of_layers_to_prune):
            position = results[f'D_{j}_s2b_idx']
            position = sorted(position[k_list[j]:])  # No pruning position
            # print(position)
            if j==0:
                if model_after_pruning_layername[f'{i}'].weight.dim() == 4:
                    model_after_pruning_layername[f'{i}'].weight = nn.Parameter(layername[f'{i}'].weight[position, :, :, :])
                    model_after_pruning_layername[f'{i}'].bias = nn.Parameter(layername[f'{i}'].bias[position])
                if layername[f'{i}'].weight.dim() == 2:
                    model_after_pruning_layername[f'{i}'].weight = nn.Parameter(layername[f'{i}'].weight[position, :])
                    model_after_pruning_layername[f'{i}'].bias = nn.Parameter(layername[f'{i}'].bias[position])
                old_position = position
            elif i==layer_num_conv2linear:
                xjbg = layername[f'{i}'].weight[position, :]
                old_position =  [ele for subele in [list(range(i1*layername[f'{int(i-2)}'].output_size[0]*layername[f'{int(i-2)}'].output_size[1],
                                                               (i1+1)*layername[f'{int(i-2)}'].output_size[0]*layername[f'{int(i-2)}'].output_size[1])) for i1 in old_position] for ele in subele]
                model_after_pruning_layername[f'{i}'].weight = nn.Parameter(xjbg[:, old_position])
                model_after_pruning_layername[f'{i}'].bias = nn.Parameter(layername[f'{i}'].bias[position])
                old_position = position
            else:
                if model_after_pruning_layername[f'{i}'].weight.dim() == 4:
                    xjbg = layername[f'{i}'].weight[position, :, :, :]
                    model_after_pruning_layername[f'{i}'].weight = nn.Parameter(xjbg[:, old_position, :, :])
                    model_after_pruning_layername[f'{i}'].bias = nn.Parameter(layername[f'{i}'].bias[position])
                if layername[f'{i}'].weight.dim() == 2:
                    xjbg = layername[f'{i}'].weight[position, :]
                    model_after_pruning_layername[f'{i}'].weight = nn.Parameter(xjbg[:, old_position])
                    model_after_pruning_layername[f'{i}'].bias = nn.Parameter(layername[f'{i}'].bias[position])
                old_position = position
    print(f'parameters number: {sum(p.numel() for p in tiny_model.parameters() if p.requires_grad)}')
    print(f'pruning rate: {1 - sum(p.numel() for p in tiny_model.parameters() if p.requires_grad) / sum(p.numel() for p in original_model.parameters() if p.requires_grad)}')
    report={}
    report["parameters number"] = sum(p.numel() for p in tiny_model.parameters() if p.requires_grad)
    report["pruning rate"] = 1 - sum(p.numel() for p in tiny_model.parameters() if p.requires_grad) / sum(p.numel() for p in original_model.parameters() if p.requires_grad)
    if finetune_pruned:
        tiny_model = finetune_model(model=tiny_model,
            train_loader=finetunedata,
            val_loader=valdata,
            epochs=finetune_epochs,
            lr=0.001,
            momentum=0.9,
            weight_decay=1e-4,
            device="cuda",
            grad_clip_norm=None,
            amp=True,
            log_every=100)

    torch.save(tiny_model,tiny_model_save_path)

    return tiny_model,report

class Tiny_model_class_vgg16(nn.Module):
    def __init__(self,k_list):
        super(Tiny_model_class_vgg16, self).__init__()
        self.k_list = k_list
        self.features = nn.Sequential(
            nn.Conv2d(3, 64 - k_list[0], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64 - k_list[0], 64 - k_list[1], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(64 - k_list[1], 128 - k_list[2], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128 - k_list[2], 128 - k_list[3], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(128 - k_list[3], 256 - k_list[4], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256 - k_list[4], 256 - k_list[5], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256 - k_list[5], 256 - k_list[6], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(256 - k_list[6], 512 - k_list[7], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(512 - k_list[7], 512 - k_list[8], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(512 - k_list[8], 512 - k_list[9], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(512 - k_list[9], 512 - k_list[10], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(512 - k_list[10], 512 - k_list[11], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(512 - k_list[11], 512 - k_list[12], kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )

        self.avgpool = nn.AdaptiveAvgPool2d(output_size=(7, 7))

        self.classifier = nn.Sequential(
            nn.Linear((512 - k_list[12]) * 7 * 7, 4096 - k_list[13]),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096 - k_list[13], 4096 - k_list[14]),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096 - k_list[14], 1000 - k_list[15])
        )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x

if __name__ == '__main__':
    model_path = r'C:\Users\Administrator\PycharmProjects\lcq\Data\CIFAR10_vgg16.pht'
    data_path =  r'C:\Users\Administrator\PycharmProjects\lcq\DataSet\cifar10_prune_dataset.pkl'
    with open(data_path, 'rb') as f:
        prune_datasetloader = pickle.load(f)
    fortestfinetunedata = prune_datasetloader
    fortestvaldata = prune_datasetloader
    model = torch.load(model_path)
    results_save_path = 'test_res.pkl'
    the_list_of_layers_to_prune = [2,4,7,9,12,14,16,19,21,23,26,28,30,35,38,41]
    the_list_of_layers_to_compute_Distance = [3,5,8,10,13,15,17,20,22,24,27,29,31,36,39]
    loss_function = nn.CrossEntropyLoss()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    class_num = 10
    results = FAIR_Pruner_get_results(model, prune_datasetloader, results_save_path, the_list_of_layers_to_prune,
                the_list_of_layers_to_compute_Distance, loss_function, device,class_num,the_samplesize_for_compute_distance=16,class_num_for_distance=None,num_iterations=1)
    k_list = get_k_list(results,   the_list_of_layers_to_prune,0.05)

    tiny_model_skeleton = Tiny_model_class_vgg16()
    tiny_model,report = Generate_model_after_pruning(tiny_model_skeleton,model_path,
                                 'test_tiny_model.pht',
                                 results,k_list,
                                 the_list_of_layers_to_prune,finetune_pruned=True,finetune_epochs=10,finetunedata=fortestvaldata,valdata=fortestvaldata)
    print(report)