from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
import sklearn
import pandas


class Model:
    def __init__(self, model_type: str = "DecisionTreeRegressor"):
        if model_type == "DecisionTreeRegressor":
            self.model = DecisionTreeRegressor()
        elif model_type == "RandomForestRegressor":
            self.model = RandomForestRegressor()
        else:
            raise ValueError("model_type is not valid")

    def get_df_from_logfile(self, logfile: str) -> pandas.DataFrame:
        return pandas.read_csv(logfile)

    def train(self, logfile: str):
        df = self.get_df_from_logfile(logfile)
        self.model = sklearn.base.clone(self.model)
        self.model.fit(df.drop(["word", "res"], axis=1), df["res"])
        return self.model

    def score(self, data) -> float:
        return self.model.predict(data.drop(["word"], axis=1))
