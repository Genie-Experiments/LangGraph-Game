#!/bin/bash

# Set PYTHONPATH
export PYTHONPATH=.

# Start backend with uvicorn in the background
uvicorn main:app --reload &

# Start frontend Streamlit
streamlit run FE/streamlit_ui.py