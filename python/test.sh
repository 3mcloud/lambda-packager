#/bin/sh
echo ""
echo "=========================================="
echo " Running pip3 install for pytesting"
echo "=========================================="
echo ""
pip3 install -r requirements-dev.txt
RC=$?
if [ $RC != 0 ] ; then exit 1; fi

echo ""
echo "=========================================="
echo " Running lint tests via pylint"
echo "=========================================="
echo ""
pylint --fail-under=9 entrypoint.py
RC=$?
if [ $RC != 0 ] ; then exit 1; fi

echo ""
echo "=========================================="
echo " Running unit tests via pytest"
echo "=========================================="
echo ""
pytest -x -s -vvv tests/
RC=$?
if [ $RC != 0 ] ; then exit 1; fi

# --rootdir
which ssh
