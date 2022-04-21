# jDEGA-Mentoring-Matching
Script for recommendations for the matching of mentees and mentors of the jDEGA mentoring program.

The script is just used for assistance with the matching process. The matching itself is done manually by the jDEGA mentoring organisation team.

## Using the script

#### Loading the script: Arguments
```console
python matching_recommendations.py PATH/TO/FOLDER/FOR/MENTORS PATH/TO/FOLDER/FOR/MENTEES OUTPUTFILE.csv
```

#### Requirements

1. There have to be two files in the same folder as the script: **Anmeldung_Mentoren.pdf** and **Anmeldung_Mentees.pdf** \
These files contain the pdf-forms used for registration to the mentoring program. They are used to create the internal DataFrames. Only the field names are used for this. Filled out spaces are not considered.
2. Folder with all files of mentors
3. Folder with all files of mentees

#### Output

Table with mentees as rows and mentors as columns. First column is the mentees names, second column is for two preferred mentors of that mentee, the rest is the available mentors.

Score for each mentor/mentee combination consisting of [a, [b1, b2, b3, b4, b5, b6, b7, b8], c, d, e]:
* a. area of study (sum of all categories)
* b. goals (-1,0,1)
   * b1. working in academia
   * b2. working in the industry
   * b3. getting a PhD
   * b4. working in an engineering office
   * b5. expert career
   * b6. start-up of own business
   * b7. management career
   * b8. not yet known 
* c. internship (-1,0,1)
* d. experience working abroad (-1,0,1)
* e. areas of assistance (sum of all categories)


#### Further Information
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
