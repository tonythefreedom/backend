from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from gensim.models.word2vec import Word2Vec
import json
import pandas
from nltk.corpus import stopwords
import csv
from operator import itemgetter
import datetime
import sys
sys.stdout.flush()

#######################################################################################################
# Setting
#######################################################################################################
test_str = 'burgerking'
test_str = test_str.lower()

#local path
#MODEL_PATH = "/Users/kyubum/PycharmProjects/API1n2_Final/create_model/embedding_model_SkipGram"
#TABLE_PATH = "/Users/kyubum/PycharmProjects/API1n2_Final/create_model/word_count_table.json"
#WM_PATH = "/Users/kyubum/PycharmProjects/API1n2_Final/create_model/weight_matrix.csv"
#N_GRAM_CASE_PATH = "/Users/kyubum/PycharmProjects/API1n2_Final/create_model/n_gram_case_dic.json"

#Server path
MODEL_PATH = "/usr/local/etc/django/model/gensim_model_skip_gram"
TABLE_PATH = "/usr/local/etc/django/model/word_count_table.json"
WM_PATH = "/usr/local/etc/django/model/weight_df.csv"



model = Word2Vec.load(MODEL_PATH)
with open(TABLE_PATH) as f:
    term_frequencys = f.readlines()


#######################################################################################################
#   API1 Functions
#######################################################################################################
# return frequency function
term_frequency_list = [json.loads(term_frequency, encoding = 'utf-8') for term_frequency in term_frequencys]
term_frequency_dict = term_frequency_list[0]
def return_frequency(word):
    word = word.lower()
    frequency = 0
    try :
        frequency = term_frequency_dict[str(word)]
    except :
        frequency = frequency
    return frequency

# input word -> similar word list return function(output : 2차원 리스트)
def return_similar_word_list(word):
    similar_output_list = []
    xx = model.most_similar(positive = [str(word)], topn = 40)
    for i in xx:
        yy = i[0]
        similar_tem_list=[]
        similar_tem_list.append(yy)
        for j in xx:
            if model.similarity(yy, j[0]) >= 0.75:
                similar_tem_list.append(j[0])
                xx.remove(j)
        similar_output_list.append(similar_tem_list)
    return similar_output_list

# input word -> similar word list return function(세부항목 name 모두)
def return_similar_word_name(kb_list):
    similar_output_list_name = []
    for i in kb_list:
        similar_output_list_name.append(i[0])
    return similar_output_list_name

# similar_word_list -> average frequency function (output: 1차원 리스트)
def return_avg_frequency(word_list):
    similar_word_frequency = []
    for i in word_list:
        frequency_tem_list = []
        avg = 0
        for j in i:
            frequency_tem_list.append(return_frequency(j))
        avg = sum(frequency_tem_list) / len(frequency_tem_list)
        similar_word_frequency.append(int(avg))
    return(similar_word_frequency)

# Final_API1_function
def API1(input_keyword):
    input_keyword = input_keyword.lower()
    input_keyword = input_keyword.strip()
    input_keyword = input_keyword.replace(' ','_')
    out_list = []
    try :
        if return_similar_word_list(input_keyword) != []:
            kb = return_similar_word_list(input_keyword)
            dic_name = return_similar_word_name(kb)
            dic_frequency = return_avg_frequency(kb)
            for i in range(len(dic_name)):
                out_dict = {}
                out_dict['name'] = dic_name[i]
                out_dict['frequency'] = dic_frequency[i]
                out_list.append(out_dict)

            out_list3 = sorted(out_list, key=itemgetter('frequency'), reverse = True)
            result = json.dumps(out_list3)

    except KeyError :
        out_list = ['No Result']
        result = json.dumps(out_list)

    return(result)



#######################################################################################################
#   API2 Function
#######################################################################################################
stop_words = set(stopwords.words('english'))

# Load Weight_matrix
weight_final_df = pandas.read_csv(WM_PATH, encoding = 'utf-8')
weight_final_df.index = ['food','service','ambience','value']
weight_final_df = weight_final_df.drop('Unnamed: 0',1)
col_list = list(weight_final_df.columns.values)

# Return Score Function
def API2_function(input_list):
    menu_name = input_list
    food_score_list = []
    service_score_list = []
    ambience_score_list = []
    value_score_list =[]

    for i in menu_name:
        input_str_list = []
        test_str = i.lower()
        test_str = test_str.replace(".","")
        test_str = test_str.replace("!","")
        input_str_list = test_str.split(' ')

        for j in input_str_list:
            food_score_list_tem = []
            service_score_list_tem = []
            ambience_score_list_tem = []
            value_score_list_tem = []

            if j in col_list:
                food_score_list_tem.append(weight_final_df[j][0])
                service_score_list_tem.append(weight_final_df[j][1])
                ambience_score_list_tem.append(weight_final_df[j][2])
                value_score_list_tem.append(weight_final_df[j][3])
            else:
                food_score_list_tem.append(0)
                service_score_list_tem.append(0)
                ambience_score_list_tem.append(0)
                value_score_list_tem.append(0)

        food_score_list.append(sum(food_score_list_tem))
        service_score_list.append(sum(service_score_list_tem))
        ambience_score_list.append(sum(ambience_score_list_tem))
        value_score_list.append(sum(value_score_list_tem))

    menu_name_list = menu_name
    out_list = []
    for i in range(len(menu_name_list)):
        out_dict = {}
        out_dict['menu'] = menu_name_list[i]
        out_dict['price_score'] = round(value_score_list[i],4)
        out_dict['taste_score'] = round(food_score_list[i],4)
        out_dict['service_score'] = round(service_score_list[i],4)
        out_dict['ambience_score'] = round(ambience_score_list[i],4)
        out_dict['avg_score'] = round((value_score_list[i] + food_score_list[i] + service_score_list[i] + ambience_score_list[i])/4 , 4)
        out_list.append(out_dict)
    #out_json = json.dumps(out_list)
    return(out_list)


def API2(menu_list):
    test_list = menu_list.split(',')
    out_list = API2_function(test_list)
    out_before_sort = sorted(out_list, key=itemgetter('avg_score'))
    if len(out_before_sort) > 3:
        out_list_sorting = [out_before_sort[-1], out_before_sort[-2], out_before_sort[-3], out_before_sort[-4]]
    elif len(out_before_sort) == 3:
        out_list_sorting = [out_before_sort[-1], out_before_sort[-2], out_before_sort[-3]]
    elif len(out_before_sort) == 2:
        out_list_sorting = [out_before_sort[-1], out_before_sort[-2]]
    else:
        out_list_sorting = [out_before_sort[-1]]

    result = json.dumps(out_list_sorting)
    return(result)
#######################################################################################################
# 리퀘스트 id 로 파라미터 보내기
#######################################################################################################
result = "{}"
def index(request):
    if request.GET["id"] == "nlp1" :
        test_str = request.GET["keyword"]
        print("API1_Starts : " , datetime.datetime.now().time(), flush = True)
        result = API1(test_str)
        print("API1_Ends   : " , datetime.datetime.now().time() , " : " , result, flush = True)

    elif request.GET["id"] == "nlp2" :
        test_str = request.GET["menu_list"]
        #n_gram_case_dic에 포함된 문자는 ' ' -> '_' 전처리 필요!
        print("API2_Starts : " , datetime.datetime.now().time(), flush = True)
        result = API2(test_str)
        print("API2_Ends   : " , datetime.datetime.now().time() , " : " , result, flush = True)
    
    return HttpResponse(result)