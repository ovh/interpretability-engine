import logging
import sys


class Model():
    def __init__(self, routes):
        self.routes = routes
        self._model_description = self.routes.describe_model()

        self.inspect_model()

    @property
    def model_description(self):
        return self._model_description

    @property
    def number_of_inputs(self):
        return len(self.model_description['inputs'])

    @property
    def number_of_outputs(self):
        return len(self.model_description['outputs'])

    @property
    def number_of_features(self):
        return self._number_of_features

    @property
    def input_names(self):
        if self.number_of_inputs > 1:
            input_names = []

            for input_node in self.model_description['inputs']:
                if input_node['shape'][1] != 1:
                    raise Exception("Do not handle a shape different than 1 when there is a multiple inputs")
                input_names.append(input_node['name'])
            return input_names

        return [self.model_description['inputs'][0]['name']]

    @property
    def output_name(self):
        if self.number_of_outputs > 1:
            logging.warning("Number of output greater than 1, try to deduce the output_name")
            for output in self.model_description['outputs']:
                if 'probability' in output['name']:
                    logging.warning('Guessed output_name=%s', output['name'])
                    return output['name']

        return self.model_description['outputs'][0]['name']

    @property
    def labels(self):
        if self.number_of_outputs > 1:
            logging.warning("Number of output greater than 1, try to deduce the labels")
            for output in self.model_description['outputs']:
                if 'probability' in output['name']:
                    labels = range(output['shape'][1])
                    logging.warning('Label guessed from the shape %s in output named "%s": %s', output['shape'], output['name'], labels)
                    return labels

        # FIXME ensure 1 is index where name=output_probability; name can be different, depend on the guy who upload
        # labels = range(model_description['outputs'][1]['shape'][1])
        return range(self.model_description['outputs'][0]['shape'][1])

    def inspect_model(self):
        if self.number_of_inputs == 1:
            logging.debug("Only one input defined in the model, the shape of the first input is considered to deduce the number of feature")
            shape = self.model_description['inputs'][0]['shape']
            self._number_of_features = shape[1]
            logging.debug("Number of features deduced: %d", self.number_of_features)
            return

        for input_name in self.model_description['inputs']:
            # TODO ensure it works
            if input_name['shape'][1] != 1:
                logging.error("The model has multiple inputs and one of them has a shape greater than 1, we cannot handle this case to interpret")
                sys.exit(1)

        self._number_of_features = self.number_of_inputs

    def check_input(self, X, features):
        if X.shape[1] != self.number_of_features:
            logging.error("Number of features passed from the samples (%d) differs than the one for the model (%d)", X.shape[1], self.number_of_features)
            sys.exit(1)

        if self.number_of_inputs == 1:
            if len(features) > self.number_of_features:
                logging.error("There is only one input and the number of features (%d) you are asking is greater than the shape (%d)", len(features), self.number_of_features)
                sys.exit(1)

            for feature in features:
                if isinstance(feature, int) and feature >= self.number_of_features:
                    logging.error("You asking the feature %d, the serving only has %d features (0 to %d)", feature, self.number_of_features, self.number_of_features - 1)
                    sys.exit(1)

        elif len(features) > len(self.model_description['inputs']):
            logging.error("The number of features (%d) you are asking is greater than the number of inputs (%d)", len(features), len(self.model_description['inputs']))
            sys.exit(1)

    def estimate(self, json):
        return self.routes.predict(json)
