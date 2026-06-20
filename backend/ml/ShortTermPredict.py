import numpy as np
import pandas as pd
import xgboost as xgb
from matplotlib import pyplot as plt
from sklearn.metrics import mean_absolute_error
CLUSTER_CONSTANTS = {

    322250: {
        "popularity_score": 0.75,
        "popularity_category": 4,
        "overall_mean": 21.0,
        "overall_max": 86,
        "peak_season_start": 18,
        "peak_season_end": 26,
        "is_growing": 1
    },
    322251: {
        'popularity_score': 0.55,
        'popularity_category': 2,
        'overall_mean': 11.80,
        'overall_max': 54,
        'peak_season_start': 17,
        'peak_season_end': 28,
        'is_growing': -1,
    },
    322252: {
        'popularity_score': 0.75,
        'popularity_category': 4,
        'overall_mean': 17.90,
        'overall_max': 74,
        'peak_season_start': 18,
        'peak_season_end': 26,
        'is_growing': 1,
    },
    322254: {
        'popularity_score': 0.35,
        'popularity_category': 1,
        'overall_mean': 3.00,
        'overall_max': 8,
        'peak_season_start': 19,
        'peak_season_end': 26,
        'is_growing': 1,
    },
    322255: {
        'popularity_score': 0.65,
        'popularity_category': 3,
        'overall_mean': 16.90,
        'overall_max': 81,
        'peak_season_start': 16,
        'peak_season_end': 28,
        'is_growing': 1,
    },
    322257: {
        'popularity_score': 0.65,
        'popularity_category': 3,
        'overall_mean': 14.10,
        'overall_max': 47,
        'peak_season_start': 18,
        'peak_season_end': 27,
        'is_growing': 1,
    },
}

class ShortTermPredict:

    def __add_cluster_popularity(self, df):
        for col, default in [
            ('popularity_score', 0.3),
            ('popularity_category', 2),
            ('overall_mean', 5),
            ('overall_max', 15),
            ('peak_season_start', 20),
            ('peak_season_end', 25),
            ('is_growing', 0),
        ]:
            df[col] = df['cluster_id'].map(
                lambda x, c=col, d=default: CLUSTER_CONSTANTS.get(x, {}).get(c, d)
            )
        df['week_num'] = pd.to_datetime(df['date']).dt.isocalendar().week
        df['is_peak_season'] = (
            (df['week_num'] >= df['peak_season_start']) &
            (df['week_num'] <= df['peak_season_end'])
        ).astype(int)


        return df

    def __is_holiday(self,df, date_column = 'date'):
        """Добавляет признак is_holiday (1 если праздник/каникулы, иначе 0)"""
        df[date_column] = pd.to_datetime(df[date_column])
        holidays = ["2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05", "2023-01-06", "2023-02-23", "2023-02-24",
                   "2023-03-08", "2023-05-01", "2023-05-08", "2023-05-09", "2023-06-12", "2023-11-06",
                   "2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04",
                   "2024-01-05", "2024-01-08", "2024-02-23", "2024-03-08", "2024-04-29", "2024-04-30", "2024-05-01",
                   "2024-05-09", "2024-05-10", "2024-06-12", "2024-11-04", "2024-12-30", "2024-12-31",
                   "2025-01-01",  "2025-01-02",  "2025-01-03",  "2025-01-06",  "2025-01-07",  "2025-01-08",  "2025-05-01",  "2025-05-02",
                   "2025-05-08",  "2025-05-09",  "2025-01-01",  "2025-06-12",  "2025-06-13", "2025-11-03", "2025-11-04", "2025-12-31",
                   "2026-01-01", "2026-01-02", "2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08", "2026-01-09", "2026-02-23", "2026-03-09",
                   "2026-05-01", "2026-05-11", "2026-06-12", "2026-11-04", "2026-12-31"
                   ]
        holidays_dt = pd.to_datetime(holidays)

        is_holiday_mask = df[date_column].isin(holidays_dt)

        df['is_holiday'] = is_holiday_mask.astype(int)

        return df

    def __sort_by_date(self, df, date_column='date'):
        """Сортировка датафрейма по колонке с датой"""
        df[date_column] = pd.to_datetime(df[date_column])
        df = df.sort_values(by=date_column).reset_index(drop=True)
        return df

    def __transformation_days(self, df):
        """Трансформации для дневных данных"""
        df['date'] = pd.to_datetime(df['date'])
        df['dayofyear'] = df['date'].dt.dayofyear
        df['sin_day'] = np.sin(2 * np.pi * df['dayofyear'] / 365)
        df['cos_day'] = np.cos(2 * np.pi * df['dayofyear'] / 365)
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek

        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        return df

    def __find_lags(self, df):
        """Добавляет лаги и скользящие средние"""

        # Лаги для температуры
        df['temperature_lag1'] = df['temperature'].shift(1)
        df['temperature_lag2'] = df['temperature'].shift(2)
        df['temperature_lag3'] = df['temperature'].shift(3)
        df['temperature_lag7'] = df['temperature'].shift(7)

        # Лаги для осадков
        df['precipitation_lag1'] = df['precipitation'].shift(1)
        df['precipitation_lag2'] = df['precipitation'].shift(2)
        df['precipitation_lag3'] = df['precipitation'].shift(3)
        df['precipitation_lag7'] = df['precipitation'].shift(7)

        # Лаги для облачности
        df['cloudiness_lag1'] = df['cloudiness'].shift(1)
        df['cloudiness_lag2'] = df['cloudiness'].shift(2)
        df['cloudiness_lag3'] = df['cloudiness'].shift(3)
        df['cloudiness_lag7'] = df['cloudiness'].shift(7)


        # Скользящие средние для температуры
        df['temperature_ma3'] = df['temperature'].rolling(3).mean()
        df['temperature_ma7'] = df['temperature'].rolling(7).mean()

        # Скользящие средние для осадков
        df['precipitation_ma3'] = df['precipitation'].rolling(3).mean()
        df['precipitation_ma7'] = df['precipitation'].rolling(7).mean()

        # Скользящие средние для облачности
        df['cloudiness_ma3'] = df['cloudiness'].rolling(3).mean()
        df['cloudiness_ma7'] = df['cloudiness'].rolling(7).mean()

        return df

    def __days_since_season_start(self, df):
        """Добавляет количество дней с начала сезона"""
        if 'season_start_date' in df.columns:
            df['season_start_date'] = pd.to_datetime(df['season_start_date'], errors='coerce')

            def calc_days(row):
                if pd.isna(row['season_start_date']):
                    return np.nan
                days = (row['date'] - row['season_start_date']).days
                return days if days >= 0 else np.nan

            df['days_since_season_start'] = df.apply(calc_days, axis=1)
        else:
            df['days_since_season_start'] = 0

        return df



    def __init__(self, file_path, sep=","):
        """Инициализация и предобработка данных"""
        self.df = pd.read_csv(file_path, sep=sep, encoding="utf-8")
        self.df = self.__sort_by_date(self.df)
        self.df = self.__transformation_days(self.df)
        self.df = self.__find_lags(self.df)
        self.df = self.__days_since_season_start(self.df)
        self.df = self.__is_holiday(self.df)
        self.df = self.__add_cluster_popularity(self.df)
        self.df = self.df.dropna()

    # КЛАСС XGB ДЛЯ КРАТКОСРОЧНОЙ МОДЕЛИ
    class XGBShortTerm:
        GLOBAL_SEED = 42

        features = [
            'sin_day',
            'cos_day',
            'month',
            'day_of_week',
            'dayofyear',
            'elevation',
            'avg_snow_depth',
            'temperature',
            'precipitation',
            'cloudiness',
            'is_weekend',
            'is_holiday',
            'week_num',
            'popularity_score',
            'popularity_category',
            'overall_mean',
            'overall_max',
            'is_growing',
            'is_peak_season',
            'days_since_season_start',
            'temperature_lag1', 'temperature_lag2', 'temperature_lag3', 'temperature_lag7',
            'temperature_ma3', 'temperature_ma7',
            'precipitation_lag1', 'precipitation_lag2', 'precipitation_lag3', 'precipitation_lag7',
            'precipitation_ma3', 'precipitation_ma7',
            'cloudiness_lag1', 'cloudiness_lag2', 'cloudiness_lag3', 'cloudiness_lag7',
            'cloudiness_ma3', 'cloudiness_ma7',
            'weekly_bites'
        ]

        target = 'amount_of_bites'

        @classmethod
        def _make_model(cls, seed):
            """Создание модели XGBoost"""
            return xgb.XGBRegressor(
                n_estimators=1000,
                max_depth=4,
                learning_rate=0.03,
                subsample=0.7,
                colsample_bytree=0.8,
                min_child_weight=5,
                reg_alpha=0.1,
                reg_lambda=0.9,
                random_state=seed,
                early_stopping_rounds=30,
                eval_metric='mae',
                enable_categorical=True,
                objective='reg:pseudohubererror'
            )

        @classmethod
        def train_model(cls, df_train, seed=GLOBAL_SEED):
            """Обучение модели XGBoost"""
            df = df_train.copy().sort_values('date').reset_index(drop=True)

            df['target_ratio'] = df[cls.target] / df['overall_max'].clip(lower=1)

            n = len(df)
            train_end = int(n * 0.80)

            X_train = df[cls.features].iloc[:train_end]
            y_train = df['target_ratio'].iloc[:train_end]

            X_val = df[cls.features].iloc[train_end:]
            y_val = df['target_ratio'].iloc[train_end:]
            overall_max_val = df['overall_max'].iloc[train_end:].values

            # Обработка пропусков
            X_train = X_train.fillna(0)
            X_val = X_val.fillna(0)


            model = cls._make_model(seed)
            target_train = df[cls.target].iloc[:train_end].values
            sample_weights = np.ones_like(target_train, dtype=float)

            # Веса для разных диапазонов
            sample_weights[target_train >= 17] = 20.0
            sample_weights[(target_train >= 10) & (target_train < 17)] = 2.0
            sample_weights[(target_train >= 5) & (target_train < 10)] = 1.0

            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                sample_weight=sample_weights,
                verbose=False
            )

            # Предсказания
            y_pred_ratio = model.predict(X_val)
            y_pred_ratio = np.clip(y_pred_ratio, 0, 1)
            y_pred = np.round(y_pred_ratio * overall_max_val).astype(int)
            y_pred = np.maximum(1, y_pred)
            y_true = df[cls.target].iloc[train_end:].values

            # Метрики
            mae = mean_absolute_error(y_true, y_pred)
            accuracy = np.mean(y_pred == y_true)

            print(f"Строк в train: {train_end}, в val: {n - train_end}")
            print(f"MAE: {mae:.2f}")
            print(f"Accuracy: {accuracy:.2%}")

            tolerance = 3
            within_tolerance = np.mean(np.abs(y_pred - y_true) <= tolerance)
            print(f"Accuracy ±{tolerance}: {within_tolerance:.2%}")


            return y_true, y_pred, model

        @classmethod
        def fit_model(cls, df_test, model, save_to_file=None):

            df = df_test.copy()

            X = df[cls.features]
            overall_max = df['overall_max'].values

            pred_ratio = model.predict(X)
            pred_ratio = np.clip(pred_ratio, 0, 1)
            preds = np.round(pred_ratio * overall_max).astype(int)
            preds = np.maximum(1, preds)
            if save_to_file:
                import os
                # Определяем исходные колонки для сохранения
                original_columns = [
                    'date', 'cluster_id', 'elevation', 'avg_snow_depth',
                    'temperature', 'precipitation', 'cloudiness',
                    'season_start_date', 'amount_of_bites'
                ]
                os.makedirs('../short_model', exist_ok=True)
                save_path = os.path.join('../short_model', save_to_file)
                # Проверяем, какие колонки действительно существуют
                existing_columns = [col for col in original_columns if col in df.columns]

                # Создаем датафрейм с предсказаниями
                result_df = df[existing_columns].copy()
                result_df['predicted_bites'] = preds

                # Сохраняем
                result_df.to_csv(save_path, index=False, encoding="utf-8")
                return preds, result_df

            return preds, df

        @classmethod
        def save_model(cls, model, filepath):
            """Сохраняет модель и её профиль"""
            import pickle
            import os
            os.makedirs('../short_model', exist_ok=True)
            full_path = os.path.join('../short_model', filepath)
            with open(full_path + '_features.pkl', 'wb') as f:
                pickle.dump(cls.features, f)
            # XGBoost модель
            model.save_model(full_path + '.json')

        @classmethod
        def load_model(cls, filepath):
            """Загружает модель и список признаков"""
            import pickle
            import os

            full_path = os.path.join('../short_model', filepath)

            # Загружаем модель
            model = cls._make_model(cls.GLOBAL_SEED)
            model.load_model(full_path + '.json')

            # Загружаем признаки
            features_path = full_path + '_features.pkl'
            if os.path.exists(features_path):
                with open(features_path, 'rb') as f:
                    model.used_features_ = pickle.load(f)
            else:
                print(f"Предупреждение: {features_path} не найден, используется cls.features")
                model.used_features_ = cls.features

            return model


# ПРИМЕР ИСПОЛЬЗОВАНИЯ

# Загрузка и предобработка данных
processor_ap = ShortTermPredict("../new-train-april_SHORT_week.csv")
df_ap = processor_ap.df

processor_ap_test = ShortTermPredict("../new-test-april_SHORT_week.csv")
df_ap_test = processor_ap_test.df

processor_may = ShortTermPredict("../new-train-may_SHORT_week.csv")
df_may = processor_may.df

processor_may_test = ShortTermPredict("../new-test-may_SHORT_week.csv")
df_may_test = processor_may_test.df

# Обучение моделей
y_true_ap, y_pred_ap, model_ap = ShortTermPredict.XGBShortTerm.train_model(
    df_ap
)
# Сохраняем модель
ShortTermPredict.XGBShortTerm.save_model(model_ap, "xgb_april_short_model")


y_true_may, y_pred_may, model_may = ShortTermPredict.XGBShortTerm.train_model(
    df_may,
)

# Сохраняем модель
ShortTermPredict.XGBShortTerm.save_model(model_may, "xgb_may_short_model")



# Прогнозирование на тестовых данных
# model_ap = ShortTermPredict.XGBShortTerm.load_model("xgb_may_short_model")

predictions_ap_test, result_df_ap = ShortTermPredict.XGBShortTerm.fit_model(
    df_ap_test, model_ap, save_to_file="predictions_april_test.csv"
)



predictions_may_test, result_df_may = ShortTermPredict.XGBShortTerm.fit_model(
    df_may_test, model_may,
    save_to_file="predictions_may_test.csv"
)









