import pandas as pd



def add_weekly_bites_by_calendar_week(weekly_predictions_file, daily_data_file, output_file):
    """
    Альтернативный вариант: использует calendar_week для маппинга
    """

    # Загружаем предсказания
    weekly_df = pd.read_csv(weekly_predictions_file, encoding='utf-8')

    # Создаем маппинг по cluster_id + year + week_num
    weekly_df['week_key'] = weekly_df['cluster_id'].astype(str) + '_' + \
                            weekly_df['year'].astype(str) + '_W' + \
                            weekly_df['week_num'].astype(str).str.zfill(2)

    weekly_mapping = dict(zip(weekly_df['week_key'], weekly_df['predicted_bites']))

    # Загружаем ежедневные данные
    daily_df = pd.read_csv(daily_data_file, encoding='utf-8')
    daily_df['date'] = pd.to_datetime(daily_df['date'])

    # Добавляем week_num для каждой даты
    def get_week_info(date):
        # Используем ISO week date (как в calendar_week)
        year = date.isocalendar()[0]
        week_num = date.isocalendar()[1]
        return year, week_num

    daily_df['year'], daily_df['week_num'] = zip(*daily_df['date'].apply(get_week_info))

    # Создаем ключ для маппинга
    daily_df['week_key'] = daily_df['cluster_id'].astype(str) + '_' + \
                           daily_df['year'].astype(str) + '_W' + \
                           daily_df['week_num'].astype(str).str.zfill(2)

    # Маппим недельные укусы
    daily_df['weekly_bites'] = daily_df['week_key'].map(weekly_mapping)

    # Удаляем временные колонки
    daily_df = daily_df.drop(['year', 'week_num', 'week_key'], axis=1)

    # Сохраняем результат
    daily_df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"Обработано {len(daily_df)} ежедневных записей")
    print(f"Найдено совпадений: {daily_df['weekly_bites'].notna().sum()}")
    print(f"Не найдено: {daily_df['weekly_bites'].isna().sum()}")

    return daily_df


# Пример использования
if __name__ == "__main__":
    # Пути к файлам
    weekly_pred_file = "long_model/weekly_train_april_LONG_pred.csv"
    daily_input_file = "new-train-april_SHORT.csv"  # файл с ежедневными данными
    daily_output_file = "new-train-april_SHORT_week.csv"

    # Используем второй вариант (по calendar_week) - он надежнее
    result_df = add_weekly_bites_by_calendar_week(
        weekly_pred_file,
        daily_input_file,
        daily_output_file
    )

    # Показываем пример результата
    print("\nПример результата:")
    print(result_df.head(10).to_string())

    # Проверка для конкретного кластера
    print("\nПроверка для cluster_id=322254:")
    sample = result_df[result_df['cluster_id'] == 322254].head(10)
    print(sample[['date', 'cluster_id', 'amount_of_bites', 'weekly_bites']].to_string())