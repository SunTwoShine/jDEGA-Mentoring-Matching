from collections import OrderedDict
from PyPDF2 import PdfFileReader
import pandas as pd
import glob
import sys


if len(sys.argv) != 4:
    sys.exit('Please enter 3 Arguments: 1 Path to mentors folder, 2 Path to mentees folder, 3 output file path + name')

path_mentors = sys.argv[1]
path_mentees = sys.argv[2]
path_output_file = sys.argv[3]

#-----------------------------------------------------------------------
# Functions for loading of filled out forms
# Answer from https://stackoverflow.com/a/43680515 by user dvska

def get_form_fields(infile):
    infile = PdfFileReader(open(infile, 'rb'))
    fields = PdfFileReader.getFields(infile)
    return OrderedDict((k, v.get('/V', '')) for k, v in fields.items())




#-----------------------------------------------------------------------
#Loading filled out forms of mentors and mentees and create DataFrames with all information

# Mentors
#Get the column names from example form
columns_mentors = get_form_fields('Anmeldung_Mentoren.pdf')
#create empty dataframe to be filled
df_mentors = pd.DataFrame(columns=columns_mentors.keys())
#read the folder with forms from mentors and fill all into the dataframe
for file in glob.glob(path_mentors + '*.pdf'):
    form_input = get_form_fields(file)
    df_temp = pd.DataFrame([form_input], columns=form_input.keys())
    df_mentors = pd.concat([df_mentors, df_temp], axis =0, ignore_index=True)



# Mentees
#get the column names from example form
columns_mentees = get_form_fields('Anmeldung_Mentees.pdf')
#create empty dataframe to be filled
df_mentees = pd.DataFrame(columns=columns_mentees.keys())
#read the folder with forms from mentees and fill all into the dataframe
for file in glob.glob(path_mentees + '*.pdf'):
    form_input = get_form_fields(file)
    df_temp = pd.DataFrame([form_input], columns=form_input.keys())
    df_mentees = pd.concat([df_mentees, df_temp], axis =0, ignore_index=True)




#-----------------------------------------------------------------------
# MATCHING-PROCESS
#-----------------------------------------------------------------------
# Create DataFrame for matching recommendations with mentees as rows and mentors as columns
# For each mentor/mentee combination, a score is calculated

#use names of the mentors for the matching recommendation dataframe
columns_matching = ['Mentee', 'Wunschmentor']
for number_mentor in range(len(df_mentors)):
    mentor = df_mentors.at[number_mentor, 'Vorname'] + ' ' + df_mentors.at[number_mentor, 'Name']
    columns_matching.append(mentor)
df_matching = pd.DataFrame(columns=columns_matching)

#insert empty row for every mentee and fill mentees name
df_matching = df_matching.reindex(list(range(0, len(df_mentees)))).reset_index(drop=True)
for number_mentee in range(len(df_mentees)):
    #insert the mentees name in first column
    df_matching.iloc[number_mentee, 0] = df_mentees.at[number_mentee, 'Vorname'] + ' ' + df_mentees.at[number_mentee, 'Name']
    #insert mentees preferred mentor in second column. Each mentee can provide two preferred mentors, these will be contacted first. If they don't accept the mentorship, another mentor from our list will be chosen
    df_matching.iloc[number_mentee, 1] = df_mentees.at[number_mentee,'Wunschmentor'] + ', ' + df_mentees.at[number_mentee,'Wunschmentor 2']



#-----------------------------------------------------------------------
# Calculation of the score for matching recommendations
# These are very specific to our mentoring program! The forms are in German, therefore the following comments will also be in German.

#there are several categories provided in the form which are used to match the mentors to mentees
#most important categories are: 
#the area of study (1. Fachgebiet), because careers in acoustics can differ greatly depending on the area of study 
#the professional goals (2. Berufliche Ziele), e.g. if a mentee wants to do a PhD, a mentor with a PhD or habilitation is preferred



#Bildung des Scores zur Bewertung der Matching-Qualität
#1. Fachgebiet (Summe der Gemeinsamkeiten)
#2. Berufliche Ziele (8 Unterkategorien - Bewertung in -1,0,1 (-1: Wunsch nicht erfüllt, 0: nicht gewünscht, 1: Wunsch erfüllt))
#3. Hospitation (Bewertung in -1,0,1)
#4. Auslandserfahrung (Bewertung in -1,0,1)
#5. Förderung (Summe der Gemeinsamkeiten)

for number_mentee in range(len(df_matching)):
    for number_mentor, name_mentor in enumerate(df_matching.columns.values[2:]):
        
        #Wohnort
        #gleicher Wohnort ist Ausschlusskriterium, da sie sich eventuell bereits kennen oder sogar zusammen arbeiten/studieren
        if df_mentees.at[number_mentee,'Adresse'].lower() == df_mentors.at[number_mentor,'Adresse'].lower():
            df_matching.at[number_mentee, name_mentor] = 'gleicher Wohnort'
        
        else:
            matching_score = []
            
            
            #Fachgebiet
            #Pro Fachgebiet, in dem beide aktiv sind, gibt es einen Punkt
            study_field = 0
            if df_mentees.at[number_mentee,'Fachgebiet'] == \
               df_mentors.at[number_mentor,'Fachgebiet'] == '/Yes':
                study_field += 1
            for area in range(2,13):
                if df_mentees.at[number_mentee,'Fachgebiet_'+str(area)] == \
                   df_mentors.at[number_mentor,'Fachgebiet_'+str(area)] == '/Yes':
                    
                    study_field += 1
            matching_score.append(study_field)
            
            
            
            
            #Berufliche Ziele (Nach dem Studium)
            #Wertung: -1, 0, 1
            #Themen, die den Mentee interessieren, die ein Mentor nicht erfüllt, werden Punkte abgezogen.
            #Themen, die für den Mentee nicht interessant sind, werden neutral betrachtet.
            #Themen, die den Mentee interessieren, die ein Mentor erfüllt, werden positiv gewertet.
            goal = [None] * 8
            
            # 1 Wissenschaft
            # Mentor: Arbeit in der Wissenschaft
            goal_number = 0
            if df_mentees.at[number_mentee,'Nach dem Studium'] == '/Yes' and \
               df_mentors.at[number_mentor,'Karriereerfahrung'] == '/Yes':
                goal[goal_number] = 1
            elif df_mentees.at[number_mentee,'Nach dem Studium'] == '/Yes' and \
                 df_mentors.at[number_mentor,'Karriereerfahrung'] == '/Off':
                goal[goal_number] = -1
            elif df_mentees.at[number_mentee,'Nach dem Studium'] == '/Off':
                goal[goal_number] = 0
            
            # 2 Industrie
            # Mentor: Arbeit in der Wirtschaft
            goal_number += 1
            if df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
               df_mentors.at[number_mentor,'Karriereerfahrung_2'] == '/Yes':
                goal[goal_number] = 1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
                 df_mentors.at[number_mentor,'Karriereerfahrung_2'] == '/Off':
                goal[goal_number] = -1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Off':
                goal[goal_number] = 0
            
            # 3 Promotion
            # Mentor: Promotion oder Habilitation
            goal_number += 1
            if df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
              (df_mentors.at[number_mentor,'Bildungsabschluss'] == '/2' or \
               df_mentors.at[number_mentor,'Bildungsabschluss'] == '/3'):
                goal[goal_number] = 1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
                (df_mentors.at[number_mentor,'Bildungsabschluss'] != '/2' or \
                 df_mentors.at[number_mentor,'Bildungsabschluss'] != '/3'):
                goal[goal_number] = -1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Off':
                goal[goal_number] = 0
            
            # 4 Ingenieurbüro
            # Mentor: Arbeit in der Wirtschaft
            goal_number += 1
            if df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
               df_mentors.at[number_mentor,'Karriereerfahrung_2'] == '/Yes':
                goal[goal_number] = 1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
                 df_mentors.at[number_mentor,'Karriereerfahrung_2'] == '/Off':
                goal[goal_number] = -1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Off':
                goal[goal_number] = 0
            
            # 5 Experte
            # Mentor: Fachlaufbahn oder Projektleitung
            goal_number += 1
            if df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
              (df_mentors.at[number_mentor,'Karriereerfahrung_5'] == '/Yes' or \
               df_mentors.at[number_mentor,'Karriereerfahrung_6'] == '/Yes'):
                goal[goal_number] = 1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
                (df_mentors.at[number_mentor,'Karriereerfahrung_5'] == '/Off' or \
                 df_mentors.at[number_mentor,'Karriereerfahrung_6'] == '/Off'):
                goal[goal_number] = -1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Off':
                goal[goal_number] = 0
            
            # 6 Selbstständigkeit
            # Mentor: Selbstständigkeit
            goal_number += 1
            if df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
               df_mentors.at[number_mentor,'Karriereerfahrung_4'] == '/Yes':
                goal[goal_number] = 1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
                 df_mentors.at[number_mentor,'Karriereerfahrung_4'] == '/Off':
                goal[goal_number] = -1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Off':
                goal[goal_number] = 0
            
            # 7 Führung
            # Mentor: Führungsposition oder Projektleitung
            goal_number += 1
            if df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
              (df_mentors.at[number_mentor,'Karriereerfahrung_3'] == '/Yes' or \
               df_mentors.at[number_mentor,'Karriereerfahrung_6'] == '/Yes'):
                goal[goal_number] = 1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes' and \
                (df_mentors.at[number_mentor,'Karriereerfahrung_3'] == '/Off' or \
                 df_mentors.at[number_mentor,'Karriereerfahrung_6'] == '/Off'):
                goal[goal_number] = -1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Off':
                goal[goal_number] = 0
            
            # 8 Weiß noch nicht
            goal_number += 1
            if df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Yes':
                goal[goal_number] = 1
            elif df_mentees.at[number_mentee,'Nach dem Studium_'+str(goal_number+1)] == '/Off':
                goal[goal_number] = 0
            
            matching_score.append(goal)
            
            
            
            #Hospitation
            #Wertung: -1, 0, 1
            #Wenn der Mentee eine Hospitation wünscht, der Mentor dies aber nicht ermöglichen kann, wird ein Punkt abgezogen.
            #Wenn der Mentee keine Hospitation wünscht oder darauf keinen Wert legt, wird neutral gewertet.
            #Wenn der Mentee eine Hospitation wünscht und der Mentor dies ermöglichen kann, wird positiv gewertet.
            if df_mentees.at[number_mentee,'Hospitation'] == '/1'and \
              (df_mentors.at[number_mentor,'Hospitation'] == '/1' or \
               df_mentors.at[number_mentor,'Hospitation'] == '/2') :
                internship = 1
            elif df_mentees.at[number_mentee,'Hospitation'] == '/1'and \
                 df_mentors.at[number_mentor,'Hospitation'] == '/3':
                internship = -1
            elif df_mentees.at[number_mentee,'Hospitation'] == '/2':
                internship = 0
            matching_score.append(internship)
            
            
            
            #Auslandserfahrung
            #Wertung: -1, 0, 1
            #Wenn der Mentee einen Mentor mit Auslandserfahrung wünscht, der Mentor dies aber nicht hat, wird ein Punkt abgezogen.
            #Wenn der Mentee keine Auslandserfahrung wünscht oder darauf keinen Wert legt, wird neutral gewertet.
            #Wenn der Mentee einen Mentor mit Auslandserfahrung wünscht und der Mentor dies hat, werden positiv gewertet.
            if df_mentees.at[number_mentee,'Auslandserfahrung Mentor'] == '/1'and \
               df_mentors.at[number_mentor,'Auslandserfahrung'] == '/1':
                abroad = 1
            elif df_mentees.at[number_mentee,'Auslandserfahrung Mentor'] == '/1'and \
                 df_mentors.at[number_mentor,'Auslandserfahrung'] == '/2':
                abroad = -1
            elif df_mentees.at[number_mentee,'Auslandserfahrung Mentor'] == '/2' or \
                 df_mentees.at[number_mentee,'Auslandserfahrung Mentor'] == '/3':
                abroad = 0
            matching_score.append(abroad)
            
            
            
            
            #Förderung
            #Pro Förderungsthema, das den Mentee besonders interessiert und der Mentor dies unterstützt, gibt es einen Punkt
            assistance = 0
            if df_mentees.at[number_mentee,'F#C3#B6rderung'] == \
               df_mentors.at[number_mentor,'F#C3#B6rderung'] == '/Yes':
                assistance += 1
            for area in range(2,10):
                if df_mentees.at[number_mentee,'F#C3#B6rderung_'+str(area)] == \
                   df_mentors.at[number_mentor,'F#C3#B6rderung_'+str(area)] == '/Yes':
                    assistance += 1
            matching_score.append(assistance)
            
            
            
            #save the matching score at the specific mentor/mentee combination
            df_matching.at[number_mentee, name_mentor] = matching_score




#Save recommendations to file
df_matching.to_csv(path_output_file)
