### About

An api suitable for ecommerce applications written using the [fastapi framework](https://fastapi.tiangolo.com/)


Implemented features
- User authentication
- Discounting using token and adding discounted price during sales
- Admin actions for order updates, product details
- Cart facility for multiple orders


#### Instaling(for linux)
- Clone the repo.
- Create a python virtual env: `python -m venv venv`
- Enter the virtual env: `source venv/bin/activate`
- Install necessary packages`python -r requirements.txt`

#### Running
- Create necessary postgresql database for testing and production
- Create an `.env` file at the project root. Refer to `app/config.py` for variable names
- Run application: `uvicorn app.main:app --reload` 

**Go to the /docs api endpoint to see the routes and its documentation**