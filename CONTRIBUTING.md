# Development

To start developing on Django REST framework, clone the repo:

    git clone git@github.com:tryming/celery_model_result.git

Changes should broadly follow the [PEP 8][pep-8] style conventions, and we recommend you set up your editor to automatically indicate non-conforming styles.

## Testing

To run the tests:
* clone the repository
* copy config.env.tmp file to config.env
* set environment variables inside that file to point at PostgreSQL database
* load environment variables from file
    * Linux    
        ```bash
        eval $(cat config.env | sed 's/^/export /')
        ```
    * macOS
        ```bash
        set -o allexport;source config.env; set +o allexport
        ```
* setup the virtual environment
    ```bash
    # Setup the virtual environment
    virtualenv env
    source env/bin/activate
    pip install django
    pip install celery
    pip install -r requirements.txt
    ``` 
* run the tests
    * no coverage
        ```bash
        pytest
        ```
    * with coverage
        ```bash
        pytest --cov=. --cov-report=html
        ```
        * coverage report available in
            ```bash
            htmlcov/index.html
            ```


### Running against multiple environments

You can also use the excellent [tox][tox] testing tool to run the tests against all supported versions of Python and Django.  Install `tox` globally, and then simply run:

    tox
