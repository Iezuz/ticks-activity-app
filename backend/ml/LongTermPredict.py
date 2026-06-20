import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
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


class LongTermPredict:
    def __add_cluster_popularity(self, df):
        for col, default in [
            ('popularity_score', 0.3),
            ('popularity_category', 2),
            ('overall_mean', 10),
            ('overall_max', 30),
            ('peak_season_start', 20),
            ('peak_season_end', 25),
            ('is_growing', 0),
        ]:
            df[col] = df['cluster_id'].map(
                lambda x, c=col, d=default: CLUSTER_CONSTANTS.get(x, {}).get(c, d)
            )

        df['is_peak_season'] = (
            (df['week_num'] >= df['peak_season_start']) &
            (df['week_num'] <= df['peak_season_end'])
        ).astype(int)

        # Разница начала сезона и стартовой/конечной датой недели
        df['weeks_to_peak_start'] = (df['peak_season_start'] - df['week_num']).clip(lower=0)
        df['weeks_since_peak_start'] = (df['week_num'] - df['peak_season_start']).clip(lower=0)
        df['weeks_to_peak_end'] = (df['peak_season_end'] - df['week_num']).clip(lower=0)

        return df

    def __sort_by_date(self, df, date_column='week_date_range'):
        df['start_date'] = pd.to_datetime(df[date_column].str.split(' - ').str[0])
        df = df.sort_values(by='start_date').reset_index(drop=True)
        df = df.drop('start_date', axis=1)
        return df

    def __transformation_weekly(self, df):
        df['year'] = df['calendar_week'].str.split('-W').str[0].astype(int)
        df['week_num'] = df['calendar_week'].str.split('-W').str[1].astype(int)

        df['sin_week'] = np.sin(2 * np.pi * df['week_num'] / 52)
        df['cos_week'] = np.cos(2 * np.pi * df['week_num'] / 52)

        df['week_start_date'] = pd.to_datetime(df['week_date_range'].str.split(' - ').str[0])
        df['week_end_date'] = pd.to_datetime(df['week_date_range'].str.split(' - ').str[1])

        df['season_start_date'] = pd.to_datetime(df['season_start_date'], errors='coerce')
        df['days_since_season_start'] = (df['week_start_date'] - df['season_start_date']).dt.days
        df['days_since_season_start'] = df['days_since_season_start'].clip(lower=0)
        df['days_since_season_end'] = (df['week_end_date'] - df['season_start_date']).dt.days
        df['days_since_season_end'] = df['days_since_season_end'].clip(lower=0)

        return df

    def __add_seasonal_profile(self, df):
        """
        Средний профиль укусов по (cluster_id, week_num) нормализованный на overall_max.
        Это даёт модели информацию о форме сезона без абсолютных значений.
        """
        if 'total_bites' in df.columns:
            profile = (
                df.groupby(['cluster_id', 'week_num'])['total_bites']
                .mean()
                .reset_index()
                .rename(columns={'total_bites': 'week_cluster_mean'})
            )
            df = df.merge(profile, on=['cluster_id', 'week_num'], how='left')

            df['week_profile_ratio'] = df['week_cluster_mean'] / df['overall_max'].clip(lower=1)
        else:
            df['week_profile_ratio'] = np.nan

        return df

    def __init__(self, file_path, sep=","):
        self.df = pd.read_csv(file_path, sep=sep, encoding="utf-8")
        self.df = self.__sort_by_date(self.df)
        self.df = self.__transformation_weekly(self.df)
        self.df = self.__add_cluster_popularity(self.df)
        self.df = self.__add_seasonal_profile(self.df)
        self.df['cluster_id'] = self.df['cluster_id'].astype('category')

    class XGBLongTerm:
        GLOBAL_SEED = 42
        features = [
            'sin_week',
            'cos_week',
            'elevation',
            'avg_snow_depth',
            'week_num',
            'year',
            'days_since_season_start',
            'days_since_season_end',
            'popularity_score',
            'popularity_category',
            'overall_mean',
            'overall_max',
            'is_growing',
            'is_peak_season',
            'weeks_to_peak_start',
            'weeks_since_peak_start',
            'weeks_to_peak_end',
            'week_profile_ratio',
            'cluster_id',
        ]
        target = 'total_bites'

        @classmethod
        def _make_model(cls, seed):
            return xgb.XGBRegressor(
                n_estimators=1000,
                max_depth=3,
                learning_rate=0.8,
                subsample=0.8,
                colsample_bytree=0.8,
                min_child_weight=2,
                reg_alpha=0.08,
                reg_lambda=0.9,
                random_state=seed,
                early_stopping_rounds=40,
                eval_metric='mae',
                enable_categorical=True,
                objective='reg:pseudohubererror',
            )

        @classmethod
        def train_model(cls, df_train, seed=GLOBAL_SEED):

            df = df_train.copy().sort_values('week_start_date').reset_index(drop=True)

            df['target_ratio'] = df[cls.target] / df['overall_max'].clip(lower=1)

            # Разбивка по времени
            n = len(df)
            train_end = int(n * 0.80)

            X_train = df[cls.features].iloc[:train_end]
            y_train = df['target_ratio'].iloc[:train_end]

            X_val = df[cls.features].iloc[train_end:]
            y_val = df['target_ratio'].iloc[train_end:]
            overall_max_val = df['overall_max'].iloc[train_end:].values

            model = cls._make_model(seed)
            target_train = df[cls.target].iloc[:train_end].values
            sample_weights = np.ones_like(target_train, dtype=float)

            # Веса для разных диапазонов
            sample_weights[target_train >= 65] = 5.0
            sample_weights[(target_train >= 55) & (target_train < 65)] = 3.0
            sample_weights[(target_train >= 40) & (target_train < 55)] = 2.0


            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                sample_weight=sample_weights,
                verbose=False
            )

            # Предсказываем ratio и конвертируем обратно
            y_pred_ratio = model.predict(X_val)
            y_pred_ratio = np.clip(y_pred_ratio, 0, 1)
            y_pred = np.round(y_pred_ratio * overall_max_val).astype(int)
            y_pred = np.maximum(1, y_pred)
            y_true = df[cls.target].iloc[train_end:].values

            #Сохранение сезонного профиля в модель
            profile = df_train.groupby(['cluster_id', 'week_num'])['week_profile_ratio'].first().to_dict()
            model.seasonal_profile_ = profile

            return y_true, y_pred, model

        @classmethod
        def fit_model(cls, df, model,  save_to_file=None):
            """
            метод для предсказания
            """

            df = df.copy()

            # Для тестовых недель которых нет в train_df — заполняем профиль ratio кластера из train
            if 'week_profile_ratio' not in df.columns or df['week_profile_ratio'].isna().any():
                df['week_profile_ratio'] = df.apply(
                    lambda row: model.seasonal_profile_.get((row['cluster_id'], row['week_num']), 0.3),
                    axis=1
                )

            X = df[cls.features]
            overall_max = df['overall_max'].values

            pred_ratio = model.predict(X)
            pred_ratio = np.clip(pred_ratio, 0, 1)
            preds = np.round(pred_ratio * overall_max).astype(int)
            preds = np.maximum(1, preds)
            if save_to_file:
                import os
                # Определяем исходные колонки, которые были в датасете
                original_columns = [
                    'cluster_id', 'year', 'week_num', 'week_date_range',
                    'calendar_week', 'elevation', 'avg_snow_depth',
                    'season_start_date', 'total_bites', 'mean_bites_for_year'
                ]
                os.makedirs('../long_model', exist_ok=True)
                save_path = os.path.join('../long_model', save_to_file)
                # Проверяем, какие колонки действительно существуют
                existing_columns = [col for col in original_columns if col in df.columns]

                # Создаем датафрейм только с исходными колонками и предсказаниями
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
            os.makedirs('../long_model', exist_ok=True)
            full_path = os.path.join('../long_model', filepath)
            # XGBoost модель
            model.save_model(full_path + '.json')
            # Профиль
            with open(full_path + '_profile.pkl', 'wb') as f:
                pickle.dump(model.seasonal_profile_, f)

            with open(full_path + '_features.pkl', 'wb') as f:
                pickle.dump(cls.features, f)


        @classmethod
        def load_model(cls, filepath):
            """Загружает модель и её профиль"""
            import pickle
            import os
            full_path = os.path.join('../long_model', filepath)

            model = cls._make_model(cls.GLOBAL_SEED)
            model.load_model(full_path + '.json')

            with open(full_path + '_profile.pkl', 'rb') as f:
                model.seasonal_profile_ = pickle.load(f)

            features_path = full_path + '_features.pkl'
            if os.path.exists(features_path):
                with open(features_path, 'rb') as f:
                    model.used_features_ = pickle.load(f)
            else:
                print(f"Предупреждение: {features_path} не найден, используется cls.features")
                model.used_features_ = cls.features
            return model





# ── ИСПОЛЬЗОВАНИЕ ──────────────────────────────────────────




# Апрель
processor_ap = LongTermPredict("../weekly_train_april_LONG.csv")
df_ap = processor_ap.df

y_true_ap, y_pred_ap, model_ap = LongTermPredict.XGBLongTerm.train_model(
    df_ap
)
LongTermPredict.XGBLongTerm.save_model(model_ap, "xgb_april_model")




# model_ap = LongTermPredict.XGBLongTerm.load_model("xgb_april_model")
# Тест апреля
processor_ap_test = LongTermPredict("../weekly_test_april_LONG.csv")
df_ap_test = processor_ap_test.df

predictions_ap_test, df_ap_test_with_preds  = LongTermPredict.XGBLongTerm.fit_model(
    df_ap_test, model_ap,
    save_to_file="weekly_test_april_LONG_pred.csv"
)




# Тест апреля
processor_ap_test = LongTermPredict("../weekly_train_may_LONG.csv")
df_ap_test = processor_ap_test.df

predictions_ap_test, df_ap_test_with_preds  = LongTermPredict.XGBLongTerm.fit_model(
    df_ap_test, model_ap,
    save_to_file="weekly_train_may_LONG_pred.csv"
)


# Май
processor_may = LongTermPredict("../weekly_train_may_LONG.csv")
df_may = processor_may.df
y_true_may, y_pred_may, model_may = LongTermPredict.XGBLongTerm.train_model(
    df_may
)
LongTermPredict.XGBLongTerm.save_model(model_may, "xgb_may_model")



# Тест мая
loaded_model_may = LongTermPredict.XGBLongTerm.load_model("xgb_may_model")
processor_may_test = LongTermPredict("../weekly_test_may_LONG.csv")
df_may_test = processor_may_test.df

predictions_may_test, df_may_test_with_preds  = LongTermPredict.XGBLongTerm.fit_model(
    df_may_test, model_may,
    save_to_file="weekly_test_may_LONG_pred.csv")



#Тест 2026
processor_test = LongTermPredict("../weekly_predict_long.csv")
df_test = processor_test.df

predictions_test, df_test_with_preds  = LongTermPredict.XGBLongTerm.fit_model(
    df_test, loaded_model_may,
    save_to_file="weekly_predict_long_pred.csv"
)



