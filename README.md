# MassMutual Data Viz Recruitment

This project is intended to evaluate MassMutual data visualization engineering candidates. The project contains a simple web app to be use as a starting point to build data visualizations.

## Instructions

Your goal, as a data visualization engineering candidate, is to build interesting data visualizations for a target audience of an insurance agent or marketing manager. These visualizations should enable these users to locate and understand potential new markets or customers for the purpose of selling life insurance.

The visualizations you construct should reveal insights about the data and follow visualization best practices. Best practices include presenting multivariate data, enabling comparisons, and providing descriptive titles and labels.

NOTE: Don’t attempt to build something too complicated. Don’t feel that you need to spend a lot time constructing an interactive dashboard system with interdependent visualizations. Just work towards creating visuals that tell the story within the data, addresses the business problem, and demonstrates your ability to work with the technologies. We would rather receive a complete project, and then talk about how the work could be extended during the onsite interview, rather than have you run out of time attempting something ambitious.

Please feel free to contact the recruiter if you have any questions.


## Getting Started

Make sure python is installed on your system:
`python --version`

If not, you can download python here:
(https://www.python.org/downloads/)

Install the python tool **virtualenv** in order to be able to set up a python virtual environment.
`pip install virtualenv`

## Data
This project contains an SQLite database, **recruit.db**. This database is pre-populated with data and should be utilized in each project to produce data visualizations.

### Data Dictionary
#### customer table
* id - primary key
* race_code - foreign key to race table
* education_id - foreign key to educaton table
* home_owner - Home Owner / Renter, O = Home Owner, R = Renter
* state - state location in the United States
* is_smoker - whether customer is a smoker, 1 = Yes
* is_exerciser - whether customer excercises, 1 = Yes
* has_insurance - Life Insurance Policy Owner, 1 = True
* income - Income By The Thousands
* travel_spending - Amount spent by customer on Travel
* sports_leisure_spending - Amount spent by customer on Sports & Leisure
* economic_stability - 01 = Most Likely Economically Stable, 30 = Least Likely Economically Stable
* insurance_segment_id - foreign key to insurance_segment table
* youtube_user_rank - Propensity to use YouTube, 01 (Most Likely) through 20 (Least Likely)
* facebook_user_rank - Propensity to use Facebook, 01 (Most Likely) through 20 (Least Likely)
* gender - M = Male, F = Female


## Project recruit-viz/web

Use a python Flask rest api and the D3.js JavaScript library to visualize data.
Start here: start.py

### Setup
Create a python virtual environment for the **web** project:
`virtualenv venv`

Then set up the new virtual environment with the required dependancies:
`./venv/bin/pip install -r requirements.txt`

Start the web application:
`./venv/bin/python start.py`

### Instructions
Use the start.py file and templates/index.html as a starting place for building web based data visualizatons driven by the data found in **recruit.db

The index.html template is mapped to the application's root at /. Please, extend the code by adding your own API endpoints and html templates.


