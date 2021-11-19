# Deploying an image detector app

## pre-requiste

- An object detector model
- client id
- client secret
- model url
  
## Dev 

- clone this
- fill the .env file ( see .env.example )
- Create a python virtual env and install ( we advise you t use python 3.8)
- launch server using gunicorn

``` 
git clone git@github.com:previsionio/prevision-object-detector-app.git
python3.8 -m venv env
pip install -r requirements.txt 
gunicorn --reload --bind 0.0.0.0:8080 --timeout 120  --limit-request-line 0   --access-logfile - run:app
```



Go to http://localhost:8080/ and check everything is fine. You should see a webapp.  You can test the API with the curl command (  using any image you want ):

```
curl --location --request POST 'http://localhost:8080/api/model/prediction' \
--form 'img=@"./test_img.jpg"'
```



## Prod