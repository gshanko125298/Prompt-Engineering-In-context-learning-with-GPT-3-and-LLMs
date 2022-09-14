Prompt-Engineering-In-context-learning-with-GPT-3-and-LLMs
1.	Introduction
     - This project focus on the overall overview of Large Language Models (LLMs) related concepts with case study. The case study focus on two types of dataset provided. As an outcome entity extraction with scoring will be expected. In this report the dataset and some features was listed. Furthermore, model selection with some justification was pointed. Finally the report provide some insight on some of the basic LLMS related concepts. In the current report some of the objective only included, we will include the other on the final with our model result.
2.	Objective of the study 
         The analysis objective of this project are divided into 4 sub-objectives that overall guides the workflow
       - Setting up environment to use LLMs APIs 
       - Comparing word-embedding based clustering with prompt based classification 
       - Setting up repeatable ML framework for prompt engineering - Reporting and Dashboard

3.	Data and features 
     There are two dataset was provided as listed below:
     Data 1:This data comes from the client described above.  
      - Domain - the base URL or a reference to the source these item comes from 
      - Title - title of the item - the content of the item
      -  Description - the content of the item
      -  Body - the content of the item
      -  Link - URL to the item source (it may not functional anymore sometime)
      -  Timestamp - timestamp that this item was collected at
      -  Analyst_Average_Score - target variable - the score to be estimated
      -  Analyst_Rank - score as rank
      -  Reference_Final_Score - Not relevant for now - it is a transformed quantity
Data-2: The data are job descriptions (together named entities) and relationships between entities in json format. 
      - Dataset 1: For development and training
      - Dataset 2: For testing and final reporting
4.	Model selection 
There are a list of LLMs that was serve as a free to create or perform analysis to extract an entity and scoring. Form the list we selected the best fit based on the requirement and our expected outcome. The following are some list of model:
      - AlenNLP: Language modeling is the task of determining the probability of a given sequence of words occurring in a sentence
      - The text generation API:  is backed by a large-scale unsupervised language model that can generate paragraphs of text. 
      - BLOOM: is used for a type of semantic search. The black text is user input, by which the LLM task is casted as search.
      - Cohere: is one of the model works on entity extraction with scoring
      
Finally we decide to us cohere as our LLMS model for this project, hence our project is focus on entity extraction not sentiment analysis. 

This are some steps which had been taken from .....
Entity Extraction
     - Extracting a piece of information from text is a common need in language processing systems. LLMs can at times extract entities which are harder to extract using other NLP methods (and where pre-training provides the model with some context on these entities). This is an overview of using generative LLMs to extract entities.
     Setup
Let's start by installing the packages we need.
1. !pip install cohere requests tqdm
2. Preparing examples for the prompt: n our prompt, we'll present the model with examples for the type of output that performs entity extraction with scoring  
3. Creating the extraction prompt
4. Getting the data
5. Running the model

For the detail of the code part please refer our (Notebook)
