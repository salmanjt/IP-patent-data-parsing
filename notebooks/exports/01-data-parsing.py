# %% [markdown]
# # Parsing Intellectual Property Patent Grants
# 
# **Author:** Salman Tahir  
# **Environment:** Conda 23.7.2, Python 3.10.12
# 

# %% [markdown]
# ---
# 

# %% [markdown]
# **Table of contents**<a id='toc0_'></a>
# 
# -   [Introduction](#toc2_)
# -   [Importing Libraries](#toc3_)
# -   [Examining Patent Files](#toc4_)
#     -   [Structure of the Data](#toc4_1_)
#     -   [Identifying Patterns & Formulating RegEx](#toc4_2_)
# -   [Loading and Parsing Files](#toc5_)
#     -   [Defining Regular Expressions](#toc5_1_)
#     -   [Preparing the Data](#toc5_2_)
#     -   [Parsing the Data](#toc5_3_)
#     -   [Creating a DataFrame](#toc5_4_)
# -   [Outputting Files](#toc6_)
#     -   [Writing to CSV](#toc6_1_)
#     -   [Writing to JSON](#toc6_2_)
#     -   [Verifying Outputs](#toc6_3_)
# -   [Summary](#toc7_)
# -   [References](#toc8_)
# 
# <!-- vscode-jupyter-toc-config
# 	numbering=false
# 	anchor=true
# 	flat=false
# 	minLevel=1
# 	maxLevel=2
# 	/vscode-jupyter-toc-config -->
# <!-- THIS CELL WILL BE REPLACED ON TOC UPDATE. DO NOT WRITE YOUR TEXT IN THIS CELL -->
# 

# %% [markdown]
# # <a id='toc2_'></a>[Introduction](#toc0_)
# 
# In this project, we parse and pre-process a raw text file into a structured format to prepare it for downstream analysis.
# 
# -   The objective is to extract data from the raw text file containing information about grants given for Intellectual Property (IP) patent claims.
# -   Regular expressions are used for pattern matching and extraction of relevant data from the dataset.
# -   The resulting data is then output to CSV and JSON file formats.
# 

# %% [markdown]
# # <a id='toc3_'></a>[Importing Libraries](#toc0_)
# 
# The following libraries are used in this project:
# 
# -   `re`: to define and use regular expressions for pattern matching.
# -   `pandas`: to create DataFrame objects and manipulate data.
# 

# %%
import re
import pandas as pd


# %% [markdown]
# # <a id='toc4_'></a>[Examining Patent Files](#toc0_)
# 

# %% [markdown]
# ## <a id='toc4_1_'></a>[Structure of the Data](#toc0_)
# 
# The first step is to examine our raw text file and understand the structure of the data.
# 
# From visual inspection of the data, we can conclude the following:
# 
# -   The XML declaration on the first line tells us, the text file contains XML data with an encoding of `UTF-8`.
# -   We can see the XML declaration: `<?xml version="1.0" encoding="UTF-8"?>` occurs multiple times in the data.
# -   This tells us the text file contains multiple XML documents, where each document is separated by the XML declaration.
# 
# Therefore, we define a function called `count_xml_docs` to count the number of XML documents in the text file.
# 
# -   The function argument is the path to our text file.
# -   We separate the XML documents by the XML declaration.
# -   We then count and return the number of documents in the text file.
# 

# %%
# Define the file path to our text file
FILE_PATH = '../data/input/patent_grants_data.txt'


# %%
def count_xml_docs(file_path):
    """
    Reads the text file returns the number of XML documents in the file.
    :param file_path: path to assignment text file
    :return: number of XML documents in the text file
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        docs = text.split('<?xml version="1.0" encoding="UTF-8"?>')[1:]

    return len(docs)


# Path to our text file
num_docs = count_xml_docs(FILE_PATH)

# Print the number of XML documents in the text file
print(f'Total number of XML documents: {num_docs}')


# %% [markdown]
# ## <a id='toc4_2_'></a>[Identifying Patterns & Formulating RegEx](#toc0_)
# 
# Now that we have a better understanding of the structure of our dataset, we can identify patterns in the data that will help us extract the relevant information.
# 
# We are given the following information about the data we need to extract:
# 
# 1. **grant_id**: a unique ID for a patent grant consisting of alphanumeric characters.
# 2. **patent_kind**: a category to which the patent grant belongs.
# 3. **patent_title**: a title given by the inventor(s) to the patent claim.
# 4. **number_of_claims**: an integer denoting the number of claims for a given grant.
# 5. **citations_examiner_count**: an integer denoting the number of citations made by the
#    examiner for a given patent grant (use 0 if None).
# 6. **citations_applicant_count**: an integer denoting the number of citations made by the
#    applicant for a given patent grant (use 0 if None).
# 7. **inventors**: a list of the patent inventors’ names (use [NA] if the value is Null).
# 8. **claims_text**: a list of claim texts for the different patent claims (use [NA] if the value
#    is Null).
# 9. **abstract**: the patent abstract text (use ‘NA’ if the value is Null).
# 

# %% [markdown]
# ### 🔵 Identifying the `grant_id`
# 
# By looking at the XML documents in the text file we can conclude the following:
# 
# -   The XML document contains a root element `<us-patent-grant>`.
# -   The root element has a set of attributes of which the one we are interested in has the format `file="US10361423-20190723.XML"`.
# 
# By examining the sample files and using the information we have gathered so far, we can identify the `grant_id` in the `file` attribute of the root element `<us-patent-grant>`.
# 
# The format of the ID is `CC-<8-digit number>-<date>` <sup>[1]</sup> where:
# 
# -   The `CC` is a two-letter ISO country code.
# -   The `<8-digit number>` is the patent number. <sup>[2]</sup>
#     -   The patent number may include up to eight characters, depending on the type of patent.
#     -   For example, a utility patent number may include up to eight characters, whereas a Reissue patent number includes `RE` followed by 6 digits. Therefore, we need to account for this in our regular expression.
# -   The `<4-digit year>-<2-digit month>-<2-digit day>` is assumed to be the date on which the patent was granted.
# 
# Now, by examining the sample outputs provided, we can identify that we only require the `CC-<8-digit number>` part of the `file` attribute therefore, we can use the following regular expression to extract the `grant_id`:
# 
# ```python
# r'<us-patent-grant.*?file="([A-Z]{2}(?:[A-Z]{1,2})?\d+).*?\.XML".*?>'
# ```
# 
# **Explanation of the regular expression:**
# 
# -   `<us-patent-grant.*?>`: matches the opening tag of the root element `<us-patent-grant>`.
# -   `.*?`: matches any characters between the opening tag of the root element and the `file` attribute.
# -   `file="`: matches the `file` attribute.
# -   `([A-Z]{2}(?:[A-Z]{1,2})?\d+)`: our capturing group that matches the `CC-<8-digit number>` part of the `file` attribute.
#     -   Here, using a non-capturing group, we also account that the 8 digit number may include some characters depending on the type of patent.
# -   `.*?`: matches any characters between the `CC-<8-digit number>` part of the `file` attribute and the `.XML"` part of the `file` attribute.
# -   `\.XML"`: is a literal match of the `.XML"` part of the `file` attribute.
# -   `.*?>`: matches any characters between the `.XML"` part of the `file` attribute and the closing tag of the root element `<us-patent-grant>`
# 

# %% [markdown]
# ### 🔵 Identifying the `patent_kind` or `kind`
# 
# By observing the sample outputs provided, we can conclude that the `patent_kind` is the value of the `kind` tag located inside the tag `<publication-reference>` element.
# 
# Although, there are a few things to note:
# 
# -   In the sample output, the `patent_kind` attribute column is named as `kind` therefore we will use the same name as in the sample output to avoid confusion.
# -   Secondly, in the sample output provided, the value of the `kind` tag is not a code but a description of the patent kind therefore, we will reference the IP Australia website to identify the USPTO kind codes for each patent kind. <sup>[3]</sup>
# 
# Hence, we can use the following regular expression to extract the `kind`:
# 
# ```python
# r'<publication-reference>.*?<kind>(\w{1,2})</kind>.*?</publication-reference>'
# ```
# 
# **Explanation of the regular expression:**
# 
# -   `<publication-reference>`: matches the opening tag of the `<publication-reference>` element.
# -   `.*?`: matches any characters between the opening tag of the `<publication-reference>` element and the `<kind>` tag.
# -   `<kind>`: matches the opening tag of the `<kind>` tag.
# -   `(\w{1,2})`: our capturing group that matches the value of the `<kind>` tag.
#     -   Note that we have identified the value of the `<kind>` tag can be a maximum of 2 characters and a minimum of 1 character.
# -   `</kind>`: matches the closing tag of the `<kind>` tag.
# -   `.*?`: matches any characters between the closing tag of the `<kind>` tag and the closing tag of the `<publication-reference>` element.
# -   `</publication-reference>`: matches the closing tag of the `<publication-reference>` element.
# 

# %% [markdown]
# ### 🔵 Identifying the `patent_title`
# 
# By observing the sample input and output files we can conclude that the `patent_title` is the value of the `<invention-title>` element.
# 
# Although, there are a few things to note:
# 
# -   Any HTML entities present in the title need to be decoded to their unicode equivalent or be removed.
# -   These changes will be accounted for in the statement for the `patent_title`.
# 
# Hence, we can use the following regular expression to extract the `patent_title`:
# 
# ```python
# r'<invention-title id=\".*?\">(.*?)</invention-title>'
# ```
# 
# **Explanation of the regular expression:**
# 
# -   `<invention-title id=".*?">`: matches the opening tag of the `<invention-title>` element.
#     -   Note that we are not interested in capturing the value of the `id` attribute.
# -   `(.*?)`: our capturing group that matches the value of the `<invention-title>` tag.
# -   `</invention-title>`: matches the closing tag of the `<invention-title>` element.
# 

# %% [markdown]
# ### 🔵 Identifying the `number_of_claims`
# 
# By observing the sample input and output files we can conclude the following:
# 
# -   The `number_of_claims` is the value of the `<number-of-claims>` element.
# -   The `<number-of-claims>` value is an integer.
# 
# Hence, we can use the following regular expression to extract the `number_of_claims`:
# 
# ```python
# r'<number-of-claims>(\d+)</number-of-claims>'
# ```
# 
# **Explanation of the regular expression:**
# 
# -   `<number-of-claims>`: matches the opening tag of the `<number-of-claims>` element.
# -   `(\d+)`: our capturing group that matches the value of the `<number-of-claims>` tag.
# -   `</number-of-claims>`: matches the closing tag of the `<number-of-claims>` element.
# 

# %% [markdown]
# ### 🔵 Identifying the `citations_examiner_count`
# 
# By observing the sample files and our input file we can conclude the following:
# 
# -   There is no specific count given for the number of citations broken down by examiner.
# -   To get the count of citations by examiner we search for all occurrences of the `<category>` element with a value of `"cited by examiner"`
# 
# Hence, we can use the following regular expression to extract the `citations_examiner_count`:
# 
# ```python
# r'<category>cited by examiner<\/category>'
# ```
# 
# **Explanation of the regular expression:**
# 
# -   `<category>`: matches the opening tag of the `<category>` element.
# -   `cited by examiner`: matches the value of the `<category>` element.
# -   `</category>`: matches the closing tag of the `<category>` element.
# 
# We will then use the len() function to count the number of times the regular expression matches.
# 

# %% [markdown]
# ### 🔵 Identifying the `citations_applicant_count`
# 
# Similarly to the `citations_examiner_count`, we can conclude the following from observing the sample files and our input file:
# 
# -   There is no specific count given for the number of citations broken down by applicant.
# -   To get the count of citations by applicant we search for all occurrences of the `<category>` element with a value of `"cited by applicant"`
# 
# Hence, we can use the following regular expression to extract the `citations_applicant_count`:
# 
# ```python
# r'<category>cited by applicant<\/category>'
# ```
# 
# **Explanation of the regular expression:**
# 
# -   `<category>`: matches the opening tag of the `<category>` element.
# -   `cited by applicant`: matches the value of the `<category>` element.
# -   `</category>`: matches the closing tag of the `<category>` element.
# 
# We will then use the len() function to count the number of times the regular expression matches.
# 

# %% [markdown]
# ### 🔵 Identifying the `inventors`
# 
# By observing the sample input and output files we conclude the following:
# 
# -   `inventors` is a list of the patent inventors' names.
# -   In the sample output, the format is `"[<first name> <last name>,<first name> <last name>,...]"`
# 
# Therefore, we first extract all information in the `<inventors>` element using the following regular expression:
# 
# ```python
# r'<inventors>.*?</inventors>'
# ```
# 
# **Explanation of the regular expression:**
# 
# -   `<inventors>`: matches the opening tag of the `<inventors>` element.
# -   `.*?`: matches any characters between the opening tag of the `<inventors>` element and the closing tag of the `<inventors>` element.
# -   `</inventors>`: matches the closing tag of the `<inventors>` element.
# 
# Then, we use the following regular expressions to extract the `first_name` and `last_name` from within the `<addressbook>` element inside the parent `<inventor>` element:
# 
# ```python
# r'<inventor[^>]*>\s*<addressbook>\s*<last-name>([^<]*)<\/last-name>\s*<first-name>([^<]*)<\/first-name>'
# ```
# 
# **Explanation of the regular expression:**
# 
# -   `<inventor[^>]*>`: matches the opening tag of the `<inventor>` element.
# -   `\s*`: matches any whitespace characters.
# -   `<addressbook>`: matches the opening tag of the `<addressbook>` element.
# -   `\s*`: matches any whitespace characters.
# -   `<last-name>`: matches the opening tag of the `<last-name>` element.
# -   `([^<]*)`: our first capturing group that matches the value of the `<last-name>` tag.
# -   `</last-name>`: matches the closing tag of the `<last-name>` element.
# -   `\s*`: matches any whitespace characters.
# -   `<first-name>`: matches the opening tag of the `<first-name>` element.
# -   `([^<]*)`: our second capturing group that matches the value of the `<first-name>` tag.
# -   `</first-name>`: matches the closing tag of the `<first-name>` element.
# 

# %% [markdown]
# ### 🔵 Identifying the `claims_text`
# 
# Each XML document in the text file has a `<claims>` element inside which there can be multiple `<claim-text>` elements.
# We can first extract all occurrences of the `<claims>` element along with its contents using the following regular expression:
# 
# ```python
# r'<claims id="claims">.*?<\/claims>'
# ```
# 
# **Explanation of the regular expression:**
# 
# -   `<claims id="claims">`: matches the opening tag of the `<claims>` element.
# -   `.*?`: matches any characters between the opening tag of the `<claims>` element and the closing tag of the `<claims>` element.
# -   `</claims>`: matches the closing tag of the `<claims>` element.
# 
# The resulting list consists of all non-overlapping matches of the regular expression, which gives us a list of strings containing the `<claims>` element and its contents. Now, for each string in the list, we can extract the `<claim-text>` element using the following regular expression:
# 
# ```python
# r'<claim-text>(.*?)<\/claim-text>'
# ```
# 
# **Explanation of the regular expression:**
# 
# -   `<claim-text>`: matches the opening tag of the `<claim-text>` element.
# -   `(.*?)`: our capturing group that matches the value of the `<claim-text>` tag.
# -   `</claim-text>`: matches the closing tag of the `<claim-text>` element.
# 
# Finally, we can use list comprehension to apply the second regular expression to each string in the list obtained from the first regular expression.
# 

# %% [markdown]
# ### 🔵 Identifying the `abstract`
# 
# By observing the sample input and output files we know:
# 
# -   The abstract is the value contained within the `<abstract>` element.
# -   The abstract is a single string.
# -   The abstract is not always present in the XML document, therefore we can use NA to represent the absence of the abstract.
# 
# Hence, we can use the following regular expression to extract the `abstract`:
# 
# ```python
# r'<abstract[^>]*>\s*<p[^>]*>(.*?)<\/p>\s*<\/abstract>'
# ```
# 
# **Explanation of the regular expression:**
# 
# -   `<abstract[^>]*>`: matches the opening tag of the `<abstract>` element.
#     -   The inclusion of [^>]\* indicates that it matches any number of characters that are not `>` between the opening `<abstract` tag and the closing `>` of that tag
# -   `\s*`: matches any whitespace characters.
# -   `<p[^>]*>`: matches the opening tag of the `<p>` element.
#     -   The inclusion of [^>]\* indicates that it matches any number of characters that are not `>` between the opening `<p` tag and the closing `>` of that tag
# -   `(.*?)`: our capturing group that matches the value of the `<p>` tag.
# -   `</p>`: matches the closing tag of the `<p>` element.
# -   `\s*`: matches any whitespace characters.
# -   `</abstract>`: matches the closing tag of the `<abstract>` element.
# 

# %% [markdown]
# # <a id='toc5_'></a>[Loading and Parsing Files](#toc0_)
# 
# Now that we have identified the patterns in the data, we can proceed with loading and parsing the files.
# 

# %% [markdown]
# ## <a id='toc5_1_'></a>[Defining Regular Expressions](#toc0_)
# 
# Here, we define the regular expressions, identified in the previous section, as variables.
# 
# We use `re.compile()` to compile the regular expressions into pattern objects, which is a more efficient way of using regular expressions in since Python won't need to recompile the regular expressions each time they are used in the loop.
# 
# We will use UPPER_CASE for the names of the regular expressions to indicate that they are constants as per the Python naming convention. <sup>[4]</sup>
# 

# %%
# Regex for extracting the grant ID
GRANT_ID_PATTERN = re.compile(
    r'<us-patent-grant.*?file="([A-Z]{2}(?:[A-Z]{1,2})?\d+).*?\.XML".*?>', flags=re.DOTALL)

# Regex for extracting the patent kind
KIND_PATTERN = re.compile(
    r'<publication-reference>.*?<kind>(\w{1,2})</kind>.*?</publication-reference>', flags=re.DOTALL)

# Regex for extracting the patent title
PATENT_TITLE_PATTERN = re.compile(
    r'<invention-title id=\".*?\">(.*?)</invention-title>', flags=re.DOTALL)

# Regex for extracting the number of claims
NUMBER_OF_CLAIMS_PATTERN = re.compile(
    r'<number-of-claims>(\d+)</number-of-claims>', flags=re.DOTALL)

# Regex for extracting the citations by examiner
CITATIONS_EXAMINER_COUNT_PATTERN = re.compile(
    r'<category>cited by examiner<\/category>', flags=re.DOTALL)

# Regex for extracting the citations by applicant
CITATIONS_APPLICANT_COUNT_PATTERN = re.compile(
    r'<category>cited by applicant<\/category>', flags=re.DOTALL)

# Regex for extracting all information in the <inventors> tag
INVENTORS_TAG_PATTERN = re.compile(
    r'<inventors>.*?</inventors>', flags=re.DOTALL)

# Regex for extracting the inventors' names
INVENTORS_PATTERN = re.compile(
    r'<inventor[^>]*>\s*<addressbook>\s*<last-name>([^<]*)<\/last-name>\s*<first-name>([^<]*)<\/first-name>', flags=re.DOTALL)

# Regex for extracting all information in the <claims> tag
CLAIMS_TAG_PATTERN = re.compile(
    r'<claims id="claims">.*?<\/claims>', flags=re.DOTALL)

# Regex for extracting the claims text
CLAIMS_TEXT_PATTERN = re.compile(
    r'<claim-text>(.*?)<\/claim-text>', flags=re.DOTALL)

# Regex for extracting the abstracts
ABSTRACT_PATTERN = re.compile(
    r'<abstract[^>]*>\s*<p[^>]*>(.*?)<\/p>\s*<\/abstract>', flags=re.DOTALL)


# %% [markdown]
# ## <a id='toc5_2_'></a>[Preparing the Data](#toc0_)
# 
# We define a function `clean_xml_docs()` that takes our text file as input and returns a list of cleaned XML documents. We achieve this in the following steps:
# 
# -   The function opens the file at the specified path (`FILE_PATH`) which we defined at the start of the notebook.
# -   The function reads the file and splits the documents into a list, removing all newlines.
# -   Furthermore, we replace all HTML entities with their corresponding characters,
#     -   Note that since we cannot use the html library (as stated in the specification), we manually replace some of the most common HTML entities.
# -   Finally we remove any empty strings, if they exist, from the list and return the cleaned list of XML documents.
# 

# %%
def clean_xml_docs(file_path):
    """
    Reads and prepares the text file containing XML documents for parsing.
    :param file_path: path to assignment text file
    :return: list of cleaned XML documents in the text file
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        docs = file.read()

    # Split the text file into a list of XML documents and remove the declaration
    xml_docs = docs.split('<?xml version="1.0" encoding="UTF-8"?>')[1:]

    # Remove all newlines from the text file
    xml_docs = [doc.replace('\n', '') for doc in xml_docs]

    # Replace HTML entities with their corresponding characters
    html_entities = {'&amp;': '&', '&lt;': '<',
                     '&gt;': '>', '&quot;': '"',
                     '&#39;': "'", '&#x2018;': "‘",
                     '&#x2019;': "’", '&#xe7;': "ç",
                     '&#x2013;': "–", '&#x2014;': "—",
                     '&#x201c;': "“", '&#x201d;': "”"
                     }
    for entity, char in html_entities.items():
        xml_docs = [doc.replace(entity, char) for doc in xml_docs]

    # Remove empty strings from the list of XML documents
    xml_docs = list(filter(lambda x: len(x.strip()) > 0, xml_docs))

    return xml_docs


clean_docs = clean_xml_docs(FILE_PATH)


# %%
# Print the number of cleaned XML documents
print(len(clean_docs))


# %% [markdown]
# ## <a id='toc5_3_'></a>[Parsing the Data](#toc0_)
# 
# Here, we extract the information by iterating over the cleaned list of XML documents, using the regular expressions defined in the previous section. We achieve this in the following steps:
# 
# -   We initialise the empty lists for our attributes.
# -   Iterate over the cleaned list of XML documents using the compiled regular expressions to extract the information for each attribute.
#     -   When extracting the information for the `kind` attribute, we use a dictionary to map the values to their corresponding descriptions which were retrieved from the USPTO website. <sup>[5]</sup>
# -   Append the extracted information to the corresponding list.
# -   Note that if any of the attributes' values are not found in the XML document, 'NA' is used to represent the absence of the value (helpful for error handling and debugging). We achieve this by:
#     -   Using try-except blocks to catch the exceptions.
#     -   For `number_of_citations` (since it has type int), `citations_examiner_counts` and `citations_applicant_counts` we use '0' to represent the absence of the value.
# 

# %%
# Initialise empty lists to store the extracted data before creating the DataFrame
grant_ids = []
kinds = []
patent_titles = []
num_claims = []
cit_examiner_counts = []
cit_applicant_counts = []
inventors = []
claims_texts = []
abstracts = []


# Iterate over the list of XML documents and extract the data using compiled regex patterns
for doc in clean_docs:
    # Extract grant ID
    try:
        grant_id = GRANT_ID_PATTERN.search(doc).group(1)
    except AttributeError:
        grant_id = 'NA'
    grant_ids.append(grant_id)

    # Extract patent kind
    try:
        kind = KIND_PATTERN.search(doc).group(1)
        # Map the codes for kind to their descriptions
        kind_map = {
            'B2': 'Utility Patent Grant (with a published application) issued on or after January 2, 2001.',
            'B1': 'Utility Patent Grant (no published application) issued on or after January 2, 2001.',
            'S1': 'Design Patent',
            'E1': 'Reissue Patent',
            'P1': 'Plant Patent Application published on or after January 2, 2001',
            'P2': 'Plant Patent Grant (no published application) issued on or after January 2, 2001',
            'P3': 'Plant Patent Grant (with a published application) issued on or after January 2, 2001',
        }.get(kind, 'NA')
    except AttributeError:
        kind = 'NA'
        kind_map = 'NA'
    kinds.append(kind_map)

    # Extract patent title
    try:
        patent_title = PATENT_TITLE_PATTERN.search(doc).group(1)
    except AttributeError:
        patent_title = 'NA'
    patent_titles.append(patent_title)

    # Extract number of claims
    try:
        num_claim = int(NUMBER_OF_CLAIMS_PATTERN.search(doc).group(1))
    except AttributeError:
        num_claim = 0
    num_claims.append(num_claim)

    # Extract number of citations by examiner
    try:
        citations_examiner_count = len(
            CITATIONS_EXAMINER_COUNT_PATTERN.findall(doc))
    except TypeError:
        citations_examiner_count = 0
    cit_examiner_counts.append(citations_examiner_count)

    # Extract number of citations by applicant
    try:
        citations_applicant_count = len(
            CITATIONS_APPLICANT_COUNT_PATTERN.findall(doc))
    except TypeError:
        citations_applicant_count = 0
    cit_applicant_counts.append(citations_applicant_count)

    # Extract inventor names
    inventors_block = INVENTORS_TAG_PATTERN.search(doc)
    inventor_list = []
    try:
        inventor_blocks = INVENTORS_PATTERN.findall(inventors_block.group())
        for last, first in inventor_blocks:
            inventor_list.append(f"{first} {last}")
    except:
        inventor_list.append('NA')
    inventors.append(f"[{','.join(inventor_list)}]")

    # Extract claims and remove any HTML tags and entities
    claim_list = []
    try:
        claims_block = CLAIMS_TAG_PATTERN.search(doc)
        claim_blocks = CLAIMS_TEXT_PATTERN.findall(claims_block.group())
        for claim in claim_blocks:
            claim = re.sub(r'<[^>]*>|&\w+;', '', claim)
            claim_list.append(claim)
    except AttributeError:
        claims_texts.append('NA')
    claims_texts.append(f"[{','.join(claim_list)}]")

    # Extract abstracts and remove any HTML tags and entities
    abstract_block = ABSTRACT_PATTERN.search(doc)
    try:
        abstract = abstract_block.group(1)
        abstract = re.sub(r'<[^>]*>|&\w+;', '', abstract)

    except AttributeError:
        abstract = 'NA'
    abstracts.append(abstract)


# %% [markdown]
# ## <a id='toc5_4_'></a>[Creating a DataFrame](#toc0_)
# 
# We use the `pandas.DataFrame()` function to create a pandas DataFrame from the lists of extracted data.
# 
# Finally, we rearrange the columns of the DataFrame to match the order of the attributes in the sample output file.
# 

# %%
# Create a DataFrame from the extracted data
df = pd.DataFrame({
    'grant_id': grant_ids,
    'kind': kinds,
    'patent_title': patent_titles,
    'number_of_claims': num_claims,
    'citations_examiner_count': cit_examiner_counts,
    'citations_applicant_count': cit_applicant_counts,
    'inventors': inventors,
    'claims_text': claims_texts,
    'abstract': abstracts
})

# Rearrange the columns to match the order in the sample output file
df = df[['grant_id', 'patent_title', 'kind', 'number_of_claims', 'inventors',
         'citations_applicant_count', 'citations_examiner_count', 'claims_text', 'abstract']]


# %% [markdown]
# # <a id='toc6_'></a>[Outputting Files](#toc0_)
# 
# Now that we have parsed the text file and created a DataFrame object, we can output the data to CSV and JSON for downstream processing and analysis.
# 

# %% [markdown]
# ## <a id='toc6_1_'></a>[Writing to CSV](#toc0_)
# 
# For outputting the file to CSV we use the `to_csv()` method.
# 

# %%
# Output the DataFrame to a CSV file
df.to_csv('../data/output/patent_grants.csv', index=False)


# %% [markdown]
# ## <a id='toc6_2_'></a>[Writing to JSON](#toc0_)
# 
# For outputting the file to JSON, since we are not allowed to use the `json` library (as stated in the specification), we manually convert the DataFrame object to a JSON formatted string. <sup>[6]</sup>
# 
# -   We initially set the index of the DataFrame to `grant_id`.
# -   Convert the DataFrame to a dictionary using the `to_dict()` method, with the `orient` parameter set to `index`.
# -   This creates a nested dictionary with the `grant_id` as the key and the values as a dictionary of the attributes and their values.
# -   Using string manipulation we convert the dictionary to a JSON formatted string by iterating over the nested dictionary and concatenating the `key:value` pairs.
# -   Finally, we write the JSON formatted string to a file using the `write()` method.
# 

# %%
# Set grant_id as index
df.set_index('grant_id', inplace=True)

# Convert DataFrame to dictionary
data = df.to_dict(orient='index')

# Convert dictionary to JSON

# Initialise JSON string
json_data = '{'
for i, (key, record) in enumerate(data.items()):
    if i > 0:
        # Add a comma to separate records
        json_data += ',\n'
    json_data += f'"{key}": {{'
    for key2, value in record.items():
        if isinstance(value, str):
            # Escape double quotes
            value = re.sub('"', '\\"', value)
            # Add double quotes around the value
            value = f'"{value}"'
        # Add the key-value pair to the JSON string
        json_data += f'"{key2}": {value},'
    # Remove the last comma
    json_data = json_data[:-1] + '}'
# Closing JSON string
json_data += '}'

# Write JSON to file
with open('../data/output/patent_grants.json', 'w') as f:
    f.write(json_data)

# Reset index to default to allow re-running if required
df.reset_index(inplace=True)


# %% [markdown]
# ## <a id='toc6_3_'></a>[Verifying Outputs](#toc0_)
# 
# Optionally, we can verify the outputs by loading the CSV and JSON files back into pandas DataFrames.
# 
# -   This helps us to verify that the outputs can be loaded back into pandas DataFrames without any errors.
# -   This also helps us to verify that both CSV and JSON outputs have the same format and data.
# 

# %%
# Import the json library for only verifying outputs
import json

# Load CSV file into a DataFrame
df_csv = pd.read_csv('../data/output/patent_grants.csv', keep_default_na=False)

# Load JSON file into a dictionary
with open('../data/output/patent_grants.json', 'r') as f:
    json_data = json.load(f)

# Convert the dictionary to a DataFrame
df_json = pd.DataFrame.from_dict(json_data, orient='index')

# Set grant_id as index
df_json.index.name = 'grant_id'
df_json.reset_index(inplace=True)

# Check for similarities between the CSV and JSON files
if set(df_csv.columns) != set(df_json.columns):
    print('Error: CSV and JSON files DO NOT have the same columns')
else:
    if df_csv.equals(df_json):
        print('CSV and JSON files have the same data and format')
    else:
        print('Error: CSV and JSON files DO NOT have the same data and format')


# %% [markdown]
# # <a id='toc7_'></a>[Summary](#toc0_)
# 
# In this project, we successfully transformed a raw text file containing multiple XML documents of patent grants into a structured format suitable for data analysis and processing. The process involved several critical steps, each meticulously designed to extract and organise the required information while handling potential anomalies in the data.
# 
# ### Examining Patent Files
# 
# -   **Initial Analysis:** Reviewed the raw text file to understand its structure. Identified that the file contains multiple XML documents, each starting with an XML declaration.
# 
# -   **Counting Documents:** Created a function to count the number of XML documents in the file by splitting the text at each XML declaration. This helped in validating the completeness of the dataset and planning the parsing process.
# 
# ### Identifying Patterns and Formulating Regular Expressions
# 
# -   **Defining Data Fields:** Identified the key data fields to extract as per the specification.
# 
# -   **Regular Expression Formulation:** Developed specific regular expressions (regex) for each data field based on the XML tags and structure. Ensured that the regex patterns accounted for variations and possible anomalies in the data, such as optional attributes or missing elements.
# 
# #### Loading and Parsing Files
# 
# -   **Defining Regular Expressions:** Compiled all the regex patterns for efficiency. Patterns were carefully crafted to accurately capture the required information while handling different cases and potential missing data.
# 
# -   **Data Cleaning:**
#     -   Created a function to preprocess the raw XML text files by removing newline characters, replacing common HTML entities with their corresponding characters, and filtering out empty strings.
#     -   This step was crucial to ensure that the regex patterns could match the data correctly, as inconsistencies in formatting and encoding can hinder accurate data extraction.
# -   **Parsing Data:**
#     -   Applied the compiled regex patterns to extract the required data fields from each XML document.
#     -   Used try-except blocks to handle cases where certain data fields might be missing or malformed, assigning default values (`'NA'` or `0`) when necessary.
# 
# ### Creating a DataFrame
# 
# -   **Data Structuring:** Collected all extracted data into lists corresponding to each data field and created a pandas DataFrame to organise the data into a structured format. This facilitated easy manipulation, analysis, and export of the data.
# 
# -   **Column Arrangement:** Rearranged the DataFrame columns to match the desired order as per the specification, ensuring consistency and readability in the output files.
# 
# ### Outputting Files
# 
# -   **Writing to CSV:** Saved the DataFrame to a CSV file using the `to_csv()` method, ensuring the data was correctly formatted and saved for further analysis.
# 
# -   **Writing to JSON:** Manually converted the DataFrame to a JSON formatted string and saved it to a JSON file. The JSON output was structured to match the required format for downstream processing.
# 
# -   **Verifying Outputs:** Loaded the CSV and JSON files back into pandas DataFrames to confirm the integrity of the output files. Ensured that the data was correctly saved and could be easily reloaded for future analysis.
# 
# By meticulously examining the structure of the XML documents and carefully crafting regular expressions, the project efficiently transformed unstructured raw text data into a clean, structured format. This not only facilitates immediate analysis but also sets a foundation for more advanced data processing and machine learning tasks related to patent data.
# 

# %% [markdown]
# # <a id='toc8_'></a>[References](#toc0_)
# 
# [1] [Formatting Patent Numbers](https://web.cas.org/training/stneasytips/patentnumber2.html)
# 
# [2] [USPTO - Patent Numbers](https://www.uspto.gov/patents/apply/applying-online/patent-number)
# 
# [3] ["Kind Codes" Included on USPTO Patent Documents](https://manuals.ipaustralia.gov.au/patent/annex-z---uspto-kind-codes)
# 
# [4] [PEP 8 – Style Guide for Python Code - Constants](https://peps.python.org/pep-0008/#constants)
# 
# [5] [U.S. Patent Grant Data XML](https://www.uspto.gov/sites/default/files/products/PatentGrantXMLv42-Documentation-508.pdf)
# 
# [6] [Stackoverflow, Generating JSON without json library](https://stackoverflow.com/questions/19712133/creating-json-in-python-without-using-json-import)
# 


