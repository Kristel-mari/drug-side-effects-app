from flask import Flask, render_template, request, jsonify
import pandas as pd
app = Flask(__name__)

# Load and clean the dataset
df = pd.read_csv("Data/DrugsData.zip.csv")
df.columns = df.columns.str.strip().str.lower()

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

# Autocomplete route
@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    search_type = request.args.get("type")
    term = request.args.get("term", "").lower()

    if search_type == "drug":
        matches = df[df["drug_name"].fillna("").str.lower().str.startswith(term)]
        suggestions = matches["drug_name"].dropna().drop_duplicates().head(10).tolist()

    elif search_type == "condition":
        matches = df[df["medical_condition"].fillna("").str.lower().str.startswith(term)]
        suggestions = matches["medical_condition"].dropna().drop_duplicates().head(10).tolist()

    else:
        suggestions = []

    return jsonify(suggestions)
if __name__ == "__main__":
    app.run(debug=True)

