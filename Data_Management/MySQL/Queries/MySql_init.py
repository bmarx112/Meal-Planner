
# I want to add foreign keys to the tables, but phpmyadmin gets mad at me when I try
# to execute everything at once with those constraints...

init_query = '''

    DROP TABLE IF EXISTS Meal;
    CREATE TABLE Meal (
            Recipe_Id     INT NOT NULL,
            Meal_Name   TEXT,
            Meal_URL    TEXT,
            Date_Uploaded   timestamp not null default current_timestamp,
            PRIMARY KEY (Recipe_Id)
        );

    DROP TABLE IF EXISTS Ingredients;
    CREATE TABLE Ingredients (
            Ingredient_Id      INT NOT NULL AUTO_INCREMENT,
            Recipe_Id     INT NOT NULL,
            Ingredient_Name   TEXT,
            Date_Uploaded   timestamp not null default current_timestamp,
            PRIMARY KEY (Ingredient_Id)
        );

    DROP TABLE IF EXISTS Instructions;
    CREATE TABLE Instructions (
            Instruction_Id      INT NOT NULL AUTO_INCREMENT,
            Recipe_Id     INT NOT NULL,
            Step_Sequence   INT NOT NULL,
            Instruction     TEXT,
            Date_Uploaded   timestamp not null default current_timestamp,
            PRIMARY KEY (Instruction_Id)
        );

    DROP TABLE IF EXISTS Nutrition;
    CREATE TABLE Nutrition (
            Nutrient_Id     INT NOT NULL AUTO_INCREMENT,
            Recipe_Id     INT NOT NULL,
            Element   TEXT NOT NULL,
            Quantity     FLOAT,
            Unit    TEXT,
            Date_Uploaded   timestamp not null default current_timestamp,
            PRIMARY KEY (Nutrient_Id)
        );
    '''