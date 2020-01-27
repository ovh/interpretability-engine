class BaseInterpretability():
    def interpret(self, model, X, features, *args, **kwargs):
        raise NotImplementedError
