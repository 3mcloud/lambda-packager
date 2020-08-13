#/bin/sh
pip3 install -r requirements-dev.txt
wait
pytest
wait
# pylint entrypoint.py
# wait
# --rootdir
which ssh
