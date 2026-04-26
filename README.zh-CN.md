# Behavior Indicator of Overreliance Dataset（中文）

[English](./README.en.md) | [中文](./README.zh-CN.md)

这是一个按 `task_1`、`task_2`、`task_3` 组织的行为日志数据集。每个任务都包含两个页面来源的交互记录：`gpt` 页面与 `tasksheet` 页面，以及对应的评分文件。

本 README 结合 `preprocess_remote.py` （该文件和`pre_process.ipynb`是一致的） 的处理逻辑编写，重点说明目录含义、数据生成流程与使用注意事项。

该数据集是论文 *Behavioral Indicators of Overreliance During Interaction with Conversational Language Models* 中使用的数据集。
ACM DOI：https://dl.acm.org/doi/10.1145/3772318.3790332

## 1. 目录总览

```text
dataset/
  README.md
  README.zh-CN.md
  README.en.md
  LICENSE
  LICENSE.zh-CN
  preprocess_remote.py
  task_1/
  task_2/
  task_3/
```

每个 `task_x/` 的结构一致：

```text
task_x/
  combined_data/
  gpt_processed_data/
  gpt_rawdata/
  gpt_rawdata_txt/
  score/
  tasksheet_processed_data/
  tasksheet_rawdata/
  tasksheet_rawdata_txt/
```

## 2. 各目录说明

### `gpt_rawdata/`
GPT 页面原始行为日志（JSON 数组），事件粒度最细，不同事件类型字段可能不同。

### `tasksheet_rawdata/`
Task Sheet 页面原始行为日志，格式与 `gpt_rawdata/` 一致。

### `gpt_rawdata_txt/` 与 `tasksheet_rawdata_txt/`
原始日志的文本版本（`.txt`），与对应 `.json` 内容一致。

### `gpt_processed_data/`
GPT 页面处理后日志。`preprocess_remote.py` 会补充标准化字段，如：
- `timestamp_second`
- `relative_time`
- `index`

### `tasksheet_processed_data/`
Task Sheet 页面处理后日志，字段体系与 `gpt_processed_data/` 基本一致。

### `combined_data/`
将两侧处理后日志按时间顺序合并的结果。脚本会：
1. 读取两侧处理后数据
2. 按 `timestamp` 排序合并
3. 统一时间戳格式为 `%Y-%m-%dT%H:%M:%S.%fZ`
4. 重算 `timestamp_second` 与 `relative_time`
5. 重编 `index`
6. 新增 `page` 字段标记来源（`gpt`/`tasksheet`）

### `score/`
任务评分文件（CSV）：`score-task_1.csv`、`score-task_2.csv`、`score-task_3.csv`。
- `index`：样本编号
- `score`：该样本在对应任务中的分数

## 3. 文件命名规则

- 日志文件通常以编号命名，如 `1001.json`、`2148.json`。
- 同一编号在不同目录中通常对应同一样本。
- `.txt` 是对应 `.json` 的文本镜像。

## 4. 数据生成流程（参考 `preprocess_remote.py`）

1. （可选）`convert_txt_data_to_json`：将 `*_rawdata_txt/` 转为 `*_rawdata/`（notebook 中示例了 `task_1`、`task_3`）。
2. 逐任务读取 `gpt_rawdata/` 与 `tasksheet_rawdata/`，按编号交集对齐（`read_raw_data_in_batch`）。
3. 根据 notebook 记录执行样本删除与人工修订（见第 6 节）。
4. 对两侧日志做事件级清洗/聚合：
   - `merge_mouseMovement_in_batch`
   - `merge_mousewheel_in_batch`（按符号拆分 `yDirection`，并汇总 `deltaY`）
   - `merge_keypress_in_batch`（同一 `target` 的连续输入聚合，`Enter` 单独处理）
   - `merge_delete_in_batch`（基于时间间隔聚合）
   - `change_idle_time_in_batch`（重算 `idle.duration`，并去除异常）
   - `add_textLength_to_highlight_in_batch`
   - `change_scroll_data_in_batch`（补充 `scroll.yDirection`）
5. `normalize_timestamp_in_batch`：统一时间戳格式为 `%Y-%m-%dT%H:%M:%S.%fZ`，并重算 `timestamp_second`、`relative_time`、`index`。
6. `save_processed_data`：输出 `gpt_processed_data/` 与 `tasksheet_processed_data/`。
7. `combined_data/`（`preprocess_remote.py`）：按时间合并两侧 processed 日志，补充 `page`，再次重算相对时间与索引。
8. 用 `score/` 提供监督信号或标签。

## 5. 字段说明（按处理阶段）

- 原始日志通用字段：`type`, `timestamp`。
- 时间兼容字段：`firstNotNull.time`、`messageInterval.startTime` 会在归一化时统一映射到 `timestamp` 语义。
- 处理后通用字段：
  - `timestamp`：统一到 `%Y-%m-%dT%H:%M:%S.%fZ`
  - `timestamp_second`：相对首条日志的秒数
  - `relative_time`：`timestamp_second / 5400 * 100`
  - `index`：文件内顺序索引（清洗后重排）
- 事件级字段（按 notebook 实际处理逻辑）：
  - `mouseMovement`：`duration`, `totalMouseMovement`
  - `mousewheel`：`deltaY`（绝对值聚合）, `yDirection`（0=无, 1=上, 2=下）, `duration`
  - `scroll`：`deltaY`, `yDirection`
  - `keypress`：`duration`, `key_count`, `target`（同一输入框聚合）
  - `deleteAction`：`duration`, `key_count`
  - `highlight`：`highlightedTextLength`（缺失时由 `text`/`highlightedText` 长度补齐）
  - `copy` / `paste`：`textLength`
  - `idle`：`duration`（由相邻事件时间差重算，异常值会过滤）
- 合并后附加字段：`page`（`gpt` / `tasksheet`）。

## 6. 样本对齐与已知注意事项

### 6.1 样本对齐规则
- `preprocess_remote.py` 优先处理两侧都存在的编号，最终可用样本通常是交集。
- 建模前建议先做 `score/` 与日志编号匹配。

### 6.2 数据删除
- `task_2/2119`：`gpt_rawdata` 无法打开且 `tasksheet_rawdata` 为空。
- `task_2/2153`：数据量过少。
- 因未出现在 `score` 中而删除：
  - `task_2/lyx`
  - `task_3/1000`
  - `task_3/1008`
  - `task_3/1033`
  - `task_3/2001`
  - `task_3/2002`
  - `task_3/2004`
  - `task_3/2011`

### 6.3 数据修改
- `task_2/2125`（`gpt` + `tasksheet`）：修正约 14 小时异常间隔。
- `task_2/2125`（`tasksheet`）：从 `2024-10-20T00:39:39.470Z` 开始的 `mouseMovement` 尾部有逆序时间戳，按后续 `idle` 删除异常项。
- `task_1/2043`（`gpt`）：从 `2024-10-19T00:50:45.016000Z` 开始的 `mouseMovement` 尾部有逆序时间戳，按后续 `idle` 删除异常项。
- `task_2/2115`：`gpt` 与 `tasksheet` 上传疑似互换，已交换修正。
- `task_2/1030` 第 478 条 `keypress`：`text` 从 `\u0002` 修正为 `\\u0002`。

### 6.4 使用建议
- 复现实验优先使用 `combined_data/`。
- 如需细粒度审查，再回看 `*_processed_data/` 与 `*_rawdata/`。

## 7. 推荐使用顺序

1. `score/`
2. `combined_data/`
3. `gpt_processed_data/` + `tasksheet_processed_data/`
4. `gpt_rawdata/` + `tasksheet_rawdata/`

## 8. 公开发布说明

### 8.1 数据采集背景与任务说明
本数据集采集于三个 lab study 任务：
- `task 1`: quiz solving
- `task 2`: summarization
- `task 3`: trip planning

### 8.2 隐私与脱敏说明
本数据集已完成隐私处理，不保留任何可定位到特定个人的私人信息，也不包含潜在敏感字段。数据中的与 LLM 对话内容仅与任务相关，不涉及隐私。

### 8.3 数据许可协议 / 使用声明
请以仓库根目录 `LICENSE` 为准：仅限非商业研究/教学用途，必须注明数据来源，禁止再识别或侵犯隐私。

---

License quick links: [English](./LICENSE) | [中文](./LICENSE.zh-CN)

