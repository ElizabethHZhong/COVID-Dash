from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
import sqlite3
from cs50 import SQL

from helpers import apology, login_required
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


def percentage(i):
    i *= 100
    return f"{i:,.2f}%"

app.jinja_env.filters["percentage"] = percentage

cur = SQL("sqlite:///covid_stats5.db")

# List of colleges
COLLEGES = [
   "Babson",
   "Bentley",
   "Berklee",
   "BU",
   "Emerson",
   "Harvard",
   "MIT",
   "Northeastern"
]

RESULT = [
    "positive",
    "negative"
]


def upsertStats(dbconn, schoolname, date, testnum, positivenum):
    dbconn.cursor().execute("INSERT OR REPLACE INTO university_covid_stats values (?, ?, ?, ?)", (schoolname, date, testnum, positivenum))
    dbconn.commit()


def main():
    con = sqlite3.connect('covid_stats2.db')
    cur = con.cursor()

    #upsertStats(con, "a", "2021/11/28", 200, 22)

    for row in cur.execute('SELECT * FROM university_covid_stats ORDER BY university_name, date'):
            print(row)
    for row in cur.execute('SELECT * FROM county_covid_stats ORDER BY county_name, date'):
            print(row)

    con.close()


# Dashboard
@app.route("/")
@login_required
def dashboard():
    """Dashboard"""
    
    ordered_schools = []
    schools = cur.execute("SELECT university_name, past_7_positive, past_7_total, city FROM university_data")

    for school in schools:
        dict = {}
        dict["university_name"] = school["university_name"]
        dict["city"] = school["city"]
        dict["positivity_rate"] = school["past_7_positive"] * 1.0 / school["past_7_total"]
        ordered_schools.append(dict)

    def f(a):
        return a["positivity_rate"]
    
    ordered_schools.sort(key=f)

    cities = cur.execute("SELECT * FROM town_covid_stats")

    def g(a):
        return a["positivity_rate"]
    
    cities.sort(key=g)

    return render_template("dashboard.html", ordered_schools=ordered_schools, cities=cities)


@app.route("/register", methods=["GET", "POST"])
def register():
  # Forget the user id
  session.clear()
  # Check when request is post
  if request.method == "POST":
      # Check to see that username field is filled
      if not request.form.get("username"):
          return apology("Must provide username!", 400)
      rows = cur.execute("SELECT * FROM student WHERE login_id = ?", request.form.get("username"))
   # Check
      if len(rows) != 0:
          return apology("Username already taken.", 400)
        
      # for password check if one was submitted
      elif not request.form.get("password"):
          return apology("Must provide password!", 400)
      # check to see if confirmation was completed
      elif not request.form.get("confirmation"):
          return apology("Must provide confirmation!", 400)
    
      # make sure confirmation and password are the same
      elif request.form.get("password") != request.form.get("confirmation"):
          return apology("Passwords do not match!", 400)
 
      elif request.form.get("college") not in COLLEGES:
          return apology("Please choose college!", 400)
    
      cur.execute("INSERT INTO student (login_id, hashed_password, university_name) VALUES (?,?,?)", request.form.get(
          "username"), generate_password_hash(request.form.get("password")), request.form.get("college"))
      return redirect("/login")
  else:
      return render_template("register.html", colleges = COLLEGES)
 
 
@app.route("/login", methods=["GET", "POST"])
def login():
  """Log user in"""
  # Forget any user_id
  session.clear()
  # User reached route via POST (as by submitting a form via POST)
  if request.method == "POST":
      # Ensure username was submitted
      if not request.form.get("username"):
          return apology("Must provide username!", 400)
      # Ensure password was submitted
      elif not request.form.get("password"):
          return apology("Must provide password!", 400)
      # Query database for username
      rows = cur.execute("SELECT * FROM student WHERE login_id = ?", request.form.get("username"))
      # Ensure username exists and password is correct
      if len(rows) != 1 or not check_password_hash(rows[0]["hashed_password"], request.form.get("password")):
          return apology("Invalid username and/or password!", 400)
 
      elif cur.execute("SELECT university_name FROM student WHERE login_id = ?", request.form.get("username"))[0]["university_name"] != request.form.get("college"):
          return apology("Incorrect school!")
  
      # Remember which user has logged in
      session["login_id"] = rows[0]["login_id"]
      # Redirect user to home page
      return redirect("/")
  # User reached route via GET (as by clicking a link or via redirect)
  else:
      return render_template("login.html", colleges = COLLEGES)
 

@app.route("/logout")
def logout():
   """Log user out"""
 
   # Forget any user_id
   session.clear()
 
   # Redirect user to login form
   return redirect("/")

@app.route("/input", methods=["GET", "POST"])
def input():
  if request.method == "POST":
      # TODO: Add the user's entry into the database
      #access form data
      #insert data into database
      if request.form.get("positivenegative") not in RESULT:
          return apology("Please choose a result!", 400)
      name = cur.execute("SELECT university_name FROM student WHERE login_id = ?", session["login_id"])[0]["university_name"]
      if request.form.get("positivenegative") == "positive":
          new_total = cur.execute("SELECT past_7_total FROM university_data WHERE university_data.university_name = ?", name)[0]["past_7_total"] + 1
          new_positive = cur.execute("SELECT past_7_positive FROM university_data WHERE university_data.university_name = ?", name)[0]["past_7_positive"] + 1
          new_ctotal = cur.execute("SELECT cummulative_total FROM university_data WHERE university_data.university_name = ?", name)[0]["cummulative_total"] + 1
          new_cpositive = cur.execute("SELECT cummulative_positive FROM university_data WHERE university_data.university_name = ?", name)[0]["cummulative_positive"] + 1
          cur.execute("UPDATE university_data SET past_7_total = ?, past_7_positive = ?, cummulative_total = ?, cummulative_positive = ? WHERE university_data.university_name = ?", new_total, new_positive, new_ctotal, new_cpositive, name)
      else:
          new_total = cur.execute("SELECT past_7_total FROM university_data WHERE university_data.university_name = ?", name)[0]["past_7_total"] + 1
          new_ctotal = cur.execute("SELECT cummulative_total FROM university_data WHERE university_data.university_name = ?", name)[0]["cummulative_total"] + 1
          cur.execute("UPDATE university_data SET past_7_total = ?, cummulative_total = ? WHERE university_data.university_name = ?", new_total, new_ctotal, name)
      return redirect("/")
  else:
      return render_template("input.html")


# Sources
@app.route("/sources.html")
def sources():
    return render_template("sources.html")


@app.route("/babson") # change here
@login_required
def babson(): # change here
    cases = cur.execute("SELECT * FROM university_covid_stats WHERE university_name = ?", "Babson") # change here

    def h(a):
        return a["date"]

    cases.sort(key=h)

    for row in cases:
        if row["test_count"] != 0:
            row["positivity_rate"] = row["positive_count"] * 1.0 / row["test_count"]
        else:
            row["positivity_rate"] = 0;

    data = cur.execute("SELECT * FROM university_data WHERE university_name = ?", "Babson")[0] # change here
    city = cur.execute("SELECT * FROM town_covid_stats WHERE town_name = ?", data["city"])[0]
    
    data["city_positivity_rate"] = city["positivity_rate"]
    data["past_positivity_rate"] = data["past_7_positive"] * 1.0 / data["past_7_total"]
    data["cummulative_positivity_rate"] = data["cummulative_positive"] * 1.0 / data["cummulative_total"]

    return render_template("babson.html", cases=cases, data=data) # change here


@app.route("/bentley") # change here
@login_required
def bentley(): # change here
    cases = cur.execute("SELECT * FROM university_covid_stats WHERE university_name = ?", "Bentley") # change here

    def h(a):
        return a["date"]

    cases.sort(key=h)

    for row in cases:
        if row["test_count"] != 0:
            row["positivity_rate"] = row["positive_count"] * 1.0 / row["test_count"]
        else:
            row["positivity_rate"] = 0;

    data = cur.execute("SELECT * FROM university_data WHERE university_name = ?", "Bentley")[0] # change here
    city = cur.execute("SELECT * FROM town_covid_stats WHERE town_name = ?", data["city"])[0]
    
    data["city_positivity_rate"] = city["positivity_rate"]
    data["past_positivity_rate"] = data["past_7_positive"] * 1.0 / data["past_7_total"]
    data["cummulative_positivity_rate"] = data["cummulative_positive"] * 1.0 / data["cummulative_total"]

    return render_template("bentley.html", cases=cases, data=data) # change here


@app.route("/berklee") # change here
@login_required
def berklee(): # change here
    cases = cur.execute("SELECT * FROM university_covid_stats WHERE university_name = ?", "Berklee") # change here

    def h(a):
        return a["date"]

    cases.sort(key=h)

    for row in cases:
        if row["test_count"] != 0:
            row["positivity_rate"] = row["positive_count"] * 1.0 / row["test_count"]
        else:
            row["positivity_rate"] = 0;

    data = cur.execute("SELECT * FROM university_data WHERE university_name = ?", "Berklee")[0] # change here
    city = cur.execute("SELECT * FROM town_covid_stats WHERE town_name = ?", data["city"])[0]
    
    data["city_positivity_rate"] = city["positivity_rate"]
    data["past_positivity_rate"] = data["past_7_positive"] * 1.0 / data["past_7_total"]
    data["cummulative_positivity_rate"] = data["cummulative_positive"] * 1.0 / data["cummulative_total"]

    return render_template("berklee.html", cases=cases, data=data) # change here


@app.route("/bu") # change here
@login_required
def bu(): # change here
    cases = cur.execute("SELECT * FROM university_covid_stats WHERE university_name = ?", "BU") # change here

    def h(a):
        return a["date"]

    cases.sort(key=h)

    for row in cases:
        if row["test_count"] != 0:
            row["positivity_rate"] = row["positive_count"] * 1.0 / row["test_count"]
        else:
            row["positivity_rate"] = 0;

    data = cur.execute("SELECT * FROM university_data WHERE university_name = ?", "BU")[0] # change here
    city = cur.execute("SELECT * FROM town_covid_stats WHERE town_name = ?", data["city"])[0]
    
    data["city_positivity_rate"] = city["positivity_rate"]
    data["past_positivity_rate"] = data["past_7_positive"] * 1.0 / data["past_7_total"]
    data["cummulative_positivity_rate"] = data["cummulative_positive"] * 1.0 / data["cummulative_total"]

    return render_template("bu.html", cases=cases, data=data) # change here


@app.route("/emerson") # change here
@login_required
def emerson(): # change here
    cases = cur.execute("SELECT * FROM university_covid_stats WHERE university_name = ?", "Emerson") # change here

    def h(a):
        return a["date"]

    cases.sort(key=h)

    for row in cases:
        if row["test_count"] != 0:
            row["positivity_rate"] = row["positive_count"] * 1.0 / row["test_count"]
        else:
            row["positivity_rate"] = 0;

    data = cur.execute("SELECT * FROM university_data WHERE university_name = ?", "Emerson")[0] # change here
    city = cur.execute("SELECT * FROM town_covid_stats WHERE town_name = ?", data["city"])[0]
    
    data["city_positivity_rate"] = city["positivity_rate"]
    data["past_positivity_rate"] = data["past_7_positive"] * 1.0 / data["past_7_total"]
    data["cummulative_positivity_rate"] = data["cummulative_positive"] * 1.0 / data["cummulative_total"]

    return render_template("emerson.html", cases=cases, data=data) # change here


@app.route("/harvard")
@login_required
def harvard():
    cases = cur.execute("SELECT * FROM university_covid_stats WHERE university_name = ?", "Harvard") # change here

    def h(a):
        return a["date"]

    cases.sort(key=h)

    for row in cases:
        if row["test_count"] != 0:
            row["positivity_rate"] = row["positive_count"] * 1.0 / row["test_count"]
        else:
            row["positivity_rate"] = 0;

    data = cur.execute("SELECT * FROM university_data WHERE university_name = ?", "Harvard")[0] # change here
    city = cur.execute("SELECT * FROM town_covid_stats WHERE town_name = ?", data["city"])[0]
    
    data["city_positivity_rate"] = city["positivity_rate"]
    data["past_positivity_rate"] = data["past_7_positive"] * 1.0 / data["past_7_total"]
    data["cummulative_positivity_rate"] = data["cummulative_positive"] * 1.0 / data["cummulative_total"]

    return render_template("harvard.html", cases=cases, data=data) # change here


@app.route("/mit") # change here
@login_required
def mit(): # change here
    cases = cur.execute("SELECT * FROM university_covid_stats WHERE university_name = ?", "MIT") # change here

    def h(a):
        return a["date"]

    cases.sort(key=h)

    for row in cases:
        if row["test_count"] != 0:
            row["positivity_rate"] = row["positive_count"] * 1.0 / row["test_count"]
        else:
            row["positivity_rate"] = 0;

    data = cur.execute("SELECT * FROM university_data WHERE university_name = ?", "MIT")[0] # change here
    city = cur.execute("SELECT * FROM town_covid_stats WHERE town_name = ?", data["city"])[0]
    
    data["city_positivity_rate"] = city["positivity_rate"]
    data["past_positivity_rate"] = data["past_7_positive"] * 1.0 / data["past_7_total"]
    data["cummulative_positivity_rate"] = data["cummulative_positive"] * 1.0 / data["cummulative_total"]

    return render_template("mit.html", cases=cases, data=data) # change here


@app.route("/northeastern") # change here
@login_required
def northeastern(): # change here
    cases = cur.execute("SELECT * FROM university_covid_stats WHERE university_name = ?", "Northeastern") # change here

    def h(a):
        return a["date"]

    cases.sort(key=h)

    for row in cases:
        if row["test_count"] != 0:
            row["positivity_rate"] = row["positive_count"] * 1.0 / row["test_count"]
        else:
            row["positivity_rate"] = 0;

    data = cur.execute("SELECT * FROM university_data WHERE university_name = ?", "Northeastern")[0] # change here
    city = cur.execute("SELECT * FROM town_covid_stats WHERE town_name = ?", data["city"])[0]
    
    data["city_positivity_rate"] = city["positivity_rate"]
    data["past_positivity_rate"] = data["past_7_positive"] * 1.0 / data["past_7_total"]
    data["cummulative_positivity_rate"] = data["cummulative_positive"] * 1.0 / data["cummulative_total"]

    return render_template("northeastern.html", cases=cases, data=data) # change here


main()