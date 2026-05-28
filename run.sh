#!/bin/bash
cd /workspaces/ANLYTC4-AI-Financial-Agent
source .venv/bin/activate
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
