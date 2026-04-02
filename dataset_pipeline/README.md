# 🛡️ Solidity Vulnerability Analysis & Dataset Generation Pipeline

## 📌 Overview

This project implements a **research-level pipeline** for analyzing Solidity smart contracts and generating a **structured vulnerability dataset**.

The system:

* Parses Solidity contracts using static analysis
* Extracts semantic signals using Slither IR
* Detects vulnerabilities using logic-based pattern matching
* Generates structured JSON outputs with:

  * Vulnerability leads
  * Evidence
  * Execution witnesses
  * Confidence scores
  * Ground truth labels (SmartBugs)

This pipeline is designed for:

* Vulnerability research
* Dataset generation
* Machine learning applications
* Security analysis automation

---

## 🚀 Key Features

### ✅ Multi-Version Solidity Support

* Automatically detects `pragma` version
* Dynamically switches compiler (0.4.x → 0.8.x)

### ✅ IR-Based Analysis (No Heuristics)

* Uses Slither Intermediate Representation (IR)
* Avoids string matching or hardcoding
* Extracts:

  * External calls
  * State writes/reads
  * Control flow ordering

### ✅ Multi-Vulnerability Detection

Supports major SWC categories:

* Reentrancy (SWC-107)
* Access Control (SWC-105)
* Unchecked Calls (SWC-104)
* Delegatecall (SWC-112)
* Selfdestruct (SWC-106)
* DOS patterns (SWC-113)
* Timestamp Dependence (SWC-116)
* tx.origin misuse (SWC-115)

### ✅ Evidence-Based Reasoning

Each detection includes:

* IR-level evidence
* Control-flow reasoning
* State transition analysis

### ✅ Witness Generation

Generates execution traces:

* Function-level paths
* Call → state update sequences
* Attack flow representation

### ✅ Scoring System

* Confidence score (signal-based)
* Priority score (severity-weighted)

### ✅ Dataset Generation

* Batch processing of contracts
* Automatic JSON generation
* Ground truth labeling (SmartBugs folders)

---

## 🏗️ Architecture

```
Solidity Code
      ↓
Slither (IR + CFG)
      ↓
Signal Extractor
      ↓
Pattern Engine
      ↓
Evidence Builder
      ↓
Lead Generator
      ↓
Witness Generator
      ↓
JSON Dataset Output
```

---

## 📁 Project Structure

```
project/
│
├── contracts/                # Input Solidity files (SmartBugs structure)
│   ├── reentrancy/
│   ├── access_control/
│   └── ...
│
├── output/                   # Generated JSON dataset
│
├── slither_runner.py         # Compiler handling + Slither integration
├── signal_extractor.py       # IR-based feature extraction
├── pattern_engine.py         # Vulnerability logic rules
├── lead_generator.py         # Lead generation + scoring
├── witness_generator.py      # Execution path generation
├── pipeline.py               # Single file processing
├── batch_runner.py           # Batch dataset generation
│
└── README.md
```

---

## ⚙️ Installation

### 1. Install dependencies

```bash
pip install slither-analyzer
pip install py-solc-x
pip install networkx
```

---

### 2. Install Solidity compilers

```bash
python -c "from solcx import install_solc; install_solc('0.4.26')"
python -c "from solcx import install_solc; install_solc('0.5.17')"
python -c "from solcx import install_solc; install_solc('0.6.12')"
python -c "from solcx import install_solc; install_solc('0.7.6')"
python -c "from solcx import install_solc; install_solc('0.8.20')"
```

---

## 📥 Dataset Setup

Clone SmartBugs dataset:

```bash
git clone https://github.com/smartbugs/smartbugs-curated.git
```

Copy contracts:

```bash
mkdir contracts
# Windows
for /r smartbugs-curated\dataset %f in (*.sol) do copy "%f" contracts\
```

---

## ▶️ Usage

### Run single file

```bash
python pipeline.py input.sol output.json label
```

---

### Run batch processing

```bash
python batch_runner.py
```

---

## 📊 Output Format

Example JSON:

```json
{
  "example_id": "contract1",
  "ground_truth": "reentrancy",
  "contract_id": "Vault",

  "target_output": {
    "leads": [
      {
        "pattern": "reentrancy",
        "swc_id": "SWC-107",
        "evidence": [
          {"tool": "ir-analysis", "note": "external call detected"},
          {"tool": "control-flow", "note": "state write after call"}
        ],
        "confidence": 0.92,
        "priority_score": 0.95
      }
    ],
    "witnesses": [
      {
        "path": [
          "external_call(msg.sender.call)",
          "state_write(balances)"
        ],
        "bad_state": "balance_drain"
      }
    ]
  }
}
```

---

## 🧠 Methodology

### Signal Extraction

* Uses Slither IR nodes
* Captures:

  * Calls
  * State writes
  * Control flow ordering

### Pattern Matching

* Rule-based logic (no hardcoding)
* Conditions derived from signals

### Evidence Construction

* Multi-source:

  * IR analysis
  * Control-flow reasoning
  * Guard analysis

### Witness Generation

* Execution trace from call sequence
* Represents potential exploit flow

---

## 📈 Applications

* Smart contract auditing
* Vulnerability research
* Dataset generation for ML
* Security benchmarking
* Automated analysis tools

---

## ⚠️ Limitations

* Contracts with missing imports may fail
* Complex build systems (Hardhat/Foundry) not fully supported
* Some false positives/negatives possible
* Static analysis limitations

---

## 🔮 Future Work

* Cross-function attack detection
* Symbolic execution integration
* ML-based vulnerability ranking
* Graph neural networks for analysis
* Real exploit generation (controlled environment)

---

## 👨‍💻 Author

Vivek Kumar
B.Tech CSE, IIT Patna

---

## 📜 License

This project is for academic and research purposes.
