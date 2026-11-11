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

### SBA Loan Default Prediction (MSBA Capstone Competition)
`/MSBA_SBA_Loan_Default`

Team project for the 2024 CSU Systemwide Business Analytics Competition: predicting which of 899,164 SBA-guaranteed loans would default, and choosing the model and approval cutoff that maximize a bank's net profit.

- **Models:** classification trees, bagging, boosting, random forest, KNN, logistic regression (Ridge, Lasso, Elastic Net), discriminant analysis, and neural networks
- **Decision rule:** profit-based cutoffs with class weights reflecting the higher cost of approving a loan that defaults
- **Includes a Lessons Learned review** of the methodology, written after graduation
- **Stack:** Python (pandas, scikit-learn), R

### Dokkan Battle Damage Calculator
`/Dokkan_Calculator`

A survival calculator for *Dragon Ball Z Dokkan Battle* that models whether a unit survives an enemy super attack, built because in-game stat screens don't show the math.

- **Models:** enemy attack stacking per action, super-attack DEF boosts, guard, damage reduction, critical hits, and enemy HP and DEF debuffs
- **Solves backward:** finds the minimum start-of-turn DEF a unit needs to survive a given hit
- **Scenario analysis:** compares normal hits, crits, and debuffed turns, and finds the exact turn a stacking boss breaks through a unit's defense
- **Stack:** Python (dataclasses), no dependencies
- **Run it:** `python dokkan_calculator.py`

### Pokémon Shiny Hunting Analytics
`/Pokemon_Shiny_Analytics`

Data tools behind my personal shiny living-dex tracker (1,100+ of 1,362 forms collected).

- **Odds analysis (`shiny_odds.py`):** models shiny hunts as a geometric distribution to show the encounters needed for a 50%, 75%, 90%, or 99% chance across hunting methods. Key finding: the median full-odds hunt takes about 2,839 encounters, roughly 31% fewer than the 4,096 average, which is why most hunts end "early" while a few run very long.
- **Pokédex scraper (`scrape_pokedex.py`):** scrapes national and regional Pokédex lists into CSV as the master list for the tracker, with polite request delays and validation that fails loudly if the page layout changes
- **Stack:** Python, NumPy, pandas, matplotlib, requests, BeautifulSoup

![Shiny odds chart](Pokemon_Shiny_Analytics/shiny_odds.png)

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
