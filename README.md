# TEXT 2 SQL

## Motivation & Inspiration

In all large companies, the business owners don't interact with the data on a day-to-day basis. They are restricted to using dashboards that show predefined KPIs or need to ask an analyst to run queries to get the data relevant for their business question. The later might take anywhere between a few hours to few days.

What if there was an AI agent that can understand the business questions in natural language, run the required SQL queries and give the results directly in the chat (Slack/Teams/etc.)? This will reduce the time required to get the insights on business KPIs that are not predefined, but will directly affect the decision to be made.

I came across such a project done at Swiggy called [Hermes](https://bytes.swiggy.com/hermes-a-text-to-sql-solution-at-swiggy-81573fb4fb6e).

## Objective

The goal of this project was to build an app that leveraged open source language models to interpret the natural language prompts and return valid SQL code. The SQL should be able to run directly to get the answers for the user's questions.
