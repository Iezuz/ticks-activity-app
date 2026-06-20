import pandas as pd
import numpy as np
import json


# Функция для конвертации numpy типов в Python типы
def convert_to_serializable(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_to_serializable(item) for item in obj)
    return obj


# Загружаем данные
df = pd.read_csv('./weekly_train_data.csv')

# Анализируем каждый кластер
cluster_constants = {}

for cluster_id in df['cluster_id'].unique():
    cluster_data = df[df['cluster_id'] == cluster_id]

    # Общая статистика
    overall_mean = round(float(cluster_data['total_bites'].mean()), 1)
    overall_max = int(cluster_data['total_bites'].max())

    # Находим пиковые недели
    threshold = np.percentile(cluster_data['total_bites'], 75)
    peak_data = cluster_data[cluster_data['total_bites'] >= threshold]
    peak_weeks = sorted([int(w) for w in peak_data['week_number'].unique()])

    # Определяем начало и конец пикового сезона
    if peak_weeks:
        peak_start = min(peak_weeks)
        peak_end = max(peak_weeks)
    else:
        peak_start = 20
        peak_end = 25

    # Определяем тренд
    years = sorted([int(y) for y in cluster_data['year'].unique()])
    is_growing = 0
    if len(years) >= 2:
        mean_first = float(cluster_data[cluster_data['year'] == years[0]]['total_bites'].mean())
        mean_last = float(cluster_data[cluster_data['year'] == years[-1]]['total_bites'].mean())
        if mean_last > mean_first * 1.2:
            is_growing = 1
        elif mean_last < mean_first * 0.8:
            is_growing = -1

    # Определяем популярность
    if overall_mean < 3:
        popularity_score = 0.15
        category = 0
    elif overall_mean < 8:
        popularity_score = 0.35
        category = 1
    elif overall_mean < 13:
        popularity_score = 0.55
        category = 2
    elif overall_mean < 17:
        popularity_score = 0.65
        category = 3
    else:
        popularity_score = 0.75
        category = 4

    # Сохраняем в словарь
    cluster_constants[str(cluster_id)] = {
        'popularity_score': popularity_score,
        'popularity_category': category,
        'overall_mean': overall_mean,
        'overall_max': overall_max,
        'peak_season_start': peak_start,
        'peak_season_end': peak_end,
        'is_growing': is_growing
    }


# Конвертируем для JSON
cluster_constants_serializable = convert_to_serializable(cluster_constants)

# Сохраняем в JSON
with open('cluster_constants.json', 'w', encoding='utf-8') as f:
    json.dump(cluster_constants_serializable, f, indent=2, ensure_ascii=False)


