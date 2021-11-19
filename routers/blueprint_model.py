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

LABELS = ['patepresseecuite',
          'patemolleacroutelavee',
          'patemollecroutenaturelle',
          'patepersillee',
          'patepresseenoncuite']

names = {
    'patepresseecuite': 'pâte pressée cuite',
    'patemolleacroutelavee': "pâte molle à croute lavée",
    'patemollecroutenaturelle': "fromage de chèvre.",
    'patepresseenoncuite': "pâte pressée non cuite",
    "patepersillee" :"pâte persillée"
}


# TODO : fill it
def adviceaboutcheese(category):
    if category == 'patemolleacroutelavee':
        return choice([
            "Ouch ! be aware that this kind of cheese are often stinky. You should try Sweet White wine with it",
            "This kind of cheese looks like it comes frome North of France. Eat it with a Jurançons or a Côteaux-du-layon ",
            "Better with an Alsace Gewurztraminer Blanc"
        ])
    if category == 'patemollecroutenaturelle':
        return choice([
            "This kind of cheese often come from Goat's milk. It's very soft and a good entry point to France's cheeses! You could eat it with them with Touraine, Vouvray or Chinon",
            "Huuum. Les Fromages de Chèvres may range from very soft to very tasty. A wine from Anjou or Bordeaux will be great with this one !",
            "Goat(s cheese. Try Sancerre or Côte-de-Beaune with the freshest one, Vouvray or Sancerres with the more mature."
        ])
    if category == 'patepersillee':
        return choice([
            "Fromages à pâte persillée are very tasy cheese. The most famous is Le Roquefort but you should try Le Bleu d'auvergne or Le Bleu de Causse. Drink a Sauternes",
            "Fromage à pâte persillée. They taste well with Cherry jam and a glass of Cahors or  Madiran",
            "A Fromage à pâte persillé. There exist two kind, some with very strong taste ( Roquefort ) but some are softer ( Bleu de Gex ). Banyuls will taste fine with it"
        ])        
    if category == 'patepresseenoncuite':
        return choice([
            "'Fromages  à pates pressee non cuite' are the most common cheese in France. There is a lot of variety like reblochon or even Cantal. Pauillac and châteauneuf-du-pape are the way to go",
            "'Fromages  à pates pressee non cuite'  could range from very runny cheese, like reblochon, to firm ones like cantal. Eat with a Meursault!"
        ])

    if category == 'patepresseecuite':
        return choice([
            "Fromage a pate pressee cuite are not the more interessting. Try other cheeses."
        ])
    
    if category in names :
        return f"we like les fromages à {names[category]}"
    
    return f"This kind of cheese is unknknown to me but, hey, I like all cheeses !"


def howtoplateaudefromage(stats):
    nunique = len(stats)
    if nunique == 1:
        return adviceaboutcheese(stats.most_common(1)[0][0])

    if nunique > 1 :
        s = stats.most_common(2)
        # top is very more frequent
        if s[0][1] >= 2*s[1][1]:
            return adviceaboutcheese(stats.most_common(1)[0][0])

    return f"There are several cheese on this image"


def didntgetitsentence():
    return choice([
        "Hum sorry, I did not get it. Maybe lighthing is off",
        "Can't find any cheese here. Maybe try from another angle",
        "Sorry image is fuzzy. Are you sure there is any cheese here ?",
        "Can't see no cheese. Try to get closer or get a better light."
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
        ncheese = len(best)
        uniquecheese = list(set([c['label'] for c in best]))
        nuniquecheese = len(uniquecheese)
        prediction['ncheese'] = ncheese
        prediction['uniquecheese'] = uniquecheese
        prediction['nuniquecheese'] = nuniquecheese
        basicstats = Counter([c['label'] for c in best if 'label' in c])
        prediction['basicstats'] = basicstats

        advice = didntgetitsentence()

        if ncheese == 1:
            p = best[0]['probability']
            l = best[0]['label']

            if p < 0.7:
                advice = f"It smells like a fromage à {names[l]} ( but not sure about it )"
            else:
                advice = adviceaboutcheese(l)
        else:
            if ncheese > 1 :
                advice = howtoplateaudefromage(basicstats)

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
