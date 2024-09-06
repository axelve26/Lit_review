import re
# import fitz
import pandas as pd
# import PyPDF2
from IPython.display import display, HTML
from sourcecode.Lit_review_functions import *
# from sourcecode.Lit_review_functions import col_to_list#, check_if_one_is_downloadable2, highlight_terms, filter_articles3, process_submitted_data, get_bib, create_highlighted_url2, remove_submitted_data_file
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
import time
import pandas as pd
import os


url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi'



# use_example = input('Do you want to use the example search term? (y/n): ')
use_example = 'y'
if use_example == 'y':
    # query = "('text-mining' OR 'language model' OR 'artificial intelligence' OR 'natural language processing') AND ('adverse outcome pathway' OR 'biomedical knowledge graph')"
    # print('Searching NCBI for:', query)
    # listy = ['language model', 'natural language processing', 'adverse outcome pathway', 'biomedical knowledge graph', 'artificial intelligence', 'text-mining']
    # name_of_query = 'text-mining_OR_language_model_OR_natural_language_processing_AND_adverse_outcome_pathway_OR_biomedical_knowledge_graph'

    # query = "('language model' OR 'natural language processing') AND ('adverse outcome pathway' OR 'biomedical knowledge graph')"
    # name_of_query = 'language_model_OR_natural_language_processing_AND_adverse_outcome_pathway_OR_biomedical_knowledge_graph'
    # query = "('artificial intelligence' OR 'language model' OR 'natural language processing') AND ('adverse outcome pathway' OR 'biomedical knowledge graph')"
    # query = "('text-mining' OR 'artificial intelligence' OR 'language model' OR 'natural language processing') AND ('adverse outcome pathway' OR 'biomedical knowledge graph')"
    query = "('text-mining' OR 'language model' OR 'natural language processing') AND ('adverse outcome pathway')"
    name_of_query = 'text-mining_OR_language_model_OR_natural_language_processing_AND_adverse_outcome_pathway'
    print('Searching NCBI for:', query)
    listy = ['language model', 'natural language processing', 'adverse outcome pathway', 'biomedical knowledge graph', 'artificial intelligence', 'text-mining', 'relation extraction', 'name entity', 'key events', 'event relationship', 'tox', 'artificial intelligence', 'literature', 'existing literature', 'NLP', 'LLMs', 'text-mining', 'text mining', 'fine-tuning', 'mask', 'knowledge', 'network', 'graph', 'toxicology', 'steatosis', 'Entity Recognition', 'Relation Extraction', 'Key Events', 'Event Relationship']

    df = pd.read_csv('data/query_and_hits_NCBI.csv')
    print('active search on ncbi is off!\n(To turn it on either uncommand the part below this print statement or rerun this script and choose n at the first question)')
    # print('active search is on!')
    # pubmed_ids = search_ncbi(query)
    # new_row = {'Query': query, 'Hits': len(pubmed_ids), 'Date': time.strftime("%Y-%m-%d %H:%M:%S"),
    #            'Pubmed_ids': pubmed_ids}
    # table_of_query_n_hits = pd.concat([df, pd.DataFrame([new_row])])
    # table_of_query_n_hits.to_csv('data/query_and_hits_NCBI.csv', index=False)
    # table_of_query_n_hits.to_excel('data/query_and_hits_NCBI.xlsx', index=False)


elif use_example == 'n':
    query = input("Please enter a query:\ne.g.\n('text-mining' OR 'language model' OR 'natural language processing') AND ('adverse outcome pathway')\n")
    name_of_query = input("Please enter a name for the query (no spaces):\ne.g.\ntext-mining_OR_language_model_OR_natural_language_processing_AND_adverse_outcome_pathway\n")
    listx = input("Lastly, please enter a list of terms to highlight in the title or abstract separated by commas:\ne.g.\nlanguage model, natural language processing, adverse outcome pathway, biomedical knowledge graph, artificial intelligence, text-mining\n")
    listy = listx.split(', ')
    print('active search is on!')
    if not os.path.exists('data/query_and_hits_NCBI.csv'):
        df = pd.DataFrame()
    else:
        df = pd.read_csv('data/query_and_hits_NCBI.csv')
    pubmed_ids = search_ncbi(query)
    new_row = {'Query': query, 'Hits': len(pubmed_ids), 'Date': time.strftime("%Y-%m-%d %H:%M:%S"), 'Pubmed_ids': pubmed_ids}
    table_of_query_n_hits = pd.concat([df, pd.DataFrame([new_row])])
    table_of_query_n_hits.to_csv('data/query_and_hits_NCBI.csv', index=False)
    table_of_query_n_hits.to_excel('data/query_and_hits_NCBI.xlsx', index=False)
    print('Query and hits saved to data/query_and_hits_NCBI.csv and data/query_and_hits_NCBI.xlsx')


# df = pd.read_csv('./data/query_and_hits_NCBI.csv')
# print('active search on ncbi is off!')
# to turn on uncomment the following lines:
# print('active search is on!')
# pubmed_ids = search_ncbi(query)
# new_row = {'Query': query, 'Hits': len(pubmed_ids), 'Date': time.strftime("%Y-%m-%d %H:%M:%S"), 'Pubmed_ids': pubmed_ids}
# table_of_query_n_hits = pd.concat([df, pd.DataFrame([new_row])])
# table_of_query_n_hits.to_csv('../review_query/query_and_hits_NCBI.csv', index=False)
# table_of_query_n_hits.to_excel('../review_query/query_and_hits_NCBI.xlsx', index=False)

print(name_of_query)
print(listy)

df = pd.read_csv('data/query_and_hits_NCBI.csv')
col = 'Pubmed_ids'
pubmed_ids = col_to_list(query, 'data/query_and_hits_NCBI.csv', col)
addition = f'_{name_of_query}_{len(pubmed_ids)}_articles'
count = 0
outputfolder = './data/'

for pubmed_id in pubmed_ids:
    count += 1

    checked_articles = []
    included_file = os.path.join(outputfolder, 'included_articles_aop.csv')
    excluded_file = os.path.join(outputfolder, 'excluded_articles_aop.csv')

    if os.path.exists(included_file) and os.path.getsize(included_file) > 0:
        included_df = pd.read_csv(included_file)
        included_articles = included_df.to_dict('records')
        checked_articles.extend(included_df['pubmed_id'].astype(str).values)  # Ensure all IDs are strings
    else:
        included_articles = []

    if os.path.exists(excluded_file) and os.path.getsize(excluded_file) > 0:
        excluded_df = pd.read_csv(excluded_file)
        excluded_articles = excluded_df.to_dict('records')
        checked_articles.extend(excluded_df['pubmed_id'].astype(str).values)  # Ensure all IDs are strings
    else:
        excluded_articles = []

    if str(pubmed_id) in checked_articles:
        print(f"Article {pubmed_id} already reviewed.")
        continue
    idstodo = len(pubmed_ids) - len(checked_articles)
    print(f"+---------------------------+\n|   Processing paper {count}/{len(pubmed_ids)}   |\n+---------------------------+")

    download_df = check_if_one_is_downloadable2(pubmed_id, addition)
    download_df['pmc_id'] = str(download_df['pmc_id']).replace('None', 'not available')
    if not download_df['pmc_id'].values[0]:
        download_df.at[0, 'pmc_id'] = 'not available'

    pmc_id = download_df['pmc_id'].values[0]
    title = download_df['title'].values[0]
    abstract = download_df['abstract'].values[0]
    url = download_df['url'].values[0]

    search_terms = listy #+ ['tox', 'artificial intelligence', 'literature', 'existing literature', 'NLP', 'LLMs', 'text-mining', 'text mining', 'fine-tuning', 'mask', 'knowledge', 'network', 'graph', 'toxicology', 'steatosis', 'Entity Recognition', 'Relation Extraction', 'Key Events', 'Event Relationship']
    print(f"\nReviewing article {count} of {idstodo} (from {len(pubmed_ids)} in total):")
    search_terms_file_name = '_'.join(search_terms)
    highlighted_title = highlight_terms(title, search_terms)
    highlighted_abstract = highlight_terms(abstract, search_terms)

    print(f"Title: {highlighted_title}")
    print(f"\nAbstract: {highlighted_abstract}")
    print(f"\nURL: {url}")

    #! 9th of july is query without text-mining and AI!!!!
    pubmed_id, automatic_screen, reason_auto = filter_articles3(pubmed_id=pubmed_id, search_terms=search_terms, file_name='09-July-2024')
    print(f"\nAutomatic screening for pubmed ID: {pubmed_id}, gave the following result:\n\n{automatic_screen.upper()} \n")#because {reason_auto}.\n")
    # Ask for relevance
    relevance = input(
        "Does this article focus on AOP or BKG generation or detection from existing literature, by employing AI, LLMs or NLP? (y/n/p(artly)): ").strip().lower()

    if relevance == 'n':
        excluded_articles.append({
            'title': title,
            'pubmed_id': pubmed_id,
            'url': url,
            'abstract': abstract,
            'automatic_screening': automatic_screen,
            'automatic_reason': reason_auto,
            'manual_screen': 'excluded, does not concern AI, LLM or NLP for BKGs or AOPs based on existing literature.'
        })
        column_order = [
            'title', 'pubmed_id', 'url', 'abstract', 'automatic_screening', 'automatic_reason', 'manual_screen',
            'category', 'aim', 'methods', 'data_sources', 'main_findings', 'limitations', 'additional_comments', 'relevant_sentences',
            'what2write', 'bib_text', 'citation_key', 'doi'
        ]
        included_df = pd.DataFrame(included_articles, columns=column_order)
        excluded_df = pd.DataFrame(excluded_articles, columns=[
            'title', 'pubmed_id', 'url', 'abstract', 'automatic_screening', 'automatic_reason', 'manual_screen'
        ])
        included_df.to_csv(included_file, index=False)
        excluded_df.to_csv(excluded_file, index=False)
        print("Results saved to 'included_articles.csv' and 'excluded_articles.csv'.\n\n")

    elif relevance == 'p':
        print("Article marked as pending/partly.")
        doi = download_df['doi'].values[0]
        pub_date = download_df['pub_date'].values[0]
        journal_title = download_df['journal_title'].values[0]
        pmc_id = download_df['pmc_id'].values[0]
        authors = download_df['authors'].values[0]
        bib_text, pubmed_to_citekey = get_bib(download_df)

        citekey = pubmed_to_citekey[pubmed_id]
        additional_comments = input("Please provide additional comments (why not yes?): ")
        included_articles.append({
            'title': title,
            'pubmed_id': pubmed_id,
            'url': url,
            'abstract': abstract,
            'automatic_screening': automatic_screen,
            'automatic_reason': reason_auto,
            'manual_screen': 'pending/partly',
            'category': 'pending/partly',
            'aim': 'pending/partly',
            'methods': 'pending/partly',
            'data_sources': 'pending/partly',
            'main_findings': 'pending/partly',
            'limitations': 'pending/partly',
            'additional_comments': additional_comments,
            'relevant_sentences': 'pending/partly',
            'bib_text': bib_text,
            'citation_key': citekey,
            'What2write': 'pending/partly',
            'doi': doi,
        })
        column_order = [
            'title', 'pubmed_id', 'url', 'abstract', 'automatic_screening', 'automatic_reason', 'manual_screen',
            'category', 'aim', 'methods', 'data_sources', 'main_findings', 'limitations', 'additional_comments', 'relevant_sentences',
            'what2write', 'bib_text', 'citation_key', 'doi'
        ]
        included_df = pd.DataFrame(included_articles, columns=column_order)
        excluded_df = pd.DataFrame(excluded_articles, columns=[
            'title', 'pubmed_id', 'url', 'abstract', 'automatic_screening', 'automatic_reason', 'manual_screen'
        ])
        included_df.to_csv(included_file, index=False)
        excluded_df.to_csv(excluded_file, index=False)
        print("Results saved to 'included_articles.csv' and 'excluded_articles.csv'.\n\n")

    elif relevance == 'y':
        print('Note: sentences in both the "relevant citations" and "what2write" fields should be separated by two dots ".."\n')
        doi = download_df['doi'].values[0]
        print(f'https://doi.org/{doi}\n')
        publisher_from_doi = fetch_publisher_by_doi(doi)
        print(f"Publisher from DOI: {publisher_from_doi}")
        dfdash = process_submitted_data(pubmed_id, download_df, url)
        print(dfdash)
        for i, row in dfdash.iterrows():
            category = row['Category (LLM/NLP, BKG/AOP, tox, lit)']
            aim = row['Aim of the study']
            methods = row['Methods used']
            data_sources = row['Data sources used']
            main_findings = row['Main findings']
            limitations = row['Limitations']
            additional_comments = row['Additional comments (e.g. specific technique/type of NLP, validation method, usefulness in AOP&BKG)']
            # doi = download_df['doi'].values[0]
            # print(doi)
            if doi == 'Not found':
                doi = input('The DOI was not found. Please enter the DOI: ')
                download_df.at[0, 'doi'] = doi
            rel_sentences = row['Relevant citations'].split('..')
            rel_sentence_dict = {}
            # print(rel_sentences)
            for sentence in rel_sentences:
                print(sentence)
                sentence.replace('.\\n', '')
                if 'PMC' in url:
                    highlighingurl = create_highlighted_url2(pubmed_id, sentence, url)
                else:
                    # doi = download_df['doi'].values[0]
                    # print(doi)
                    # if doi == 'Not found':
                    #     doi = input('The DOI was not found. Please enter the DOI: ')
                    full_doi = f'doi_{doi}'
                    highlighingurl = create_highlighted_url2(publisher_from_doi, sentence, full_doi)
                print(highlighingurl)
                print('\n')
            #     pmc_id_2 = str(download_df['pmc_id'].values[0]).strip().replace(' ', '').replace('0', '').replace(
            #         '\nName:pmc_id,dtype:object', '')
            #
            #     highlighted_url = create_highlighted_url(pubmed_id, sentence, pmc_id_2)
                rel_sentence_dict[sentence] = highlighingurl
            what2write = row['What2write']

            bib_text, pubmed_to_citekey = get_bib(download_df)
            citekey = pubmed_to_citekey[pubmed_id]
            doi = download_df['doi'].values[0]

            included_articles.append({
                'title': title,
                'pubmed_id': pubmed_id,
                'url': url,
                'abstract': abstract,
                'automatic_screening': automatic_screen,
                'automatic_reason': reason_auto,
                'manual_screen': 'included, does concern text-mining, LLM or NLP for BKGs or AOPs based on existing literature.',
                'category': category,
                # 'category_citation': category_citation,
                'aim': aim,
                # 'aim_citation': aim_citation,
                'methods': methods,
                # 'methods_citation': methods_citation,
                'data_sources': data_sources,
                # 'data_sources_citation': data_sources_citation,
                'main_findings': main_findings,
                # 'main_findings_citation': main_findings_citation,
                'limitations': limitations,
                # 'limitations_citation': limitations_citation,
                'additional_comments': additional_comments,
                # 'additional_comments_citation': additional_comments_citation,
                'relevant_sentences': rel_sentence_dict,
                'what2write': what2write,
                # 'what2write_citations': used_citations,
                'bib_text': bib_text,
                'citation_key': citekey,
                'doi': doi,
            })


        column_order = [
            'title', 'pubmed_id', 'url', 'abstract', 'automatic_screening', 'automatic_reason', 'manual_screen',
            'category', 'aim', 'methods', 'data_sources', 'main_findings', 'limitations', 'additional_comments', 'relevant_sentences',
            'what2write', 'bib_text', 'citation_key', 'doi'
        ]

        included_df = pd.DataFrame(included_articles, columns=column_order)
        excluded_df = pd.DataFrame(excluded_articles, columns=[
            'title', 'pubmed_id', 'url', 'abstract', 'automatic_screening', 'automatic_reason', 'manual_screen'
        ])

        if included_df.empty:
            included_df = pd.DataFrame(
                columns=['title', 'pubmed_id', 'url', 'abstract', 'automatic_screening', 'automatic_reason', 'manual_screen', 'category', 'aim', 'methods', 'data_sources', 'main_findings', 'limitations', 'additional_comments', 'relevant_sentences','what2write', 'bib_text', 'citation_key', 'doi'])
        if excluded_df.empty:
            excluded_df = pd.DataFrame(
                columns=['title', 'pubmed_id', 'url', 'abstract', 'automatic_screening', 'automatic_reason',
                         'manual_screen'])

        to_add2review = str(what2write).split('..')
        print(bib_text)
        print('\n')
        for line in to_add2review:
            sen = line + ' \\cite{' + citekey + '}.'
            print(sen)
        ready = input("Press Enter to continue to the next article. (or press ctrl + C to exit)")
        if ready == 'q':
            break
        if not ready:
            remove_submitted_data_file()

            included_df.to_csv(included_file, index=False)
            excluded_df.to_csv(excluded_file, index=False)
            print("Results saved to 'included_articles.csv' and 'excluded_articles.csv'.\n\n")
            continue




print('All done! :D')

'''
(btw use ctrl + click to open in new tab or shift + click to open in new window)
newest version
'''
