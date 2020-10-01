THIS_FILE=${BASH_SOURCE[0]}
# name of this file
THIS_PATH=$(realpath "$THIS_FILE")
# full path to this file

PROJECT_DIR=$(dirname "$THIS_PATH")

export PYTHONPATH=$PROJECT_DIR/src/:$PROJECT_DIR:$PYTHONPATH
