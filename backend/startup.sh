pip install -r requirements.txt
cd -
if [[ -f ./.git/hooks/pre-commit ]]
then
    echo "pre-commit already setup"
    cd backend
else
    cd backend
    pre-commit install
fi

uvicorn main:app --reload
