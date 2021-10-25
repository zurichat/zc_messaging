# for setting up pre-commit hook
if [[ -f ./.git/hooks/pre-commit ]]
then
    echo "pre-commit already setup"
else
    cp ./pre-commit ./.git/hooks
    chmod +x ./.git/hooks/pre-commit
fi

cd backend
pip install -r requirements.txt
uvicorn main:app --reload