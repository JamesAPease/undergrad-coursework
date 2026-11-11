# James Pease — Data Analytics Portfolio

Senior Data Analyst | Analytics Engineer · Orange County, CA
[LinkedIn](https://www.linkedin.com/in/james-a-pease/) · james.a.pease@gmail.com

I build and own the analytics systems executives use to run the business. As the sole data analyst for a 200+ location restaurant franchisee, I manage the full stack: SQL Server, automated Azure pipelines, Python predictive models, and 20+ Power BI dashboards across finance, operations, HR, risk, and marketing.

This repository showcases selected projects. Work built on company data has been rewritten to run on **synthetic data**, so the methods are shown without exposing any confidential information.

## Featured Projects

### Store Cost Prediction Models
`/Financial_Cost_Prediction`

Predicts expected monthly food and labor costs for each store from revenue and company, then flags stores whose actual costs break from the prediction.

- **Pipeline:** loads multi-year ledger data, unpivots and joins it to a chart of accounts and store master table, and aggregates it to store-month level
- **Models:** Linear Regression, Ridge (alpha tuned with GridSearchCV), and Random Forest, compared on RMSE and R²
- **Results on production data:** R² of 0.94 for food cost and 0.87 for labor cost; the Random Forest version runs each month-end and loads predictions to SQL Server for Power BI reporting
- **Stack:** Python, pandas, scikit-learn (the production version also uses SQLAlchemy to read from Azure SQL)
- **Run it:** `pip install -r requirements.txt`, then `python cost_prediction.py`

## Skills

- **BI and visualization:** Power BI (DAX, Power Query), Tableau, Excel
- **Data engineering:** SQL Server, Azure Data Factory, Power Automate, ETL design, data modeling, data quality
- **Programming and analytics:** SQL, Python, R, predictive modeling, machine learning, exploratory data analysis
- **Tools:** Git, GitHub, AI-assisted development

## Education

- M.S., Business Analytics, California State University, Sacramento (2025)
- B.S., Management Information Systems, California State University, San Marcos (2020)

## Archive

`/Archive` holds early coursework from my undergraduate program (Java exercises and database design assignments).
