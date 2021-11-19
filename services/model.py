import logging
logger = logging.getLogger('Cheezam')
logging.basicConfig(format='[ %(name)s API ] %(asctime)s %(message)s', level=logging.WARNING)



import sqlite3

from requests.exceptions import ConnectionError
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

import os
from dotenv import load_dotenv

load_dotenv()
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
predict_url = os.getenv('model_url')

client = BackendApplicationClient(client_id=client_id)

def send(img):
    try :
        oauth = OAuth2Session(client=client)
        oauth.fetch_token(token_url='https://accounts.prevision.io/auth/realms/prevision.io/protocol/openid-connect/token', client_id=client_id,  client_secret=client_secret)             
        files = {'image': img}        
        prediction = oauth.post("{}/model/predict".format(predict_url), files=files)
        return prediction.json()
    except ConnectionError:
        logging.error("Cannot call model")
        return {}


def predict_file(img):
    """Do something with your file a prediction or whatever

    Args:
        img (Bytes): A file in RAM

    Returns:
        dict : Some json about the file
    """
    logging.info("Prediction over a file")
    p = send(img)
    predictions =  p["predictions"]
    infos = len(img.getvalue())
    logging.info(infos)
    return {"infos":infos, "predictions":predictions}




def predict(featureDict):
    """Do A prediction over features

    Args:
        featureDict (dict): features

    Returns:
        dict : Prediction
    """
    logger.info("Prediction")
    logger.info(featureDict)
    # A very basic prediction
    res = featureDict['feat_1'] +featureDict['feat_2'] +featureDict['feat_3']
    logger.info(res)
    return {"prediction":res}    