import os
from pathlib import Path

import magic
from secml.array import CArray

from secml_malware.models import End2EndModel


def load_test_data():
    folder = str(Path(__file__).parent.parent / "secml_malware" / "data" / "malware_samples" / "test_folder")
    X = []
    file_names = []
    for i, f in enumerate(os.listdir(folder)):
        path = os.path.join(folder, f)
        if "PE32" not in magic.from_file(path):
            continue
        with open(path, "rb") as file_handle:
            code = file_handle.read()
        x = End2EndModel.bytes_to_numpy(code, len(code), 256, False)
        X.append(x)
        file_names.append(path)
    maxlen = max(len(x) for x in X)
    X = [x.astype(int).tolist() + [0] * (maxlen - len(x)) for x in X]
    X = CArray(X)
    return X, file_names
