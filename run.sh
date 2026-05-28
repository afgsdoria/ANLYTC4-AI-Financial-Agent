#!/bin/bash
cd /workspaces/ANLYTC4-AI-Financial-Agent
kill -9 $(lsof -t -i:8501) 2>/dev/null
/workspaces/ANLYTC4-AI-Financial-Agent/.venv/bin/python -m streamlit run app.py --server.address=127.0.0.1 --server.port=8501
