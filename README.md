# CALORIE-TRACKER
### Video Demo: <https://youtu.be/vbf5yuxGz0E>
### Description:

My project, called Calorie Tracker, is a web app used to help track your daily calories and protein. It uses the USDA FoodData Central API to look up foods the user searches for, and calculates their caloric and macronutrient impact by multiplying the values by the weight the user enters. The web app also calculates the user's estimated maintnance calories (TDEE) using data provided by the user, like their heigh, weight, age, gender, and activity level.

### Features 
- Registration and login with hashed password
- A biometric profile of the user with their(weight, height, age, gender and activity level) used to estimate their BMR and TDEE using the Mifflin-ST Jeor formula. New users are redirected to set this up right after their first login if the user didnt set it up already.
- Food search via the USDA FoodData Central API, storing the values localy for already searched foods for quicker search and saving on API requests.
- Food logging by meal (breakfast, lunch, dinner) reseting daily.
- A dashboard showing calories eaten so far today againts the daily target, visualised with a progress bar. 
- Ability to delete miss-logged food


### How it works 

The app is built with Flask and SQLite, using three related tables:

- **users** - stores login credentials and biometric data(wight, height, age, gender, activity level), with biometric fields left nullable until the user fills them in.
- **foods** - stores the data of searched food items allowing for shorter wait times while searching for food already in the database also saving on API requests.
- **logs** - stores the food user decided to log for the day in and allows user to see the food inside the index page 

**Routes:**
- '/' - allows the user to see their TDEE, what they ate in the day for breakfast, lunch and dinner also shows them progress bar towards their caloric goal 
- '/login' - authenticates the user and redirects them into /biometrics if they dont have that data already setup 
- '/lougt' - clears the session.
- '/register' - allows the user to create their own account with username and hashed password
- '/food' - searches for the name of the food set, first from the foods database if its not there calls an API request 
- '/logs' - saves the entry of the food with its weight and time of entry to display on todays index 
- '/biometrics' - lets user set their own biometric information use to calculate the formula for their BMI and TDEE
- '/delete' - used to delete unwanted entries into the logs table 

### Design decisions

**Storing** already searched foods localy rather than constantly calling the API to save time and api requests.

**Filtering** by dataType in USDA database to allow the user to choose between generic foods and branded versions

**Calculating instead of storing** the users calorirc maintenance gets calculated on the go instead of being pre saved to allow for grater flexibility 

### Limitations 

- The USDA FoodData Central doesnt include every name of every food so it can be a limiting factr
- Search requires the user to type the exact name of the food theres no autocomplete
- The macros can be not exact since there are many similar types of the same food so you have to be very exact with your names specifically problematic with generic names 
- No manual food entry 

### Setup 
1. Create a virtual enviroment and activate it 
2. Installe required libraries with pip install (Flask, Flask-Session, requests, python-dotenv, werkzeug).
3. Create a .env file in the project root containing your own API key from the USDA database
4. Run the app with flask run 

### Disclosure 

I used many resources to make this web app amongst them:

- **Claude** used in a way like the cs50 duck as learning aid I used it to explain concepts like API, help with css costumisation and as a helper with debugging code 
- **W3schools** used for HTML and CSS formating 
- **StackOwerflow** used to find help amongst other people during debugging
- **Reddit** used to find help with debugging code and how APIs work 
- **USDA** used the API to enable search of foods in the webapp
