from flask import Flask, request, make_response
from flask_restful import Resource, Api, abort
from recipe_scrapers import scrape_me
from urllib.parse import urlparse

# List of supported sites. If more sites are added switch to reading an external file for easier management
SUPPORTED_SITES = ["seriouseats.com", "bonappetit.com", "allrecipes.com", "food.com"]

# Creating flask app
app = Flask(__name__)
api = Api(app)

# Defining Helper Functions
def reformat_url(url):
    """ Reformats user submitted url to use https and removes any additional query strings """
    parsed = urlparse(url)
    new_url = "https://" + parsed.netloc + parsed.path
    return new_url

def url_for_supported_site(url):
    """ Check if the site displaying the recipe is supported by this api """
    parsed = urlparse(url)
    hostname = parsed.hostname
    # If the hostname includes www. we remove it
    if hostname[:4] == "www.":
        hostname = hostname[4:]
    if hostname in SUPPORTED_SITES:
        return True
    else:
        return False

def parse_recipe(url):
    """ Parses a recipe from a webpage """
    try:
        scraper = scrape_me(url)
    except:
        return False
    recipe_dict = {}
    recipe_dict['title'] = scraper.title()
    recipe_dict['ingredients'] = scraper.ingredients()
    recipe_dict['instructions'] = scraper.instructions().split('\n')
    return recipe_dict


# Resources

class FullRecipe(Resource):
    def get(self):
        submitted_url = request.args.get('url')
        url = reformat_url(submitted_url)
        if url_for_supported_site(url):
            recipe = parse_recipe(url)
            if recipe is not False:
                return recipe
        return abort(400)


api.add_resource(FullRecipe, '/getRecipe')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
