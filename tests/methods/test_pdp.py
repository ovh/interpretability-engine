import pytest
from unittest.mock import Mock, MagicMock
import pickle

import numpy as np
import pandas as pd

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import partial_dependence

from interpretability_engine.methods.pdp import PdpInterpretability


class TestPdpInterpretability():
    def setup(self):
        self.pdp = PdpInterpretability()

    def test_grid(self):
        iris = load_iris()
        X, y = iris.data, iris.target
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

        pdp = PdpInterpretability()

        features = [0, 1]

        grid, values, _ = self.pdp._grid(X, features=features, percentiles=(0.05, 0.95), grid_resolution=100)

        assert len(grid[0]) == len(features)

        assert min(grid[:, 0]) == 4.3
        assert max(grid[:, 0]) == 7.9

        assert len(values[0]) == len(np.unique(X[:, 0]))
        assert len(values[1]) == len(np.unique(X[:, 1]))

        grid, values, _ = self.pdp._grid(X, features=[0], percentiles=(0.05, 0.95), grid_resolution=10)

        assert len(values[0]) == 10

    def test_interpret(self):
        iris = load_iris()
        X, y = iris.data, iris.target

        df = pd.DataFrame(iris.data, columns=['sepal length', 'sepal width', 'petal length', 'petal width'])
        df['species'] = iris.target

        X = df.drop(columns=['species'])
        y = df['species']

        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

        classifier = RandomForestClassifier(random_state=42)
        classifier.fit(X_train, y_train)

        grid_resolution = 100

        pdp, axes = partial_dependence(classifier, X, [0], response_method='predict_proba',
                           percentiles=(0.05, 0.95), grid_resolution=grid_resolution,
                           method='brute')

        # ensure original pdp implemtend by scikit learn works as expected
        assert pytest.approx(pdp[0][0]) == 0.34126667
        assert pytest.approx(pdp[0][-1]) == 0.29406667

        # load predictions that have been saved from the exact model trained above and run through serving engine v1.0.2
        predictions = pickle.load(open("./misc/predictions.pickle", "rb"))

        # simulate the responses from serving engine
        model = MagicMock()
        model.output_name = 'output_probability'
        model.number_of_inputs = 1

        model.input_names.return_value = [[0] * grid_resolution] # input_names index (which is only 0 when exported with scikit) * number of times input_names will be called

        flatten = lambda l: [item for sublist in l for item in sublist]

        # Try with one api call
        model.estimate = Mock(side_effect=[{'output_probability': flatten(predictions)}])

        sim_pdp, sim_axes = self.pdp.interpret(model=model, X=X, features=[0], percentiles=(0.05, 0.95), grid_resolution=100, one_api_call=True)

        # check that pdp values computed from predictions of serving engine matches scikit's pdp implementation
        assert pdp[0][0] == sim_pdp[0][0]
        assert (pdp == sim_pdp).all()

        assert (axes[0] == sim_axes[0]).all()

        # Try with multiple api calls
        model.estimate = Mock(side_effect=[{'output_probability': predictions[i]} for i in range(len(predictions))])

        sim_pdp, sim_axes = self.pdp.interpret(model=model, X=X, features=[0], percentiles=(0.05, 0.95), grid_resolution=100, one_api_call=False)

        # check that pdp values computed from predictions of serving engine matches scikit's pdp implementation
        assert pdp[0][0] == sim_pdp[0][0]
        assert (pdp == sim_pdp).all()

        assert (axes[0] == sim_axes[0]).all()
