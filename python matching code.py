import pandas as pd
import json

def change_nan(obj):
    if pd.isna(obj):
        return ""
    return obj

def is_compatible(a,b):
    '''returns True iff person a and person b are compatible'''

    for i in range(2):
        person=[a,b][i]
        other=[a,b][1-i]

        prefs=people_dic[person]["preferences"]

        if "bro" in prefs:
            if people_dic[other]["gender"] != "man":
                return False

        if "sis" in prefs:
            if people_dic[other]["gender"] != "woman":
                return False

        if "dorm" in prefs:
            if people_dic[person]["dorm"] != people_dic[other]["dorm"]:
                return False

        if "year" in prefs:
            if people_dic[person]["year"] != people_dic[other]["year"]:
                return False

    return True

data=pd.read_excel(r"Pset matching MSA edition (Responses).xlsx")

people_dic={} # dic of the form {name: {year: , dorm: , gender: ,
              # preferences: set(), classes_partner: {class:list(people)}}}


classes_dic={} # dic of the form {class: set(people names)}

for i,person in enumerate(data["Name"]):
    person_dic={}

    person_dic["dorm"]=change_nan(data["Dorm"][i]).lower()

    person_dic["year"]=change_nan(data["Class year"][i])

    person_dic["gender"]=change_nan(data["Gender"][i]).lower()


    prefs=set()

    entry=data[data.columns[4]][i]
    if not pd.isna(entry):
        for pr in ["bro","sis","year","dorm"]:
            if pr in entry:
                prefs.add(pr)

    person_dic["preferences"]=prefs


    person_classes={}
    for col in data.columns[6:]:
        class_num=data[col][i]
        if not pd.isna(class_num):
            person_classes[str(class_num)]=[]

            class_set=classes_dic.get(str(class_num),set())
            class_set.add(person)
            classes_dic[str(class_num)]=class_set

    person_dic["classes_partners_dic"]=person_classes

    people_dic[person]=person_dic

# Matching
for course,people in classes_dic.items():
    for person in people:
        dic=people_dic[person]["classes_partners_dic"]
        for other in people:
            if other!=person and is_compatible(person,other):
                dic[course].append(other)


name=input("What's your name? ")

for course,partners in people_dic[name]["classes_partners_dic"].items():
    print(course)
    print(partners)
    print()
