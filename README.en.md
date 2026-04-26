# Behavior Indicator of Overreliance Dataset (English)

[English](./README.en.md) | [中文](./README.zh-CN.md)

This is a behavioral log dataset organized into `task_1`, `task_2`, and `task_3`. Each task contains interaction records from two page sources (`gpt` and `tasksheet`) and corresponding score files.

This document is based on the actual processing logic in `preprocess_remote.py` (the file content is the same as `pre_process.ipynb`), focusing on folder semantics, data generation flow, and practical usage notes.

This dataset is used in the paper *Behavioral Indicators of Overreliance During Interaction with Conversational Language Models*.
ACM DOI: https://dl.acm.org/doi/10.1145/3772318.3790332

## 1. Directory Overview

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

Each `task_x/` has the same structure:

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

## 2. Folder Descriptions

### `gpt_rawdata/`
Raw GPT-page behavioral logs (JSON arrays) at event-level granularity. Fields can vary across event types.

### `tasksheet_rawdata/`
Raw Task Sheet logs in the same format as `gpt_rawdata/`.

### `gpt_rawdata_txt/` and `tasksheet_rawdata_txt/`
Plain-text versions (`.txt`) of raw logs. They mirror the corresponding `.json` content.

### `gpt_processed_data/`
Processed GPT-page logs. `preprocess_remote.py` adds normalized fields such as:
- `timestamp_second`
- `relative_time`
- `index`

### `tasksheet_processed_data/`
Processed Task Sheet logs with a schema largely aligned to `gpt_processed_data/`.

### `combined_data/`
Chronologically merged logs from both processed streams. The script:
1. Reads processed logs from both pages
2. Sorts and merges records by `timestamp`
3. Normalizes timestamp format to `%Y-%m-%dT%H:%M:%S.%fZ`
4. Recomputes `timestamp_second` and `relative_time`
5. Reassigns `index`
6. Adds `page` (`gpt` or `tasksheet`) to mark event source

### `score/`
Task score CSV files: `score-task_1.csv`, `score-task_2.csv`, `score-task_3.csv`.
- `index`: sample ID
- `score`: score for the corresponding task

## 3. File Naming Rules

- Log files are typically ID-based, e.g., `1001.json`, `2148.json`.
- The same ID across folders usually refers to the same sample.
- `.txt` files are text mirrors of corresponding `.json` files.

## 4. Data Generation Flow (Based on `preprocess_remote.py`)

1. (Optional) `convert_txt_data_to_json`: convert `*_rawdata_txt/` into `*_rawdata/` (the notebook demonstrates this for `task_1` and `task_3`).
2. For each task, read GPT and Task Sheet logs and align by ID intersection (`read_raw_data_in_batch`).
3. Apply sample removals and manual fixes documented in the notebook notes (see Section 6).
4. Run event-level cleaning/aggregation for both pages:
   - `merge_mouseMovement_in_batch`
   - `merge_mousewheel_in_batch` (split sign into `yDirection`, aggregate `deltaY`)
   - `merge_keypress_in_batch` (merge consecutive keypresses on the same `target`; keep `Enter` separate)
   - `merge_delete_in_batch` (merge by time interval)
   - `change_idle_time_in_batch` (recompute `idle.duration` and remove invalid outliers)
   - `add_textLength_to_highlight_in_batch`
   - `change_scroll_data_in_batch` (add `scroll.yDirection`)
5. `normalize_timestamp_in_batch`: normalize timestamp format to `%Y-%m-%dT%H:%M:%S.%fZ`, and recompute `timestamp_second`, `relative_time`, and `index`.
6. `save_processed_data`: write `gpt_processed_data/` and `tasksheet_processed_data/`.
7. `combined_data/` (`preprocess_remote.py`): merge both processed streams by timeline, add `page`, then recompute relative time and index.
8. Use `score/` as supervision signals/labels.

## 5. Field Notes by Stage

- Raw common fields: `type`, `timestamp`.
- Time-compatibility fields: `firstNotNull.time` and `messageInterval.startTime` are normalized into `timestamp` semantics during processing.
- Common processed fields:
  - `timestamp`: normalized as `%Y-%m-%dT%H:%M:%S.%fZ`
  - `timestamp_second`: elapsed seconds from the first log in the file
  - `relative_time`: `timestamp_second / 5400 * 100`
  - `index`: in-file sequence index (reindexed after cleaning)
- Event-level fields (as used in notebook logic):
  - `mouseMovement`: `duration`, `totalMouseMovement`
  - `mousewheel`: aggregated absolute `deltaY`, `yDirection` (0=none, 1=up, 2=down), `duration`
  - `scroll`: `deltaY`, `yDirection`
  - `keypress`: `duration`, `key_count`, `target`
  - `deleteAction`: `duration`, `key_count`
  - `highlight`: `highlightedTextLength` (filled from `text`/`highlightedText` length if missing)
  - `copy` / `paste`: `textLength`
  - `idle`: recomputed `duration` (invalid values are filtered)
- Combined-stage extra field: `page` (`gpt` / `tasksheet`).

## 6. Sample Alignment and Known Notes

### 6.1 Alignment Rule
- `preprocess_remote.py` prioritizes IDs available in both GPT and Task Sheet logs; usable samples are usually based on the intersection.
- Before modeling, match IDs between logs and `score/` first.

### 6.2 Removed Samples
- `task_2/2119`: unreadable `gpt_rawdata` and empty `tasksheet_rawdata`.
- `task_2/2153`: insufficient data volume.
- Removed because not in `score`:
  - `task_2/lyx`
  - `task_3/1000`
  - `task_3/1008`
  - `task_3/1033`
  - `task_3/2001`
  - `task_3/2002`
  - `task_3/2004`
  - `task_3/2011`

### 6.3 Manual Corrections
- `task_2/2125` (`gpt` + `tasksheet`): fixed an abnormal ~14-hour gap.
- `task_2/2125` (`tasksheet`): removed trailing `mouseMovement` entries with backward timestamps near `2024-10-20T00:39:39.470Z` using the next `idle` timestamp as reference.
- `task_1/2043` (`gpt`): removed trailing `mouseMovement` entries with backward timestamps near `2024-10-19T00:50:45.016000Z` using the next `idle` timestamp as reference.
- `task_2/2115`: GPT and Task Sheet files were likely uploaded in swapped order and were corrected.
- `task_2/1030`, record #478 (`keypress`): `text` changed from `\u0002` to `\\u0002`.

### 6.4 Usage Suggestions
- For reproducibility, start from `combined_data/`.
- For deeper audit, trace back to `*_processed_data/` and `*_rawdata/`.

## 7. Recommended Reading Order

1. `score/`
2. `combined_data/`
3. `gpt_processed_data/` + `tasksheet_processed_data/`
4. `gpt_rawdata/` + `tasksheet_rawdata/`

## 8. Public Release Notes

### 8.1 Study Background and Tasks
Data was collected in three lab-study tasks:
- `task 1`: quiz solving
- `task 2`: summarization
- `task 3`: trip planning

### 8.2 Privacy and De-identification
This dataset has been privacy-processed and contains no personal information that can identify a specific individual, and no potentially sensitive identifying fields. LLM conversation content is strictly task-related and does not involve private information.

### 8.3 License / Usage Statement
Please refer to repository-root `LICENSE`: non-commercial research/education use only, mandatory attribution, and no re-identification or privacy-infringing use.

---

License quick links: [English](./LICENSE) | [中文](./LICENSE.zh-CN)

