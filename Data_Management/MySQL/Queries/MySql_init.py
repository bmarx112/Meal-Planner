
init_query = '''
    DROP TABLE IF EXISTS Meal;
    CREATE TABLE Meal (
            Recipe_Id     INTEGER NOT NULL PRIMARY KEY UNIQUE,
            Meal_Name   TEXT,
            Meal_URL    TEXT,
            Date_Uploaded   timestamp not null default current_timestamp
        );

    DROP TABLE IF EXISTS Ingredients;
    CREATE TABLE Ingredients (
            Recipe_Id     INTEGER NOT NULL,
            Ingredient_Name   TEXT,
            Date_Uploaded   timestamp not null default current_timestamp
        );

    DROP TABLE IF EXISTS Instructions;
    CREATE TABLE Instructions (
            Recipe_Id     INTEGER NOT NULL,
            Step_Sequence   INTEGER NOT NULL,
            Instruction     TEXT,
            Date_Uploaded   timestamp not null default current_timestamp
        );

    DROP TABLE IF EXISTS Nutrition;
    CREATE TABLE Nutrition (
            Recipe_Id     INTEGER NOT NULL,
            Element   TEXT NOT NULL,
            Quantity     FLOAT,
            Unit    TEXT,
            Date_Uploaded   timestamp not null default current_timestamp
        );
    '''