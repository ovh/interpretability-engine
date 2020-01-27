import logging

from .routes import Routes
from .model import Model
from .methods import pdp


class InterpretabilityEngine():
    def __init__(self, token, url_deployment, verify=True):
        self.routes = Routes(token=token, url_deployment=url_deployment, verify=verify)
        self.model = Model(self.routes)

    def interpret(self, method, X, features, main_effects=True, plot=False, output_file=None, feature_names=None, label_names=None):
        if features is None or len(features) == 0:
            logging.warning("No features has been specified, try to find the 3 most important features automatically (computationally expensive)")
            # NOTE can use something like https://scikit-learn.org/stable/modules/generated/sklearn.inspection.permutation_importance.html#sklearn.inspection.permutation_importance
            raise NotImplementedError

        self.model.check_input(X=X, features=features)

        logging.info("Interpret the model with the method %s", method)

        if method == 'pdp':
            interpreter = pdp.PdpInterpretability()
            if main_effects:
                averaged_predictions_per_feature = {}
                grid_values_per_feature = {}

                for feature in features:
                    averaged_predictions, grid_values = interpreter.interpret(self.model, X, [feature])
                    averaged_predictions_per_feature[feature] = averaged_predictions
                    grid_values_per_feature[feature] = grid_values
            elif not main_effects and len(features) <= 2:  # TODO add int tests
                averaged_predictions, grid_values = interpreter.interpret(self.model, X, [feature])
            else:
                raise Exception("Do not handle more than 2 features when computing the interaction")

            if plot:
                pdp.PdpInterpretability.plot(main_effects=main_effects,
                                             features=features,
                                             averaged_predictions_per_feature=averaged_predictions_per_feature,
                                             grid_values_per_feature=grid_values_per_feature,
                                             labels=self.model.labels,
                                             output_file=output_file,
                                             feature_names=feature_names,
                                             label_names=label_names)
        else:
            raise Exception("Unkown interpretability method {}".format(method))
