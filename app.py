from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the dataset
df = pd.read_csv("Data/DrugsData.zip.csv")
df.columns = df.columns.str.strip().str.lower()  # Clean column names

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    query_type = None

    if request.method == "POST":
        search_type = request.form.get("search_type")
        query = request.form.get("query", "").strip().lower()

        if search_type == "drug":
            matches = df[df['drug_name'].str.lower() == query].drop_duplicates(subset=['drug_name'])
            if not matches.empty:
                result = matches[['drug_name', 'medical_condition', 'side_effects']].to_dict(orient='records')
                query_type = "side_effects"
            else:
                result = "No matching drug found."

        elif search_type == "condition":
            matches = df[df['medical_condition'].str.lower().str.contains(query)]
            if not matches.empty:
                # Drop duplicates and sort by drug_name
                result = (
                    matches[['medical_condition', 'drug_name']]
                    .drop_duplicates()
                    .sort_values(by='drug_name', key=lambda col: col.str.lower())
                    .to_dict(orient='records')
                )
                query_type = "drugs"
            else:
                result = "No matching condition found."

    return render_template("index.html", result=result, query_type=query_type)

if __name__ == "__main__":
    app.run(debug=True)
