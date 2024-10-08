# SURPMutationViewer

A python FastAPI application for viewing and commenting on mutations generated for the Racket corpus. In order to run it requires the 2234-grading directory in the same parent directory as the main.py file. I believe it should work if you just unzip that file straight from the OneDrive account, but for context my 2234-grading directory looks like\
parent_directory/

- main.py
- mutation_report.csv
- 2234-grading/
    - AssignmentX/
        - shuffled-XX/
            - text.rkt
        - ...
    - ...
\
The particular naming's of the directories are infact important. Everything else should be included in this repository, I didn't want to push that folder for obvious reasons. Additonally, requirements.txt contains everything needed for a virtual environment to run the script, and the script can just be run via python3 main.py, at which point the webserver will be hosted localy.

A couple of notes: When creating a note in the webapp, your notes will be saved to the CSV file containing all the data, thus, if you wish to share your notes, pushing & pulling is required\
A grey highlight means that all mutants which appeared on that line were killed\
A red highlight means that all mutants which appeared on that line survived\
A orange highlight means that there was a mixture of killed/survived mutants
