![US-patent-data-parsing](images/IP-patent-data-parsing.svg)

# Project Description

The primary objective of this project is to parse and preprocess a raw text file containing multiple XML documents of intellectual property (IP) patent grants. By leveraging regular expressions and data manipulation techniques, we aim to extract relevant data from unstructured XML data and transform it into a structured format suitable for data analysis, trend identification and machine learning applications related to patent data.

The project involves several key steps:

-   **Examining Patent Files:** Understanding the structure of the raw text file and identifying that it contains multiple XML documents, each representing a patent grant.

-   **Identifying Patterns and Formulating Regular Expressions:** Developing specific regular expressions to accurately extract required data fields such as grant IDs, patent kinds, titles, number of claims, citation counts, inventors, claims text and abstracts.

-   **Loading and Parsing Files:** Reading the text file, cleaning the data by removing newlines and replacing HTML entities, and splitting it into individual XML documents for processing.

-   **Data Extraction:** Applying the compiled regular expressions to extract the desired information from each XML document, handling potential anomalies and missing data.

-   **Creating a DataFrame:** Organising the extracted data into a pandas DataFrame, providing a structured and organised format for data manipulation and analysis.

-   **Outputting Files:** Saving the structured data into CSV and JSON formats, ensuring compatibility for downstream applications and further processing.

Overall, this project demonstrates a practical and comprehensive approach to handling unstructured XML data. By parsing the XML data and extracting relevant attributes, the project facilitates the transformation of unstructured text data into a structured and organised format. This structured data is essential for downstream analysis, enabling insights to be gained from complex patent-related information. It lays a solid foundation for future analytical endeavours in patent data analysis and intellectual property research.

# Project Tree

```
📦 US-patent-data-parsing
├─ LICENSE
├─ README.md
├─ data
│  ├─ input
│  │  └─ patent_grants_data.txt
│  ├─ output
│  │  ├─ patent_grants.csv
│  │  └─ patent_grants.json
│  └─ sample
│     ├─ sample_input.txt
│     ├─ sample_output.csv
│     └─ sample_output.json
├─ images
│  └─ US-patent-data-parsing.png
└─ notebooks
   └─ 01-data-parsing.ipynb
```

# Technologies Used

-   [Python](https://www.python.org/downloads/)
-   [Pandas](https://pandas.pydata.org/)
-   [RegEx](https://docs.python.org/3/library/re.html)
-   [Jupyter ](https://jupyter.org/)

# Outputs

The project generates several key output files (located in the `data/output` directory):

-   **`patent_grants.csv`:** Contains the structured data extracted from the patent XML documents. Each row represents a patent grant with fields such as grant ID, patent title, kind, number of claims, inventors, citation counts, claims text and abstract.

-   **`patent_grants.json`:** A JSON file with the same structured data as the CSV, formatted for compatibility with applications that consume JSON data.

# Future Improvements

-   **Automated Testing:** Implement automated tests for the regular expressions and data extraction process to ensure stability and robustness of the project.
-   **Comparative Analysis:** Conduct comparative analyses of different patent datasets to identify trends, patterns or anomalies, contributing to a deeper understanding of IP patent grants.
-   **Scalability:** Optimise the code to handle larger datasets efficiently, possibly through parallel processing or memory management techniques.

# License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/salmanjt/US-patent-data-parsing/blob/main/LICENSE) file for details.

# Credits

[Author - Salman Tahir](https://linkedin.com/in/salmanjt)  
[Project Tree Generator](https://woochanleee.github.io/project-tree-generator)
