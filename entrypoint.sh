set -o errexit
set -o pipefail
set -o nounset

python testmanage.py migrate
python testmanage.py test tests/ --noinput