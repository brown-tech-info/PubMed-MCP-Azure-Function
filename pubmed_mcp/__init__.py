import os
from dotenv import load_dotenv
load_dotenv()
import requests
import azure.functions as func
import json
import logging

PUBMED_API_KEY = os.environ.get('PUBMED_API_KEY')
PUBMED_EMAIL = os.environ.get('PUBMED_EMAIL')

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Received request to pubmed_mcp function.")
    query = req.params.get('query')
    logging.info(f"Query param: {query}")
    if not query:
        try:
            req_body = req.get_json()
            logging.info(f"Request body: {req_body}")
        except ValueError as e:
            logging.error(f"Error parsing request body: {e}")
            return func.HttpResponse(
                "Missing search query.", status_code=400
            )
        query = req_body.get('query')
    if not query:
        logging.warning("No search query provided.")
        return func.HttpResponse(
            "Missing search query.", status_code=400
        )
    # PubMed E-utilities: esearch to get IDs
    esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    esearch_params = {
        "db": "pubmed",
        "term": query,
        "retmax": 5,
        "api_key": PUBMED_API_KEY,
        "email": PUBMED_EMAIL,
        "retmode": "json"
    }
    logging.info(f"Sending esearch request to PubMed: {esearch_params}")
    try:
        esearch_resp = requests.get(esearch_url, params=esearch_params)
        logging.info(f"esearch response status: {esearch_resp.status_code}")
        logging.debug(f"esearch response text: {esearch_resp.text}")
    except Exception as e:
        logging.error(f"Exception during esearch request: {e}")
        return func.HttpResponse(
            f"Error contacting PubMed: {str(e)}", status_code=502
        )
    if esearch_resp.status_code != 200:
        logging.error(f"Error from PubMed esearch: {esearch_resp.text}")
        return func.HttpResponse(
            f"Error from PubMed: {esearch_resp.text}", status_code=502
        )
    id_list = esearch_resp.json().get('esearchresult', {}).get('idlist', [])
    logging.info(f"PubMed ID list: {id_list}")
    if not id_list:
        logging.info("No articles found for query.")
        return func.HttpResponse(
            json.dumps({"results": []}), mimetype="application/json"
        )
    # efetch to get details
    efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    efetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "retmode": "xml",
        "api_key": PUBMED_API_KEY,
        "email": PUBMED_EMAIL
    }
    logging.info(f"Sending efetch request to PubMed: {efetch_params}")
    try:
        efetch_resp = requests.get(efetch_url, params=efetch_params)
        logging.info(f"efetch response status: {efetch_resp.status_code}")
        logging.debug(f"efetch response text: {efetch_resp.text}")
    except Exception as e:
        logging.error(f"Exception during efetch request: {e}")
        return func.HttpResponse(
            f"Error contacting PubMed: {str(e)}", status_code=502
        )
    if efetch_resp.status_code != 200:
        logging.error(f"Error from PubMed efetch: {efetch_resp.text}")
        return func.HttpResponse(
            f"Error from PubMed: {efetch_resp.text}", status_code=502
        )
    # Parse XML for titles/abstracts
    import xml.etree.ElementTree as ET
    try:
        root = ET.fromstring(efetch_resp.text)
        results = []
        for article in root.findall('.//PubmedArticle'):
            title = article.findtext('.//ArticleTitle')
            abstract = article.findtext('.//AbstractText')
            results.append({"title": title, "abstract": abstract})
        logging.info(f"Returning {len(results)} articles.")
        return func.HttpResponse(
            json.dumps({"results": results}), mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error parsing PubMed XML: {e}")
        return func.HttpResponse(
            f"Error parsing PubMed response: {str(e)}", status_code=500
        )
