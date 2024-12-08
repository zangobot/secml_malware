import os
from pathlib import Path

import magic
from secml.array import CArray

from secml_malware.attack.blackbox.c_black_box_padding_evasion import CBlackBoxPaddingEvasionProblem
from secml_malware.attack.blackbox.c_wrapper_phi import CEnd2EndWrapperPhi
from secml_malware.attack.blackbox.ga.c_base_genetic_engine import CGeneticAlgorithm
from secml_malware.attack.whitebox.c_header_evasion import CHeaderEvasion
from secml_malware.models import End2EndModel
from secml_malware.models.c_classifier_end2end_malware import CClassifierEnd2EndMalware
from secml_malware.models.malconv2mb import MalConv2MB

malconv = MalConv2MB()  # CNN trained on RAW BYTES
malconv = CClassifierEnd2EndMalware(malconv, input_shape=(1, 2000000))
malconv.load_pretrained_model()

folder = str(Path(__file__).parent / "../secml_malware/data/malware_samples/test_folder")
X = []
y = []
file_names = []
for i, f in enumerate(os.listdir(folder)):
    path = os.path.join(folder, f)
    if 'petya' not in path:
        continue
    if "PE32" not in magic.from_file(path):
        continue
    with open(path, "rb") as file_handle:
        code = file_handle.read()
    x = End2EndModel.bytes_to_numpy(
        code, malconv.get_input_max_length(), malconv.get_embedding_value(),
        malconv.get_is_shifting_values()
    )
    pred, confidence = malconv.predict(CArray(x), True)
    print(pred)
    if confidence[0, 1].item() < 0.5:
        continue

    print(f"> Added {f} with confidence {confidence[0, 1].item()}")
    X.append(x)
    conf = confidence[1][0].item()
    y.append([1 - conf, conf])
    file_names.append(path)

partial_pdos_attack = CHeaderEvasion(malconv, random_init=False, iterations=10, optimize_all_dos=True,
                                     threshold=0.0)
partial_pdos_attack.run(CArray(X[0]), CArray([1]))
print(partial_pdos_attack.confidences_)
grad = partial_pdos_attack.loss_function_gradient(CArray(X[0]).atleast_2d(), CArray(X[0]).atleast_2d(), 0)
print(grad[0, partial_pdos_attack.indexes_to_perturb, :].norm(dim=1))

wrapper = CEnd2EndWrapperPhi(malconv)
ga = CGeneticAlgorithm(
    CBlackBoxPaddingEvasionProblem(wrapper, iterations=1, how_many_padding_bytes=100, population_size=3))
ga.run(CArray(X[0]), CArray([1]))
print(ga.confidences_)
