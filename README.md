# jDEGA-Mentoring-Matching
Script for recommendations for the matching of mentees and mentors of the jDEGA mentoring program

## Loading the script: Arguments
```console
python matching_recommendations.py PATH/TO/FOLDER/FOR/MENTORS PATH/TO/FOLDER/FOR/MENTEES OUTPUTFILE
```

**Requirements**
1. There have to be two files in the same folder as the script: **Anmeldung_Mentoren.pdf** and **Anmeldung_Mentees.pdf** \
These files contain the pdf-forms used for registration to the mentoring program. They are used to create the internal DataFrames. Only the field names are used for this. Filled out spaces are not considered.
2. Folder with all files of mentors
3. Folder with all files of mentees

## Using the script
The script is making a summary of all mentor/mentee combinations. Each combination gets a score.

All files of mentors taking part in this round of the program should be placed in one folder.
All files of mentees registered for this round should be placed in a different folder.

If someone provided a file that cannot be used directly, e.g. a scan of the form, this has to be manually corrected. \
If someone didn't include their residence, this should be changed to the current city they work/study in. The residence is an important criterion for matching, as people with the same residence will never be matched together. The program should provide new insides and not connect people who see each other every day.


## Environment
Create a new environment using the requirements file in this repo.

```console
pyenv local 3.9.4
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
