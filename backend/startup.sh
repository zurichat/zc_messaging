
if [ $1 = "venv" ] || [ $1 = "pipenv" ]
then

    if [ -z "$VIRTUAL_ENV" ]
    then
        echo "No VIRTUAL_ENV set"
    else
        echo "VIRTUAL_ENV is set"
        if [ $1 = "venv" ]
        then
            pip install -r requirements.txt
            cd ..

        else
            pipenv install -r requirements.txt
            cd ..

        fi

        if [ -f ./.git/hooks/pre-commit ]
        then
            echo "pre-commit already setup"
            cd backend
        else
            cd backend
            pre-commit install
        fi

        pytest
        uvicorn main:app --reload

    fi

else
    echo "invalid option"
    echo "use either venv or pipenv"
    exit 0
fi
