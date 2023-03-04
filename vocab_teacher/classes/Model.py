from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import sklearn
import pickle
import pandas


class Model:
    def __init__(self, model_type: str = "DecisionTreeRegressor"):
        self.model_type = model_type
        if model_type == "DecisionTreeRegressor":
            self.model = DecisionTreeRegressor(max_depth=4)
        elif model_type == "RandomForestRegressor":
            self.model = RandomForestRegressor(max_depth=2)
        else:
            raise ValueError("model_type is not valid")

    def get_df_from_logfile(self, logfile: str) -> pandas.DataFrame:
        return pandas.read_csv(logfile)

    def reduce_df_columns(
        self, df: pandas.DataFrame, history_size_to_consider: int = 1
    ) -> pandas.DataFrame:
        cols = df.columns.tolist()
        for i in range(history_size_to_consider, 5):
            cols.remove(f"rounds_last_met{i+1}")
            cols.remove(f"words_last_met{i+1}")
            cols.remove(f"time_last_met{i+1}")
            cols.remove(f"res_last_met{i+1}")

        return df[cols]

    def train(self, logfile: str, history_size_to_consider: int = 1):
        df = self.get_df_from_logfile(logfile)
        df = self.reduce_df_columns(df, history_size_to_consider)
        self.model = sklearn.base.clone(self.model)
        self.model.fit(df.drop(["word", "res"], axis=1), df["res"])
        self.save()
        return self.model

    def score(self, data, history_size_to_consider: int = 1) -> float:
        data = self.reduce_df_columns(data, history_size_to_consider)
        return self.model.predict(data.drop(["word"], axis=1))

    def save(self):
        filepath = f"../models/{self.model_type}.pmd"
        pickle.dump(self.model, open(filepath, "wb"))
        return filepath
