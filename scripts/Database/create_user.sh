#/bin/bash
python3 -m venv .venv
pip install --upgrade -r requirements.txt
python3 create_user.py