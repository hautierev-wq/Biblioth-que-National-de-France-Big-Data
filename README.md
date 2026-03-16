# Biblioth-que-National-de-France-Big-Data
This repository will let you explore the French National Library Database (abbriviated as BnF).  Through statistical analysis and visualizations, the goal is to have a better understanding of the library's database contents and what it underlines. 

All the information was extracted from the BnF SparQL Api endpoint (https://data.bnf.fr/sparql/) and then formalized into visualizations using python.

We used 6 different vocabularies from the Bnf : 
- Dublin Core terms, or dcterms, handles the core bibliographic fields. 
- FOAF describes persons and organisations.
- SKOS is the backbone of the RAMEAU subject thesaurus — that's the BnF's own controlled vocabulary with over 21 million concept records.
- MARC Relators from the Library of Congress captures roles: marcrel:aut for author, marcrel:trl for translator, marcrel:ill for illustrator, and so on.
- RDA connects works to their manifestations.
- Bnf-onto is the BnF's own proprietary namespace for fields like ISBN numbers, first publication year, and ARK identifiers.
