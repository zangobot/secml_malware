from examples.utils import load_test_data
from secml_malware.models.c_classifier_remote import CClassifierRemote, AvailableOnlineAntivirus

X, names = load_test_data()
x = X[0, :]
filename = names[0]
api_key = "INSERT HERE YOUR API KEY"
vt_antivirus = CClassifierRemote(AvailableOnlineAntivirus.VirusTotal, api_key=api_key, threshold=0.2)
print(f"Analysing {filename} with VirusTotal.")
pred = vt_antivirus.predict(x)
print(f"Predicted: {pred.item()}")
