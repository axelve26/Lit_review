import pandas as pd
import os
import sys
df = pd.read_csv('./data/included_articles_all.csv')
# def search_cite(df, key):
#     for i, row in df.iterrows():
#         if row['citation_key'] == key:
#             print(row)
#             print(row['relevant_sentences'])
#             return row['relevant_sentences']
#
# key = 'Marie_Corradi_The_2024'
# cited = search_cite(df, key)
#
# def search_author_date(df, author, publication_date):
#     for i, row in df.iterrows():
#         if author in row['citation_key']:
#             if publication_date in row['citation_key']:
#                 print('\nText in review:')
#                 print(row['what2write'])
#                 print('\n\n\n\n')
#                 citations = row['relevant_sentences'].split('\', \'')
#                 for citation in citations:
#                     print(citation)
#                     print('\n')
#                 return row['relevant_sentences']
#
#
# author = 'Jaylet'
# date = '2023'
# cited = search_author_date(df, author, date)

def search_title(df, title):
    for i, row in df.iterrows():
        if title in row['title']:
            print('\nText in review:')
            print(row['what2write'])
            print('\n\n\n\n')
            citations = row['relevant_sentences'].split('\', \'')
            for citation in citations:
                citation_link = citation.split('\': \'')
                citation, link = citation_link[0], citation_link[1]
                print(citation)
                print('Original link:')
                print(link)
                if 'sciencedirect' in link:
                    link2 = link.replace('https://www.sciencedirect.com', 'https://www.sciencedirect-com.ezproxy.leidenuniv.nl')
                    print('Leiden eproxy link:')
                    if '-' in link2:
                        link2 = link2.replace('-', '%2D')
                    print(link2)
                print('\n')
            # return row['relevant_sentences']

title = 'Deciphering Adverse Outcome Pathway Network Linked to Bisphenol F Using Text Mining and Systems Toxicology Approaches.'

'''
Nota bene: when using the leiden eproxy link, you should first open a paper in Chrome through that eproxy before the links to the marked text work.
'''


cited = search_title(df, title)
