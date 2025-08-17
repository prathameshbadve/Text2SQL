# TEXT-2-SQL

## Motivation & Inspiration

In all large companies, the business owners don't interact with the data on a day-to-day basis. They are restricted to using dashboards that show predefined KPIs or need to ask an analyst to run queries to get the data relevant for their business question. The latter might take anywhere between a few hours to few days.

What if there was an AI agent that can understand the business questions in natural language, run the required SQL queries and give the results directly in the chat (Slack/Teams/etc.)? This will reduce the time required to get the insights on business KPIs that are not predefined, but will directly affect the decisions to be made.

I came across the Text-2-SQL project done at Swiggy called [Hermes](https://bytes.swiggy.com/hermes-a-text-to-sql-solution-at-swiggy-81573fb4fb6e) and thought it is a good way to brush my NLP skills and learn how to deploy an AI application involving context engineering, RAG and finetuning LLMs.

## Objective

The objective is to develop an AI agentic application that generates SQL based on natural language prompts, runs the SQL and returns a response with the required KPI/stat/insight. The model should generate a valid SQL, run it and return a response in an insightful manner.

## Methodology

#### Version 0.1.0

For this version, I am using the open source LLM by Meta - Llama3.2:3b as the main LLM, [Weaviate](https://weaviate.io) as the Vector DB, PostgreSQL for hosting the open source dataset [Pagila](https://github.com/devrimgunduz/pagila) and streamlit for the app UI. Also, I am restricting the scope to simply return SQL. The generated SQL will have to be run manually by copying and pasting in a separate chatbox on the same page.

![V0.1.0 LLD](images/v010_LLD.png "LLD")

## Try it!

1. Clone this repo.
2. Setup python environment using python 3.11

```
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install --upgrade pip
python3.11 -m pip install -r requirements.txt
```

3. Follow the instructions on the [Pagila](https://github.com/devrimgunduz/pagila) documentation and create the Postgres DB. Add the DB connection parameters to a .env file.
4. Use the docker-compose file to create the Weaviate instance.

```
docker-compose up -d
```

The app connects to a locally hosted Weaviate instance, so no connection parameters are required for this DB.

5. Run the streamlit app from the parent directory.

```
python3.11 -m streamlit run app/run_app.py
```

I have created a separate admin page to extract the DB schema and upload schema embeddings to the vector DB. So make sure to run the two procedures by clicking the buttons on the 'Admin' page.

6. Finally, you can interact with the model via the chat interface on the left. It will return the generated SQL, which can be copied and queried in the chat interface on the right.

## Note:

- This is my first attempt at creating an AI application.
- The model still does not return valid SQL all the time. Even if the SQL syntax is correct, it does not necessarily use the correct column names.
- In the next version, I want to add a few NL-SQL examples so that the model is able to refer to them for complex logic.
- More context about the entity relations should be added to the model.
- The capability has to be extended, so that the SQL is run automatically and insights are shown directly in the chat instead of SQL.
