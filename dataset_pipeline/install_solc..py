from solcx import install_solc

versions = [
    "0.4.26",
    "0.5.17",
    "0.6.12",
    "0.7.6",
    "0.8.20"
]

for v in versions:
    print("Installing:", v)
    install_solc(v)

print(" All versions installed")