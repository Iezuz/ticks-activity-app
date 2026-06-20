import pandas as pd

# Загружаем данные
df = pd.read_csv('./predict_long.csv', parse_dates=['date'], sep=',')

# Убедимся, что даты отсортированы
df = df.sort_values(['cluster_id', 'date']).reset_index(drop=True)

# Добавляем колонки с годом и календарной неделей (ISO)
df['year'] = df['date'].dt.isocalendar().year
df['week'] = df['date'].dt.isocalendar().week

# Подсчитываем количество дней в каждой неделе для каждого кластера
df['days_in_week'] = df.groupby(['cluster_id', 'year', 'week'])['date'].transform('count')

# Удаляем недели, где меньше m дней
df_filtered = df[df['days_in_week'] >= 1].copy()

# Группируем по кластеру, году и неделе
grouped = df_filtered.groupby(['cluster_id', 'year', 'week']).agg(
    week_start=('date', 'min'),
    week_end=('date', 'max'),
    elevation=('elevation', 'first'),
    avg_snow_depth=('avg_snow_depth', 'first'),
    season_start_date=('season_start_date', 'first'),
).reset_index()

# Создаем строку с диапазоном дат
grouped['week_date_range'] = (grouped['week_start'].dt.strftime('%Y-%m-%d') +
                               ' - ' + grouped['week_end'].dt.strftime('%Y-%m-%d'))

# Добавляем номер недели (отдельная колонка)
grouped['week_number'] = grouped['week']  # просто номер недели

# Добавляем календарную неделю в формате год-неделя
grouped['calendar_week'] = grouped['year'].astype(str) + '-W' + grouped['week'].astype(str)

# Убираем временные колонки, оставляем нужные
result = grouped[['cluster_id', 'year', 'week_number', 'week_date_range', 'calendar_week',
                  'elevation', 'avg_snow_depth', 'season_start_date']]

# Сохраняем результат
result.to_csv('weekly_predict_long.csv', index=False)

# Показываем первые строки
print(result.head(10))

# Информация о количестве недель по кластерам
print("\nКоличество недель по кластерам (только с >1 днем):")
print(grouped.groupby('cluster_id').size())

# Дополнительно: сколько недель было отфильтровано
total_weeks_before = df.groupby(['cluster_id', 'year', 'week']).size().shape[0]
total_weeks_after = grouped.shape[0]
print(f"\nВсего недель до фильтрации: {total_weeks_before}")
print(f"Осталось недель (>=1 день): {total_weeks_after}")
print(f"Отфильтровано недель: {total_weeks_before - total_weeks_after}")