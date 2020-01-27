import logging

import requests


class Routes():
    def __init__(self, token, url_deployment, verify=True):
        self.url_deployment = url_deployment
        self.headers = {'Authorization': 'Bearer {}'.format(token)}
        self.verify = verify

    @property
    def _requests_params(self):
        return {'headers': self.headers, 'verify': self.verify}

    @staticmethod
    def _check_response(response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logging.error(response.text)
            raise err

    @staticmethod
    def get_url_deployment_model(token, url_serving, model_id, verify):
        response = requests.get('{}/model/{}'.format(url_serving, model_id), headers={'Authorization': 'Bearer {}'.format(token)}, verify=verify)
        Routes._check_response(response)
        return response.json()

    def describe_model(self, url_deployment=None):
        if not url_deployment:
            url_deployment = self.url_deployment

        response = requests.get('{}/describe'.format(url_deployment), **self._requests_params)
        Routes._check_response(response)
        return response.json()

    def predict(self, json, url_deployment=None):
        if not url_deployment:
            url_deployment = self.url_deployment

        response = requests.post('{}/eval'.format(url_deployment), json=json, **self._requests_params)
        Routes._check_response(response)
        return response.json()
