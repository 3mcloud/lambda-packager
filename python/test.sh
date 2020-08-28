#/bin/sh
pip3 install -r requirements-dev.txt > /dev/null
wait
pytest -x -s
wait
pylint entrypoint.py
wait
# --rootdir
which ssh
