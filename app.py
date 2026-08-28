import sqlite3

from flask import Flask, redirect, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import os, requests

app = Flask(__name__)

load_dotenv()
api_key = os.environ.get("USDA_API_KEY")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#response = requests.get(
 #   "https://api.nal.usda.gov/fdc/v1/foods/search",
  #  params={"query": "chicken breast", "api_key": api_key}
#)
#data = response.json()


#print(data["foods"][0]["description"])

con = sqlite3.connect("calories.db",)
cur = con.cursor()
if __name__ == "app":
    cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT UNIQUE, hash" \
    " TEXT, weight REAL, height REAL, age INTEGER, gender TEXT, activity_level REAL)"
)
    con.commit()  
    cur.execute("CREATE TABLE IF NOT EXISTS foods (food_id INTEGER PRIMARY KEY, name TEXT, kcal REAL," \
    "protein REAL, carbs REAL, fat REAL, fibre REAL) ")  
    con.commit()
    cur.execute("CREATE TABLE IF NOT EXISTS logs (log_id INTEGER PRIMARY KEY, user_id INT, food_id INT," \
    " weight INT, meal_type TEXT, date TEXT DEFAULT CURRENT_DATE, FOREIGN KEY (user_id) REFERENCES users(user_id)," \
    "FOREIGN KEY (food_id) REFERENCES foods(food_id))")
    con.commit()
    con.close()

@app.route("/")
def index():

    con = sqlite3.connect("calories.db",)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM logs JOIN foods ON logs.food_id = foods.food_id "\
               "WHERE logs.user_id = ? AND logs.date = CURRENT_DATE",(session["user_id"],)
     )
    data = cur.fetchall()
    con.commit()  
    total_kcal = 0
    total_protein = 0
    for row in data:
       total_kcal += (row["kcal"])/ 100 * row["weight"]
       total_protein += (row["protein"])/ 100 * row["weight"]
    return render_template("index.html", data = data, total_kcal = total_kcal, total_protein = total_protein)

@app.route("/login", methods = ["GET", "POST"])
def login():

    session.clear()
    if request.method == "GET":
        render_template("login.html")
    if request.method == "POST":
        if not request.form.get("username"):
            return "must provide username 400"
        if not request.form.get("password"):
            return "must provide password 400"

        con = sqlite3.connect("calories.db",)
        cur = con.cursor()
 
        cur.execute(
             "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
          )
        id = cur.fetchall()
        if len(id) != 1 or not check_password_hash(
            id[0][2], request.form.get("password")
        ):
            return "invalid username and/or password 400"
        else:
            session["user_id"] = id[0][0]
            print(session)
        con.close()
        return render_template("layout.html")
    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return "must provide username(400)"
        elif not request.form.get("password"):
            return "must provide password(400)"
        elif request.form.get("password") != request.form.get("confirmation"):
            return "passwords dont match(400)"
        else:
            try:
                con = sqlite3.connect("calories.db",)
                cur = con.cursor()
                cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", 
                            (request.form.get("username"), generate_password_hash(request.form.get("password")),))
                con.commit()
                con.close()
            except:
                return "username already exists(400)"
            return redirect("/")

    return render_template("register.html")

@app.route("/food", methods=["GET","POST"])
def food():
    if request.method == "GET":
        return render_template("food.html")
    if request.method == "POST":
        if not request.form.get("food"):
            return "no food entered 400"
        if not request.form.get("weight"):
            return "no weight set 400"
        elif int(request.form.get("weight")) < 1:
            return "weight must be positive 400"

        con = sqlite3.connect("calories.db",)
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        check = cur.execute("SELECT * FROM foods WHERE name = ?", (request.form.get("food"),))
        check = cur.fetchone()
        con.commit()
        con.close()
        weight = int(request.form.get("weight"))

        if not check:

            response = requests.get(
            "https://api.nal.usda.gov/fdc/v1/foods/search",
            params={"query": request.form.get("food"), "api_key": api_key}
            )
            data = response.json()
        
            for food in data["foods"]:
                if (food["dataType"]) == request.form.get("type"):
                    selected_food = food
                    break
        
            for nutrient in selected_food["foodNutrients"]:
                if nutrient["nutrientName"] == "Protein":
                    print(nutrient["value"])
                    protein = nutrient["value"]
                elif nutrient["nutrientName"] == "Total lipid (fat)":
                    print(nutrient["value"])
                    fat = nutrient["value"] 
                elif nutrient["nutrientName"] == "Energy" and nutrient["unitName"] == "KCAL":
                    print(selected_food["foodNutrients"])
                    print(nutrient)
                    kcal = nutrient["value"]
                elif nutrient["nutrientName"] == "Carbohydrate, by difference":
                    carbs = nutrient["value"]
                elif nutrient["nutrientName"] == "Fiber, total dietary":
                    fibre = nutrient["value"]

            con = sqlite3.connect("calories.db",)
            con.row_factory = sqlite3.Row
            cur = con.cursor()   
            cur.execute("INSERT INTO foods (name, kcal, protein, carbs, fat, fibre) VALUES (?, ?, ?, ?, ?, ?)",(
                        request.form.get("food"), kcal, protein, carbs, fat, fibre)
                        )
            cur.execute("SELECT * FROM foods WHERE name = ?", (request.form.get("food"),))
            check = cur.fetchone()
            con.commit() 
            con.close()
            return render_template("logs.html", check = check, weight = weight)
   
        else: 
            return render_template("logs.html", check = check, weight = weight)
            
    return render_template("food.html")

@app.route("/logs", methods=["GET","POST"])
def logs():
    if request.method == "POST":
        request.form.get("weight")

        con = sqlite3.connect("calories.db",)
        cur = con.cursor()   
        cur.execute("INSERT INTO logs( user_id, food_id, weight, meal_type) VALUES(?, ?, ?, ?)", (session["user_id"], request.form.get("food_id"),
                     request.form.get("weight"), request.form.get("time")),
                     )
        con.commit() 
        con.close()

    return redirect("/")

#request.form.get("food"), (kcal / 100) * int(request.form.get("weight")), (protein / 100) * int(request.form.get("weight")),
 #                       (carbs / 100) * int(request.form.get("weight")), (fat / 100) * int(request.form.get("weight")), (fibre / 100) * int(request.form.get("weight"))
