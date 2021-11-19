import logging
from flask import Blueprint, request
from io import BytesIO

from services import model

from collections import Counter
from random import choice

# define the blueprint
blueprint_model = Blueprint(name="blueprint_model", import_name=__name__)


logger = logging.getLogger('model')
logging.basicConfig(
    format='[ %(name)s API ] %(asctime)s %(message)s', level=logging.WARNING)



# TODO : fill it
def adviceabout(category):
    # Build a function that return a sentence about category
    return choice([
        "This is some sentence about the object detected",
        "This is another random sentence"
    ])

def adviceaboutmanyobjects(stats):
    nunique = len(stats)
    if nunique == 1:
        return adviceabout(stats.most_common(1)[0][0])

    if nunique > 1 :
        s = stats.most_common(2)
        # top is very more frequent
        if s[0][1] >= 2*s[1][1]:
            return adviceabout(stats.most_common(1)[0][0])

    return f"There are several Objects on this image"


def didntgetitsentence():
    return choice([
        "Hum sorry, I did not get it. Maybe lighthing is off",
        "Can't find any object  here. Maybe try from another angle",
        "Sorry image is fuzzy. Are you sure there is any object here ?",
        "Can't see no object. Try to get closer or get a better light."
    ])


def addadvice(prediction):
    if 'predictions' in prediction:
        predictions = prediction['predictions']
        logger.info('------------------------------------------')
        logger.info(predictions)
        best = [p for p in predictions if p['probability'] > 0.40]
        logger.info(best)
        prediction['predictions'] = best

        # Ok magic sauce
        nobject = len(best)
        uniqueobject = list(set([c['label'] for c in best]))
        nuniqueobject = len(uniqueobject)
        prediction['nobject'] = nobject
        prediction['uniqueobject'] = uniqueobject
        prediction['nuniqueobject'] = nuniqueobject
        basicstats = Counter([c['label'] for c in best if 'label' in c])
        prediction['basicstats'] = basicstats

        advice = didntgetitsentence()

        if nobject == 1:
            p = best[0]['probability']
            l = best[0]['label']

            if p < 0.7:
                advice = f"It looks like a  {l} ( but not sure about it )"
            else:
                advice = adviceabout(l)
        else:
            if nobject > 1 :
                advice = adviceaboutmanyobjects(basicstats)

        prediction['advice'] = advice
    return prediction


@blueprint_model.route("/health", methods=["GET"])
def health():
    res = {"msg": "I'm OK"}
    return res



@blueprint_model.route("/prediction", methods=["POST"])
def make_prediction_on_file(**kwargs):
    logger.info(">>>>>>>>>>>>>>  POST a file")
    logger.debug(kwargs)

    # Get the files from form
    source = request.files['img']
    sourceBin = source.read()

    # Do what you want with your file
    f = BytesIO(sourceBin)
    res = model.predict_file(f)

    res['source'] = source.filename
    logger.info("<<<<<<<<<<<<<<<File  Prediction API Output")

    return addadvice(res)
