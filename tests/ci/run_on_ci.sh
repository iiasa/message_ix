set -x
set -e

python generate_test_file.py

python download_license.py

python download_db.py

pytest -v -s .
