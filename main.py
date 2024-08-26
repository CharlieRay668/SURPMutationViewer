from fastapi import FastAPI, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
from typing import List, Optional
import os
import html

# Initialize the FastAPI app
app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define Pydantic models for request and response
class Mutation(BaseModel):
    NumMutant: int
    MutatorType: str
    file: str
    MutantSourceLine: int
    MutantSourceColumn: int
    MutantSource: str
    MutantDestinationFile: str
    MutantDestinationRow: float
    MutantDestinationCol: float
    MutantDestination: str
    Result: str
    mutation_score: float
    Notes: str

class MutationList(BaseModel):
    mutations: List[Mutation]

def read_csv(file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"{file_path} not found")
    return pd.read_csv(file_path)

@app.get("/mutations", response_model=MutationList)
def get_mutations(file: str = Query("mutation_report.csv")):
    data = read_csv(file)
    mutations = data.to_dict(orient="records")
    return MutationList(mutations=mutations)

@app.get("/", response_class=HTMLResponse)
def home(file: str = Query("mutation_report.csv")):
    data = read_csv(file)
    # Group by file and calculate mutation scores
    mutation_scores = data.groupby('file')['Result'].value_counts(normalize=True).unstack(fill_value=0)
    mutation_scores['MutationScore'] = mutation_scores.get('failed', 0)
    
    # Assignment based on the file path
    data['Assignment'] = data['file'].apply(lambda x: x.split("/")[2])
    
    unique_files = data['file'].unique()
    file_list_html = "<table id='fileTable'><thead><tr><th onclick='sortTable(0)'>Path</th><th onclick='sortTable(1)'>Assignment</th><th onclick='sortTable(2)'>Mutation Score</th><th>Action</th></tr></thead><tbody>"
    
    for file_item in unique_files:
        file_path = file_item.lstrip("./")
        assignment = data[data['file'] == file_item]['Assignment'].iloc[0]
        mutation_score = mutation_scores.loc[file_item, 'MutationScore'] if file_item in mutation_scores.index else 0
        file_list_html += f"""
            <tr>
                <td>{html.escape(file_path)}</td>
                <td>{html.escape(assignment)}</td>
                <td>{mutation_score:.2f}</td>
                <td><a href="/source/{html.escape(file_path)}?file={html.escape(file)}"><button>Inspect</button></a></td>
            </tr>
        """
    file_list_html += "</tbody></table>"
    
    html_content = f"""
    <html>
    <head>
    <title>Mutation Viewer</title>
    <link rel="stylesheet" type="text/css" href="/static/styles.css">
    <script src="/static/scripts.js"></script>
    </head>
    <body>
    <h1>Select a file to view mutations</h1>
    <form method="get" action="/">
        <label for="file">Choose a CSV file:</label>
        <select name="file" id="file">
            <option value="mutation_report.csv" {"selected" if file == "mutation_report.csv" else ""}>mutation_report.csv</option>
            <option value="random_sample.csv" {"selected" if file == "random_sample.csv" else ""}>random_sample.csv</option>
        </select>
        <button type="submit">Load</button>
    </form>
    {file_list_html}
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/source/{file_path:path}", response_class=HTMLResponse)
def get_source(file_path: str, file: str = Query("mutation_report.csv")):
    old_file_path = file_path
    file_path = f"./{old_file_path}"
    try:
        with open(file_path, "r") as source_file:
            source_code = source_file.readlines()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

    data = read_csv(file)
    file_mutations = data[data['file'] == f'./{old_file_path}']
    file_mutations['MutantSourceLine'] = file_mutations['MutantSourceLine'].astype(int)
    file_mutations['MutantSourceColumn'] = file_mutations['MutantSourceColumn'].astype(int)

    # Summarize mutations
    num_mutants = len(file_mutations)
    mutant_lines = file_mutations['MutantSourceLine'].unique().tolist()
    
    # Highlight the mutations in the source code
    highlighted_code = ""
    for line_num, line in enumerate(source_code, start=1):
        line_mutations = file_mutations[file_mutations['MutantSourceLine'] == line_num]
        if not line_mutations.empty:
            mutation_details = ""
            results = line_mutations['Result'].unique()
            if len(results) > 1:
                highlight_class = "highlight-mixed"
            elif results[0] == "failed":
                highlight_class = "highlight-failed"
            else:
                highlight_class = "highlight-passed"
            
            min_start_col = line_mutations['MutantSourceColumn'].min()
            for _, mutation in line_mutations.iterrows():
                destination = mutation['MutantDestination']
                mutant_type = mutation['MutatorType']
                mutant_status = mutation['Result']
                if mutant_status == "failed":
                    mutant_status = "Killed"
                else:
                    mutant_status = "Survived"
                notes = mutation['Notes'] if pd.notna(mutation['Notes']) else ""
                mutant_index = data[(data['file'] == f'./{old_file_path}') & (data['MutantDestination'] == destination)].index[0]
                mutation_details += f"<p>Mutation ID: {mutant_index}</p><p>Mutation type: {mutant_type}</p><p>Mutant Status: {mutant_status}</p><p>{html.escape(destination)}</p><br><p>Notes: <textarea id='note-{mutant_index}' rows='8' cols='50' onchange='updateNotes({mutant_index}, this.value)'>{html.escape(notes)}</textarea></p><hr>"
            highlighted_line = (line[:min_start_col] +
                                f'<span class="{highlight_class}" data-tooltip="Mutations: {len(line_mutations)}" onclick="showMutations(`{mutation_details}`)">{line[min_start_col:]}</span>')
            highlighted_code += f"{line_num}: {highlighted_line}<br>"
        else:
            highlighted_code += f"{line_num}: {line}<br>"

    summary_html = f"""
    <div class="summary">
        <p>Total number of mutants: {num_mutants}</p>
        <p>Lines with mutations: {', '.join(map(str, mutant_lines))}</p>
    </div>
    """

    html_content = f"""
    <html>
    <head>
    <link rel="stylesheet" type="text/css" href="/static/styles.css">
    <script src="/static/scripts.js"></script>
    </head>
    <body>
    <div class="left-panel">
        <h1>Source Code for {html.escape(file_path)}</h1>
        {summary_html}
        <pre>{highlighted_code}</pre>
        <a href="/?file={html.escape(file)}">Back to Home</a>
    </div>
    <div class="right-panel">
        <div class="top-right-panel">
            <h2>Mutations</h2>
            <div id="top-right-panel-content"></div>
        </div>
    </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/update_note")
def update_note(mutant_index: int = Form(...), note: str = Form(...), file: str = Form(...)):
    print(file)
    data = read_csv(file)
    if mutant_index < 0 or mutant_index >= len(data):
        raise HTTPException(status_code=404, detail="Invalid mutant index")
    data.at[mutant_index, 'Notes'] = note
    data.to_csv(file, index=False)
    return JSONResponse(status_code=200, content={"message": "Note updated successfully"})

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
