
# readfile/v1.py

#- Imports -----------------------------------------------------------------------------------------

import h5py

from sklearn.mixture import GaussianMixture

from ...utils.debug import alert
from ...typing import (
    data_dict_t, SensorData
)


#- Read Method -------------------------------------------------------------------------------------

def read_file(f: h5py.File) -> data_dict_t:
    try:
        models_dict: data_dict_t = {}

        for name in f.keys():
            gmm_group = f[name]

            if isinstance(gmm_group, h5py.Group):
                models_dict[name] = SensorData()

                models_dict[name].threshold = float(gmm_group['threshold'][()])
                models_dict[name].n_components = int(gmm_group['n_components'][()])
                models_dict[name].random_state = int(gmm_group['random_state'][()])

                for _, model_group in gmm_group.items():
                    if not isinstance(model_group, h5py.Group):
                        continue

                    model_instance = GaussianMixture()

                    model_instance.n_component = model_group['n_components'][()]
                    model_instance.weight = model_group['weights'][()]
                    model_instance.mean = model_group['means'][()]
                    model_instance.covariance = model_group['covariances'][()]
                    model_instance.precisions_cholesk = model_group['precisions_cholesky'][()]

                    models_dict[name].models.append(model_instance)

    except Exception as e:
        alert(f"Unable to parse file. {e}")

    return models_dict

