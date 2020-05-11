from sklearn.utils import _get_column_indices, _safe_indexing
from sklearn.inspection._partial_dependence import _grid_from_X

import numpy as np
import matplotlib.pyplot as plt

from .base import BaseInterpretability


# NOTE inspired from https://github.com/scikit-learn/scikit-learn/blob/b194674c4/sklearn/inspection/_partial_dependence.py#L180
class PdpInterpretability(BaseInterpretability):
    def _grid(self, X, features, percentiles, grid_resolution):
        features_indices = np.asarray(
            _get_column_indices(X, features), dtype=np.int32, order='C'
        ).ravel()

        grid, values = _grid_from_X(
            _safe_indexing(X, features_indices, axis=1), percentiles,
            grid_resolution
        )

        return grid, values, features_indices

    def _X_batch(self, X, features_indices, grid):
        X_batch = []

        for new_values in grid:
            X_eval = X.copy()

            for i, feature_index in enumerate(features_indices):
                if hasattr(X_eval, 'iloc'):
                    X_eval.iloc[:, feature_index] = new_values[i]
                else:
                    X_eval[:, feature_index] = new_values[i]

            X_batch.append(X_eval)

        return X_batch

    def _averaged_predict_batch(self, X_batch, model, one_api_call=True):
        # NOTE one_api_call is faster but cost more memory for the customer
        averaged_predictions = []

        if one_api_call:
            batches_len = []
            for batch in X_batch:
                batches_len.append(len(batch))

            json = {}

            if model.number_of_inputs > 1:
                for input_name in model.input_names:
                    json[input_name] = [[batch[input_name].values.tolist()] for batch in X_batch]
            else:
                json[model.input_names[0]] = [batch.values.tolist() for batch in X_batch]

            raw_predictions = model.estimate(json=json)
            predictions = raw_predictions[model.output_name]

            start = 0
            for batch_len in batches_len:
                end = start + batch_len
                predictions_index = np.array(predictions[start:end])
                averaged_predictions.append(np.mean(predictions_index, axis=0))
                start = end
        else:
            for batch in X_batch:
                json = {}

                if model.number_of_inputs > 1:
                    for input_name in model.input_names:
                        json[input_name] = [[batch[input_name].values.tolist()]]
                else:
                    json[model.input_names[0]] = batch.values.tolist()

                raw_predictions = model.estimate(json=json)
                predictions = np.array(raw_predictions[model.output_name])
                averaged_predictions.append(np.mean(predictions, axis=0))

        return averaged_predictions

    def interpret(self, model, X, features, percentiles=(0.05, 0.95), grid_resolution=100, one_api_call=True):  # pylint: disable=arguments-differ
        grid, values, features_indices = self._grid(X, features, percentiles, grid_resolution)

        X_batch = self._X_batch(X, features_indices, grid)

        averaged_predictions = self._averaged_predict_batch(X_batch=X_batch, model=model, one_api_call=one_api_call)

        averaged_predictions = np.array(averaged_predictions).T

        averaged_predictions = averaged_predictions.reshape(
            -1, *[val.shape[0] for val in values])

        # NOTE it is possible that some treatment are required depending of the type of model (binary classifier, regressor, ...)
        # in this case, take a look on https://github.com/scikit-learn/scikit-learn/blob/b194674c4/sklearn/inspection/_partial_dependence.py#L168

        return averaged_predictions, values

    @staticmethod
    def plot(main_effects, features, averaged_predictions_per_feature, grid_values_per_feature, labels, output_file=None, feature_names=None, label_names=None):  # pylint: disable=too-many-locals
        if not main_effects:
            raise NotImplementedError

        f, axarr = plt.subplots(len(features), 1)

        for index, feature in enumerate(features):

            ax = axarr
            if len(features) > 1:
                ax = axarr[index]

            X = grid_values_per_feature[feature][0]

            for label in labels:
                label_name = label

                if label_names:
                    label_name = label_names[label]

                ax.plot(X, averaged_predictions_per_feature[feature][label], marker=None, alpha=0.7, label=label_name, markersize=1, linewidth=.5)

            feature_name = feature

            if feature_names:
                feature_name = feature_names[feature]

            ax.set_xlabel("Value for feature {}".format(feature_name))
            ax.set_ylabel("PDP")

        handles, labels = ax.get_legend_handles_labels()
        f.legend(handles, labels, loc='lower right')

        f.tight_layout()

        if output_file:
            f.savefig(output_file, dpi=300)
            return

        plt.show()
