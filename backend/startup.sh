pip install -r requirements.txt
cd -
if [[ -f ./.git/hooks/pre-commit ]]
then
    echo "pre-commit already setup"
else
    cd backend
    pre-commit install
fi
cd backend
uvicorn main:app --reload
