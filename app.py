from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
from flask_cors import CORS 
from bson import ObjectId

load_dotenv()

mongoURI = os.getenv("URI")

app = Flask(__name__)
CORS(app)

# Configure MongoDB using Flask-PyMongo
app.config['MONGO_URI'] = mongoURI
mongo = PyMongo(app)
collection = mongo.db.scraped_data

# POST 
@app.route('/scrape', methods=['POST'])
def scrape_wikipedia():
    try:
        data = request.get_json()
        url = data['url']
        
        # Scrape Wikipedia page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all URLs from the page starting with "https"
        scraped_urls = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith('https')]
        
        # Store the scraped data in MongoDB
        inserted_data = collection.insert_one({"url": url, "scraped_urls": scraped_urls})
        
        return jsonify({"message": "Scraping and storing complete!", "id": str(inserted_data.inserted_id)})
    except Exception as e:
        return jsonify({"error": str(e)})
    
# GET by url
@app.route('/get_urls', methods=['GET']) 
def get_scraped_urls_single():
    try:
        url_param = request.args.get('url')
        data = collection.find_one({"url": url_param})
        if data:
            scraped_urls = data.get("scraped_urls", [])
            return jsonify({"scraped_urls": scraped_urls})
        else:
            return jsonify({"message": "No scraped URLs found for the specified URL."})
    except Exception as e:
        return jsonify({"error": str(e)})
    
# Get All
@app.route('/get_all_data', methods=['GET'])
def get_all_data_reverse():
    try:
        # get the all data reverse the order
        all_data = list(collection.find().sort("_id", -1))
        
        for item in all_data:
            item["_id"] = str(item["_id"])

        if all_data:
            return jsonify({"data": all_data})
        else:
            return jsonify({"message": "No data found in the collection."})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
