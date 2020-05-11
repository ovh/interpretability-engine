import logging
import tempfile

import pandas as pd
from swiftclient.service import SwiftService, SwiftError


def swift_download_samples(container, object):  # pylint: disable=redefined-builtin
    output_directory = tempfile.mkdtemp()

    with SwiftService() as swift:
        try:
            for down_res in swift.download(container=container,
                                           objects=[object],
                                           options={'out_directory': output_directory}):

                if down_res['success']:
                    logging.debug("'%s' downloaded", down_res['object'])
                else:
                    logging.debug("'%s' download failed", down_res['object'])
                    raise Exception("Object {}/{} no found".format(container, object))

                logging.debug(down_res)

                return down_res['path']
        except SwiftError as e:
            logging.error(e.value)


def load_samples(samples_path, swift_container, swift_object):
    if not samples_path:
        logging.info('retrieve the samples from swift')
        samples_path = swift_download_samples(swift_container, swift_object)

    logging.info("load %s sample in dataframe and convert to numpy", samples_path)

    df = pd.read_csv(samples_path)

    return df
