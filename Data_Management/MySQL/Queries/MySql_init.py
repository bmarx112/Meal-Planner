

init_query = [
    '''SET FOREIGN_KEY_CHECKS = 0;
    ''',
    '''
    DROP TABLE IF EXISTS Meal;
    ''', 
    '''
    CREATE TABLE Meal (
            Recipe_Id     INT NOT NULL,
            Meal_Name   VARCHAR(255),
            Meal_Category   VARCHAR(100),
            Meal_URL    VARCHAR(255),
            Date_Uploaded   timestamp not null default current_timestamp,
            PRIMARY KEY (Recipe_Id)
        );
    ''', 
    '''
    DROP TABLE IF EXISTS Ingredients;
    ''',
    '''
    CREATE TABLE Ingredients (
            Ingredient_Id      INT NOT NULL AUTO_INCREMENT,
            Recipe_Id     INT NOT NULL,
            Ingredient_Name   VARCHAR(255),
            Date_Uploaded   timestamp not null default current_timestamp,
            PRIMARY KEY (Ingredient_Id),
            FOREIGN KEY (Recipe_Id) REFERENCES Meal(Recipe_Id)
        );
    ''', 
    '''
    DROP TABLE IF EXISTS Instructions;
    ''', 
    '''
    CREATE TABLE Instructions (
            Instruction_Id      INT NOT NULL AUTO_INCREMENT,
            Recipe_Id     INT NOT NULL,
            Step_Sequence   INT NOT NULL,
            Instruction     TEXT,
            Date_Uploaded   timestamp not null default current_timestamp,
            PRIMARY KEY (Instruction_Id),
            FOREIGN KEY (Recipe_Id) REFERENCES Meal(Recipe_Id)
        );
    ''', 
    '''
    DROP TABLE IF EXISTS Nutrition;
    ''', 
    '''
    CREATE TABLE Nutrition (
            Nutrient_Id     INT NOT NULL AUTO_INCREMENT,
            Recipe_Id     INT NOT NULL,
            Element   VARCHAR(100) NOT NULL,
            Quantity     FLOAT,
            Unit    VARCHAR(5),
            Date_Uploaded   timestamp not null default current_timestamp,
            PRIMARY KEY (Nutrient_Id),
            FOREIGN KEY (Recipe_Id) REFERENCES Meal(Recipe_Id)
        );
    ''',
    '''
    SET FOREIGN_KEY_CHECKS = 1;
    ''']
