# sap-intelligent-replenishment-agent

This repository is a starter skeleton for the **Intelligent Stock Replenishment Agent**.
It includes mock SAP MM data, extraction stubs, forecasting, draft PO generation, and a switchable GPT commentary module.

## Quickstart (local, mock mode)

1. Create virtualenv and activate:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.template` to `.env` and edit as needed (keep `USE_MOCK_DATA=true` for local testing).

4. Run the main pipeline:
```bash
python main.py
```

Outputs (draft POs) will be written to `output/draft_pos.csv`.
