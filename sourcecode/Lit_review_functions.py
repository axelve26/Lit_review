import os
import re
import urllib.parse
import subprocess
import requests
import pandas as pd
import csv
import ast
import xml.etree.ElementTree as ET
import urllib.parse
import time
import json

def get_pii_by_doi(doi):
    SEARCH_URL = 'https://api.elsevier.com/content/search/scopus'
    if not os.path.exists('./api_key.csv'):
        print("API key file not found. Get the API key and save it in a file named 'api_key.csv' in the current directory\n(e.g. publisher,api_key\nelsevier,<your_api_key>)")
        return None
    else:
        api_key_csv = pd.read_csv('./api_key.csv', header=0)
        for i, row in api_key_csv.iterrows():
            if 'elsevier' in row['publisher']:
                # print(row)
                API_KEY = row['api_key']
                # print('API key:', API_KEY)

    # api_key_csv = pd.read_csv('../api_key.csv')
    headers = {
        'X-ELS-APIKey': API_KEY,
        'Accept': 'application/json'
    }
    params = {
        'query': f'DOI({doi})'
    }
    response = requests.get(SEARCH_URL, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json()
        entries = results.get('search-results', {}).get('entry', [])
        if entries:
            for entry in entries:
                if 'pii' in entry:
                    return entry['pii']
            return None
        else:
            return None
    else:
        return None

def get_pii_by_title(title):
    SEARCH_URL = 'https://api.elsevier.com/content/search/scopus'

    headers = {
        'X-ELS-APIKey': API_KEY,
        'Accept': 'application/json'
    }

    params = {
        'query': f'TITLE("{title}")'
    }

    response = requests.get(SEARCH_URL, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json()
        entries = results.get('search-results', {}).get('entry', [])
        if entries:
            for entry in entries:
                if 'pii' in entry:
                    return entry['pii']
            return None
        else:
            return None
    else:
        return None


def search_ncbi(query):
    url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'
    maxi = 96
    params = {
        'db': 'pubmed',
        'term': query,
        "retmax": maxi,
        # "retstart": "0",
        'retmode': 'json'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        # print(data)
        id_list = data['esearchresult']['idlist']
        count_0 = data['esearchresult']['count']
        # print('there are', count_0, 'articles containing', count_0, 'in the abstract')
        time.sleep(1)

    # print(f'\n note: set the retmax (currently at {maxi}) to the nr of articles ({count_0}) and run again to get all the articles')
    # print(f'(This step is double because we need to know the total number of articles, namely {count_0}, to set the retmax to that number...)')
    maxi = count_0
    params = {
        'db': 'pubmed',
        'term': query,
        "retmax": maxi,
        # "retstart": "0",
        'retmode': 'json'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        # print(data)
        id_list = data['esearchresult']['idlist']
        count = data['esearchresult']['count']
        print('Initial query results: there are', count, 'articles containing', query, 'in the abstract or title')
        time.sleep(1)
        # print(len(id_list))

    # print(id_list)
    return id_list


import requests
import time
import xml.etree.ElementTree as ET

def fetch_external_link(pubmed_id):
    retries = 3
    delay = 2

    for attempt in range(retries):
        try:
            url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi'
            params = {
                'dbfrom': 'pubmed',
                'id': pubmed_id,
                'cmd': 'llinks',
                'retmode': 'xml'
            }
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                tree = ET.ElementTree(ET.fromstring(response.content))
                root = tree.getroot()
                linksets = root.findall('.//LinkSetDb')
                for linkset in linksets:
                    if linkset.find('LinkName').text == 'pubmed_pubmed':
                        print(f"Found external link for {pubmed_id}: {linkset}")
                        pass#continue
                    links = linkset.findall('Link/IdUrlList/IdUrl')
                    print(links)
                    for link in links:
                        print(link.text)
                        provider = link.find('Provider').text
                        url = link.find('Url').text
                        if provider and url:
                            print(f"Provider: {provider}, URL: {url}")
                            return provider, url
            else:
                print(f"Failed to fetch external link for {pubmed_id} (Status Code: {response.status_code})")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Moving to the next ID.")

    return None, None

def create_highlighted_url(pubmed_id, sentence, pmc_id='not available'):
    if pmc_id == 'not available':
        external_link = fetch_external_link(pubmed_id)
        if not external_link:
            return "External link not found."

        highlighted_text = urllib.parse.quote(sentence)
        full_url = f"{external_link}#:~:text={highlighted_text}"
        return full_url
    elif pmc_id != 'not available':
        # print(pmc_id)
        pmcid = str(pmc_id).strip()
        # print(pmcid)
        highlighted_text = urllib.parse.quote(sentence)
        url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/'
        full_url = f"{url}#:~:text={highlighted_text}"
        return full_url

def url_issues(highlighted_text):
    if '-' in highlighted_text:
        highlighted_text = highlighted_text.replace('-', '%2D')
    if '(' in highlighted_text:
        highlighted_text = highlighted_text.replace('(', '%28')
    if ')' in highlighted_text:
        highlighted_text = highlighted_text.replace(')', '%29')
    if '/' in highlighted_text:
        highlighted_text = highlighted_text.replace('/', '%2F')
    return highlighted_text

def create_highlighted_url2(pubmed_id, sentence, url):
    if not 'PMC' in url:
        # external_link = fetch_external_link(pubmed_id)
        # result = fetch_external_link(pubmed_id)
        # if not result:#external_link:
        #     return "External link not found."
        # if result:
        #     print(f"Publisher: {result[0]}, URL: {result[1]}")
        # else:
        #     print("No external link found.")
        if 'doi_' in url:
            # print(url)
            doi_only = url.split('doi_')[1]
            pii_id = get_pii_by_doi(doi_only)
            if pii_id:
                link = f'https://www.sciencedirect.com/science/article/pii/{pii_id}'

                highlighted_text = urllib.parse.quote(sentence)
                # full_url = f"{external_link}#:~:text={highlighted_text}"
                highlighted_text = url_issues(highlighted_text)
                full_url = f"{link}#:~:text={highlighted_text}"
                return full_url
            else:
                # print(url, doi_only)
                if pubmed_id == 'American Chemical Society (ACS)':
                    link = f'https://pubs.acs.org/doi/{doi_only}'
                    highlighted_text = urllib.parse.quote(sentence)
                    highlighted_text = url_issues(highlighted_text)
                    full_url = f"{link}#:~:text={highlighted_text}"
                    return full_url
                elif 'Springer' in pubmed_id:
                    link = f'https://link.springer.com/article/{doi_only}'
                    highlighted_text = urllib.parse.quote(sentence)
                    highlighted_text = url_issues(highlighted_text)
                    full_url = f"{link}#:~:text={highlighted_text}"
                    return full_url
        else:
            return "External link not found."
    else:
        pmc_id = url.split('/')[-2]
        # print(pmc_id)
        pmcid = str(pmc_id).strip()
        # print(pmcid)
        highlighted_text = urllib.parse.quote(sentence)
        highlighted_text = url_issues(highlighted_text)
        # url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/'
        full_url = f"{url}#:~:text={highlighted_text}"
        return full_url


def get_bib(some_df):
    bib_text = ''
    pubmed_to_citekey = {}
    titles = []

    for index, row in some_df.iterrows():
        title = row['title']
        author = row['authors'][0].split(',')[0]
        pubmed_id = row['pubmed_id']
        cite_key = f"{author}_{title.split(' ')[0]}_{row['pub_date'].split('-')[0]}"
        # print(row['url'])
        # print(row['pmc_id'])
        if 'PMC' in row['url']:
            id = str(some_df['pmc_id'].values[0]).strip().replace(' ', '').replace('0', '').replace('\nName:pmc_id,dtype:object', '')
            url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{id}/'
        else:
            url = f'https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/'
        if ',' in cite_key:
            cite_key = cite_key.replace(',', '_')
        if '-' in cite_key:
            cite_key = cite_key.replace('-', '_')
        if ' ' in cite_key:
            cite_key = cite_key.replace(' ', '_')
        # add 'f'  note={{Visited on: {visit_date}}},\n' to the bib_text with visited date being the current date:
        # get current date:
        visit_date = time.strftime("%Y-%m-%d")

        bib_text += f"@article{{{cite_key},\n  title={{{title}}},\n  author={{{' and '.join(row['authors'])}}},\n  year={{{row['pub_date']}}},\n  journal={{{row['journal_title']}}},\n  doi={{{row['doi']}}},\n  url={{{url}}},\n  note={{Visited on: {visit_date}}}\n}}"
        pubmed_to_citekey[pubmed_id] = cite_key
        # if bib_text not in new_bibs:
        #     new_bibs.append(bib_text)
        titles.append(title)
    if not os.path.exists('../review_query/References.bib'):
        with open('../review_query/References.bib', 'w') as f:
            f.write(bib_text)
    else:
        with open('../review_query/References.bib', 'r') as f:
            content = f.read()
            if bib_text.strip() not in content:
                with open('../review_query/References.bib', 'a') as f:
                    f.write('\n' + bib_text)

    # # print(bib_text)
    if not os.path.exists('../review_query/References.txt'):
        with open('../review_query/References.txt', 'w') as f:
            f.write(bib_text)
    else:
        with open('../review_query/References.txt', 'r') as f:
            bib_line = bib_text.split('\n')[0]
            if bib_line not in f.read():
                with open('../review_query/References.txt', 'a') as f:
                    f.write(bib_text)



    return bib_text, pubmed_to_citekey

def highlight_terms(text, terms):
    for term in terms:
        text = re.sub(f"({term})", r"\033[1;31m\1\033[0m", text, flags=re.IGNORECASE)
    return text

def ask_question(question, prev_answer=None):
    if prev_answer:
        question += f" (current: {prev_answer})"
    return input(question).strip()

import re

def highlight_relevanterms(sentence, search_terms):
    for term in search_terms:
        term_escaped = re.escape(term)
        sentence = re.sub(f'({term_escaped})', r'<span style="color:red">\1</span>', sentence, flags=re.IGNORECASE)
    return sentence


def col_to_list(query, path, col):
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Query'] == query:
                pubmed_ids = ast.literal_eval(row[col])
                return pubmed_ids


def remove_submitted_data_file():
    if os.path.exists("./data/saved_progress/submitted_data.csv"):
        os.remove("./data/saved_progress/submitted_data.csv")
        print("./data/saved_progress/submitted_data.csv has been removed.")
    else:
        print("./data/saved_progress/submitted_data.csv does not exist.")

def fetch_external_link(pubmed_id):
    retries = 3
    delay = 2

    for attempt in range(retries):
        try:
            url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
            params = {
                'db': 'pubmed',
                'id': pubmed_id,
                'retmode': 'xml'
            }
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                tree = ET.ElementTree(ET.fromstring(response.content))
                root = tree.getroot()
                docsum = root.find('.//DocSum')
                if docsum is not None:
                    links = docsum.findall('.//Item[@Name="ELocationID"]')
                    for link in links:
                        if link.text and 'http' in link.text:
                            return link.text
            else:
                print(f"Failed to fetch external link for {pubmed_id} (Status Code: {response.status_code})")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Moving to the next ID.")

    return None

def create_highlighted_url(pubmed_id, sentence, pmc_id='not available'):
    if pmc_id == 'not available':
        external_link = fetch_external_link(pubmed_id)
        if not external_link:
            return "External link not found."

        highlighted_text = urllib.parse.quote(sentence)
        full_url = f"{external_link}#:~:text={highlighted_text}"
        return full_url
    elif pmc_id != 'not available':
        # print(pmc_id)
        pmcid = str(pmc_id).strip()
        # print(pmcid)
        highlighted_text = urllib.parse.quote(sentence)
        url = f'https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/'
        full_url = f"{url}#:~:text={highlighted_text}"
        return full_url


#
import subprocess
import os
import time
import pandas as pd

def start_dash_app(pubmed_id, url):
    process = subprocess.Popen(['python', './sourcecode/Lit_review_Dash_app.py', pubmed_id, url])
    return process

def wait_for_data():
    file_path = "./data/saved_progress/submitted_data.csv"
    while not os.path.exists(file_path):
        time.sleep(1)
    time.sleep(2)


def process_submitted_data(pubmed_id, download_df, url):
    process = start_dash_app(pubmed_id, url)
    # print('process:', process)
    wait_for_data()
    dffromdash = pd.read_csv("./data/saved_progress/submitted_data.csv", header=0)
    print(dffromdash)
    process.terminate()

    return dffromdash

def start_dash_app_2(pubmed_id, url):
    process = subprocess.Popen(['python', './sourcecode/Lit_review_Dash-app-2.py', pubmed_id, url])
    return process

def wait_for_progress_save(pubmed_id):
    file_path = f"./data/saved_progress/saved_in_progress_{pubmed_id}.csv"
    while not os.path.exists(file_path):
        time.sleep(1)
    time.sleep(2)


def process_submitted_data_2(pubmed_id, download_df, url):
    process = start_dash_app_2(pubmed_id, url)
    print('process:', process)
    wait_for_progress_save(pubmed_id)
    # dffromdash = pd.read_csv("./data/saved_progress/submitted_data.csv", header=0)
    # print(dffromdash)
    process.terminate()
    print('progress saved, nothing submitted')
    return 0



def fetch_article_details2(pubmed_id):
    retries = 3
    delay = 2

    for attempt in range(retries):
        try:
            url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi'
            params = {
                'db': 'pubmed',
                'id': pubmed_id,
                'retmode': 'xml'
            }
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                tree = ET.ElementTree(ET.fromstring(response.content))
                root = tree.getroot()
                title = root.find('.//ArticleTitle').text if root.find('.//ArticleTitle') is not None else ''
                abstract_texts = root.findall('.//AbstractText')

                abstract_parts = []
                if abstract_texts:
                    for abstract_text in abstract_texts:
                        if abstract_text is not None and abstract_text.text is not None:
                            abstract_parts.append(abstract_text.text)
                        else:
                            abstract_parts.append('')
                    abstract = ' '.join(abstract_parts)
                else:
                    abstract = 'Not found'

                return title, abstract
            else:
                print(f"Failed to fetch article details for {pubmed_id} (Status Code: {response.status_code})")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Moving to the next ID.")

    return 'Not found', 'Not found'

import requests


def fetch_publisher_by_doi(doi):
    base_url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(base_url)

    if response.status_code == 200:
        data = response.json()
        publisher = data['message'].get('publisher', 'Publisher not found')
        return publisher
    else:
        return 'DOI not found or invalid request'


def fetch_publisher_by_pubmed_id(pubmed_id):
    pubmed_base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": pubmed_id,
        "retmode": "json"
    }
    response = requests.get(pubmed_base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        uid = list(data['result'].keys())[0]
        if uid == 'uids':
            return 'PubMed ID not found'
        else:
            article_data = data['result'][uid]
            doi = article_data.get('elocationid', None)

            if doi and doi.startswith('doi:'):
                doi = doi[4:]
                return fetch_publisher_by_doi(doi)
            else:
                return 'DOI not found in PubMed record'
    else:
        return 'PubMed ID not found or invalid request'


def fetch_article_pmcid(pubmed_id):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": pubmed_id,
        "retmode": "xml"
    }
    response = requests.get(base_url, params=params)
    pmc_id = None

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        for pubmed_article in root.iter('PubmedArticle'):
            for article_id_list in pubmed_article.iter('ArticleIdList'):
                for article_id in article_id_list:
                    if 'IdType' in article_id.attrib and article_id.attrib['IdType'] == 'pmc':
                        pmc_id = article_id.text
                        break

                if pmc_id:
                    break

            if pmc_id:
                break

    return pmc_id


def fetch_article_metadata2(pubmed_id):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": pubmed_id,
        "retmode": "xml"
    }

    response = requests.get(base_url, params=params)
    pmc_id = None

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        article = root.find('PubmedArticle')

        title = article.find(".//ArticleTitle").text
        # abstract = article.find(".//AbstractText").text #if article.find(".//AbstractText") is not None else ""
        title, abstract = fetch_article_details2(pubmed_id)
        pub_date = article.find(".//PubDate/Year").text
        journal_title = article.find(".//Journal/Title").text

        pmc_id = fetch_article_pmcid(pubmed_id)

        for article_id in article.findall(".//ArticleId"):
            if article_id.attrib['IdType'] == 'doi':
                doi = article_id.text
                print(doi)
                break
            else:
                doi = 'Not found'
        # for article_id in article.findall(".//ArticleId"):
        #     #print(article_id)
        #     if article_id.attrib['IdType'] == 'pmc':
        #         pmc_id = article_id.text

        authors = []
        for author in article.findall(".//Author"):
            lastname = author.find("LastName").text if author.find("LastName") is not None else ""
            forename = author.find("ForeName").text if author.find("ForeName") is not None else ""
            authors.append(f"{forename} {lastname}")

        return title, authors, pub_date, pmc_id, journal_title, abstract, doi

    else:
        print(f"Failed to fetch data for PubMed ID: {pubmed_id}")
        return None


def check_if_one_is_downloadable2(pubmed_id, addition=0):
    download_list = []
    download_df = pd.DataFrame(
        columns=['title', 'authors', 'pub_date', 'pubmed_id', 'pmc_id', 'journal_title', 'url', 'downloadable', 'abstract', 'doi'])
    undownloadables = []
    undownloadable_df = pd.DataFrame(
        columns=['title', 'authors', 'pub_date', 'pubmed_id', 'pmc_id', 'journal_title', 'url', 'downloadable', 'abstract', 'doi'])
    #title, authors, pub_date, pmc_id, journal_title, abstract, doi
    metadata = fetch_article_metadata2(pubmed_id)
    time.sleep(2)
    if metadata:
        title, authors, pub_date, pmc_id, journal_title, abstract, doi = metadata
        if pmc_id is None or 'PMC' not in pmc_id:
            print('fail\n \n*        *\n\n   ~\n')  # ' no pmc_id for:', title, 'by', ', '.join(authors), pub_date)
            # if pmc_id == None:
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
            print(f"\n NO pmc_id for:\t\t'{title}',\t{pub_date}\nThis is the URL: {url}")  # by {', '.join(authors)},
            pmc_id = 'None'
            # url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
            # url = f'<a href="https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/">https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/</a>'
            # url = f'=HYPERLINK("https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/", "PubMed Link")'
            # print(url)
            undownloadable_df.loc[len(undownloadable_df)] = [title, authors, pub_date, pubmed_id, pmc_id,
                                                             journal_title,
                                                             url, False, abstract, doi]
            undownloadables.append(url)
            return undownloadable_df

        if "PMC" in pmc_id:
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"#pdf/"
            # url = f'<a href="https://pubmed.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/">https://pubmed.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/</a>'
            # url = f'=HYPERLINK("https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/", "PubMed Link")'
            # print(
            #     f"PMC ID found:   {pmc_id}    is downloadable :D\nTitle: \n  {title} \nAuthors:\n  {', '.join(authors)} \nPublication Date:   {pub_date}      Journal:    {journal_title}\n URL:")
            print(
                f"PMC ID found:   {pmc_id}    is downloadable :D\nTitle:\t{title} \nPublication Date:   {pub_date}\t\tURL: {url}")
            # print(url, '\n')
            download_list.append(pmc_id)
            # clickable = display_link(url, f'Click here to see the article: {pmc_id}')
            # print(clickable)
            download_df.loc[len(download_df)] = [title, authors, pub_date, pubmed_id, pmc_id, journal_title, url, True, abstract, doi]
            # else:
            #     print('Fail')
            #     #print(f"\n\n*        *\n    ~\n NO pmc_id for:\n'{title}'\n, by {', '.join(authors)}, {pub_date}\n This is the URL:")
            #     url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}"
            #     undownloadable_df.loc[len(undownloadable_df)] = [title, authors, pub_date, pubmed_id, url]
            #     #clicky = display_link(url, f'Click here to see the article: {pubmed_id}')
            #     undownloadables.append(url)
            #     print('undownloadable_df:', undownloadable_df)
            return download_df


def filter_articles3(pubmed_id, search_terms, file_name):
    count_removed = 0
    count_retained = 0

    if not os.path.exists(f'../temp/retained_articles_temp_{file_name}.csv'):
        retained_articles = pd.DataFrame()
    else:
        retained_articles = pd.read_csv(f'../temp/retained_articles_temp_{file_name}.csv', header=0)
    if not os.path.exists(f'../temp/removed_articles_temp_{file_name}.csv'):
        removed_articles = pd.DataFrame()
    else:
        removed_articles = pd.read_csv(f'../temp/removed_articles_temp_{file_name}.csv', header=0)

    # retained_articles = pd.DataFrame()
    to_analyze = 10000
    # print(f"Processing {to_analyze} articles ...")
    # for pubmed_id in pubmed_ids:

    if 'pubmed_id' in retained_articles.columns:
        if pubmed_id in retained_articles['pubmed_id'].values:
            print(f"Article {pubmed_id} already processed. Skipping ...")
            return pubmed_id, f'excluded', 'Article already processed.'
    if 'pubmed_id' in removed_articles.columns:
        if pubmed_id in removed_articles['pubmed_id'].values:
            print(f"Article {pubmed_id} already processed. Skipping ...")
            return pubmed_id, f'excluded', 'Article already processed.'
    # if count_retained >= to_analyze:
    #     break

    title, abstract = fetch_article_details2(pubmed_id)
    # print(f"Processing article {pubmed_id}, {title}")
    if title:
        title = str(title).lower()
    if abstract:
        abstract = str(abstract).lower()
    else:
        return pubmed_id, f'included', 'Abstract not found. Requires manual check.'
    # print("Title:", title)
    # print("Abstract:", abstract)
    # print(abstract)
    # print(f"Processing article {pubmed_id}, {title}")
    if title is None:
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
        # print(f"Article {pubmed_id}: Title not found. Requires manual check.", url)
        new_row = {'pubmed_id': pubmed_id, 'title': 'Not found', 'included': True, 'cause': 'Title not found. Requires manual check.', 'abstract': abstract, 'url': url}
        retained_articles = pd.concat([retained_articles, pd.DataFrame([new_row])])
        retained_articles.to_csv(f'../temp/retained_articles_temp_{file_name}.csv', index=False)
        # count_retained += 1
        # print(count_retained)
        return pubmed_id, f'included', 'Title not found. Requires manual check.'
    if any(term in title for term in search_terms) or any(term in abstract for term in search_terms):
        new_row = {'pubmed_id': pubmed_id, 'title': title, 'included': True, 'cause': f'Title or abstract contains search terms: {search_terms}', 'abstract': abstract}
        # print(f"Article {title} retained. Cause: Title or abstract contains search terms: {search_terms}")

        retained_articles = pd.concat([retained_articles, pd.DataFrame([new_row])])
        retained_articles.to_csv(f'../temp/retained_articles_temp_{file_name}.csv', index=False)
        # count_retained += 1
        # print(count_retained)
        return pubmed_id, f'included', f'Title or abstract contains search terms: {search_terms}'

    else:
        if abstract == 'Not found':
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
            new_row = {'pubmed_id': pubmed_id, 'title': title, 'included': True, 'cause': 'Abstract not found. Requires manual check.', 'abstract': abstract, 'url': url}
            # use concat:
            retained_articles = pd.concat([retained_articles, pd.DataFrame([new_row])])
            retained_articles.to_csv(f'../temp/retained_articles_temp_{file_name}.csv', index=False)
            # print(f"Article {pubmed_id}: Abstract not found. Requires manual check.")
            # count_retained += 1
            # print(count_retained)
            return pubmed_id, f'included', 'Abstract not found. Requires manual check.'
        else:
            count_removed += 1
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
            new_row = {'pubmed_id': pubmed_id, 'title': title, 'url': url, 'included': False, 'cause': f'None of {search_terms} present in title & abstract', 'abstract': abstract}
            removed_articles = pd.concat([removed_articles, pd.DataFrame([new_row])])
            removed_articles.to_csv(f'../temp/removed_articles_temp_{file_name}.csv', index=False)
            # print(f'Removed: {title} - {url}')
            return pubmed_id, f'excluded', f'None of {search_terms} present in title & abstract'

