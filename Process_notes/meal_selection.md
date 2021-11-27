
# Selecting The Meals

## <u>Criteria</u>
### Meal Diversity
1. Idea: Distance formula WRT main ingredient qtys
### Popularity Stratification
#### bucketize based on <b>rating</b> and <b>number of reviews</b>
1. Idea: Calculate Z-Score for each meal WRT stats of meals within meal_Category. Multiply rating by Z-score of num. ratings
2. Idea: Devise multivar scoring formula using both rating and popularity to derive a comparable score.


## <u>Searching Model: Simulated Annealing</u>
### Objective
1. Find % difference between the sum of a nutrient across three meals and daily nutrition target for user
2. Multiply each pct diff (a decimal) by a weight factor of importance for the given nutrient
3. Sum weighted values to find E(s)

### Candidate Selection
For each of the three meal slots:
1. Create an n-dimensional vector of nutrient quantities by adding/subtracting random perturbations to each nutrient value of the current meal in the category.
2. The perturbations will be aleatory, based on a random pct of the standard deviation for the nutrient in each category
3. With this new vector, find the new closest meal within the n-d 'nutrient' space, assign it to the respective meal slot for the new candidate

### Acceptance Probability Function
1. The traditional Metropolis selection criterion will be used: $${e^(\frac{-(E(s_{0}) - E(s_{1}))}{T})}$$

### Similarity of Ingredients between Proposed State and Previous Days' States
1. Instead of nutrients, we will use the presence and quantity of ingredients to discern similarity between meals. Meals will be evaluated within their own category: breakfast vs breakfast, lunch vs lunch, etc.
2. Jaccard Index: Quantify similarity of presence of elements in category <i>i</i>. This will not account for varying magnitudes of ingredient amount. 