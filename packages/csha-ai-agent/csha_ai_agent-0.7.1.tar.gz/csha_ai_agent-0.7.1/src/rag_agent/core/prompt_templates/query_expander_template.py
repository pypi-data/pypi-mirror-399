# QUERY_EXPAND_TEMPLATE = """
#     You are now a query expander model.

#     Instructions: 
#     1. Expand the acronyms that are not related to California Health in the query
#     2  For acronyms related to California Health, refer to acronym glossary below. If the acronym is not in the glossary, expand the acronym in the context of California Health if you know the acronym is valid. 
#     3. Expand entities into every possible form. An entity is a person, title, named organization, location, country, etc. Names, first names, last names, surnames, names of someone, countries are entities. Nationalities are entities even if they are adjectives. Sports, sporting events, adjectives, verbs, numbers, adverbs, abstract concepts, sports, are not entities. Dates, years and times are not entities.
#     4. Remove any stop words from the query (e.g. a, an, the, to,etc.). Remove CSHA or California School-Based Health Alliance as a stopword(s) from the query.
#     5. Add OR between each word in the query.

#     Acronym glossary:
#     ```
#     V2R: vision reality
#     SBHC: school-based health center
#     WC: wellness center
#     FQHC: federally qualified health center
#     LCFF: local control funding formula
#     ```

#     Query:
#     ```{query}```
    
#     Example 1:
#     Input:
#     Who is the ED of CSHA?
#     Output: 
#     Executive OR Director

#     Example 2:
#     Input:
#     What is an SBHC?
#     Output:
#     school-based OR health center OR SBHC 

#     Example 3:
#     Input:
#     What is V2R?
#     Output:
#     vision OR reality OR V2R

#     Example 4:
#     Input:
#     When is the next conference?
#     Output:
#     conference

#     Example 5:
#     Input:
#     What is the WC?
#     Output:
#     wellness center OR WC
# """

QUERY_EXPAND_TEMPLATE = """
    You are now a query expander model.

    Instructions: 
    1. Expand the acronyms that are not related to California Health in the query
    2  For acronyms related to California Health, refer to acronym glossary below. If the acronym is not in the glossary, expand the acronym in the context of California Health if you know the acronym is valid. 
    3. Expand entities into every possible form. An entity is a person, title, named organization, location, country, etc. Names, first names, last names, surnames, names of someone, countries are entities. Nationalities are entities even if they are adjectives. Sports, sporting events, adjectives, verbs, numbers, adverbs, abstract concepts, sports, are not entities. Dates, years and times are not entities.
    4. Remove any stop words from the query (e.g. a, an, the, to,etc.). 

    Acronym glossary:
    ```
    V2R: vision reality
    SBHC: school-based health center
    WC: wellness center
    FQHC: federally qualified health center
    LCFF: local control funding formula
    ```

    Query:
    ```{query}```
    
    Example 1:
    Input:
    Who is the ED of CSHA?
    Output: 
    csha executive director

    Example 2:
    Input:
    What is an SBHC?
    Output:
    school-based health center sbhc 

    Example 3:
    Input:
    What is V2R?
    Output:
    vision reality v2r

    Example 4:
    Input:
    When is the next conference?
    Output:
    conference

    Example 5:
    Input:
    What is the WC?
    Output:
    wellness center wc
"""