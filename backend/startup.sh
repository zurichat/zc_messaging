cd backend
pip install -r requirements.txt

if [[ -f ./.git/hooks/pre-commit ]]
then
    echo "pre-commit already setup"
else
    pre-commit install
fi
uvicorn main:app --reload
