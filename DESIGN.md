### Back-end (SQL database):

Our main tool for the implementation of our dashboard is our dynamic SQL database. To find the data for the SQL database, we located the COVID-19 data for 8 schools (Babson, Bentley, Berklee, BU, Emerson, Harvard, MIT, and Northeastern) in Massachusetts. We scraped their COVID-19 data regarding daily positive cases, cumulative past seven day cases, and semester cumulative data. Moreover, we scraped the positivity rate data from the public records for the cities of each university and their shared state of Massachusetts. Finally, we created several SQL tables to store the information. 

Throughout the development of our application, our SQL database underwent several iterations as our UX needs changed. Our final SQL database, covid_stats5.db, contains five tables: county_covid_stats, student, university_covid_stats, town_covid_stats, and university_data. The first table, county_covid_stats, contains the test count, positive count, and death count for several counties across the period of five days. The second table, student, contains account data, including the username, the hash password, and university of each user. The third table, university_covid_stats, contains the test count, positive count, county, and town of each university over the seven-day period from 11/28/21 to 12/4/21. The fourth table, town_covid_stats, contains the positivity rate of each town that these universities are located in. Finally, our fifth table, university_data, contains the total positive count and test count over the past 7 days, the cumulative positive and test count over the past semester (or further back), the vaccination rate of the university, and the city the university resides in.

All of the data is retrieved from the back-end using SQL queries and displayed through the visual formatting described below in the front-end design section. 

### Front-end (Python-Flask, Javascript, HTML/CSS):

Our project displays several HTML pages, including Dashboard, Login, Register, and the individual university pages.

# Dashboard:
The dashboard consists of two features, the map slider and tables. The map slider utilizes javascript to create the slider and to overlay the images, as well as HTML to display the maps on the dashboard page. The university table retrieves data in the university_data table from the SQL database, using a for loop in jinja to display and rank the colleges by the positivity rate of the past seven days. Similarly, the table displaying the college towns retrieves data in the covid_town_stats table from the SQL database and uses a jinja for loop to display the data in a table.

# Register: 
The register page contains three short-answer forms, a drop down selection form, and a submission button. For the username form, the coding behind the form uses a SQL query to check that the username has not already been taken, and that the user actually imputed a username. The password form checks to see that the user imputed a password, and the coding also checks that the imputed password and confirmation password match. Finally, the drop down menu checks that the user has selected a college for registration. The submitted username, password, and selected college are stored in the SQL table named student with columns login_id, hash_password, and university_name.

# Login: 
The login page contains two short-answer forms, a drop down selection form, and a submission button. For the username form, the coding behind the form uses a SQL query to check that the username exists, and that the user actually imputed a username. The password form uses the function “check_password_hash” to check that the hashed password for the imported password matches with the hashed password stored in the SQL table student. The drop down menu checks that the user’s selected college mathes with the one they registered with. Only after these requirements have been met can a user visit the dashboard.

# Logout: 
The logout page simply uses the function session.clear to log the user out and bring the user back to the login page. 

# Input: 
In the input page, users select whether they have tested positive or negative using a drop-down option selector. If the selected option is positive, python coding increases the column values in past_7_positive, past_7_total, cummulative_positive, and cummulative_total for the college that the user is logged into by 1. If the selected option is negative, only the past_7_total and cummulative_total values for the respective college increase by 1.

# College Pages:
The individual college pages each display consistent information across all of the colleges: daily cases from 11/28/21 to 12/4/21, the testing statistics over the past seven days and the cumulative data from the start of the semester (or from further back), the positivity rates in Massachusetts and the college town, and the vaccination rate of students in the college. This data was retrieved from the university_data table, the university_covid_stats table, and town_covid_stats table. Once again, I used a jinja for loop to display the data in multiple tables.
