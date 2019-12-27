import requests
import json
import xlwt
from bs4 import BeautifulSoup as BS
import pymongo
from time import sleep

queries = [u'面试', u'实习', u'找工作', u'简历']
entries = [u'search_terms', u'search_rank', u'question_url', u'question_title',
           u'question_follow_num', u'question_view_num',
           u'question_top_answer_id', u'question_top_answer_username']

headers = {
    'cookie': "",
    'Host': 'www.zhihu.com',
    'Referer': 'http://www.zhihu.com/',
    'user-agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) Ap"
    "pleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safar"
    "i/604.1",
    'Accept-Encoding': 'gzip'}


def GET(url, headers):
    page = ""
    while page == "":
        try:
            page = requests.get(url, headers=headers)
            assert(page != None)
            return page
        except requests.ConnectionError as e:
            print("ERR: {}".format(e))
            print("sleep for 5 seconds")
            sleep(5)
            print("continuing")
            continue


def get_link_content(question_url, query_num):
    html = GET(question_url, headers=headers)
    bs = BS(html.text, 'html.parser')
    res = bs.find("script", id='js-initialData')
    dt = json.loads(res.text)
    userid = list(dt['initialState']['entities']['questions'].keys())[0]
    question_view_num = dt['initialState']['entities']['questions'][userid]['visitCount']
    question_follow_num = dt['initialState']['entities']['questions'][userid]['followerCount']

    answer_url_tmp = "https://www.zhihu.com/api/v4/questions/{}" \
    "/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Crew" \
    "ard_info%2Cis_collapsed%2Cannotation_action%2Canotation_detail%2Ccollap" \
    "se_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count" \
    "%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment" \
    "_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_" \
    "info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized" \
    "%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recogn" \
    "ized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%" \
    "5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&li" \
    "mit=5&offset=0&platform=desktop&sort_by=default"

    answer_url = answer_url_tmp.format(query_num)
    ans_response = GET(answer_url, headers=headers)

    ans_response.encoding = "utf-8"
    L3 = json.loads(ans_response.text)
    question_top_answer_username = L3['data'][0]['author']['name']
    question_top_answer_id = L3['data'][0]['author']['id']

    return (question_follow_num, question_view_num,
            question_top_answer_username, question_top_answer_id)
    # print(question_top_answer_username)


def get_query_content(query):
    global ct, total, worksheet, collection
    for i in range(50):
        url_tmp = "https://www.zhihu.com/api/v4/search_v3?t=general&q={}" \
            "&correction=1&offset={}&limit=20&lc_idx={}&show_all_topics=0&se" \
            "arch_hash_id=3d21e38b5e93277e80022091d9992046&vertical_info=1" \
            "%2C1%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C1"

        url = url_tmp.format(query, i * 20, i * 20 + 7)
        print(url)
        response = GET(url, headers=headers)
        response.encoding = "utf-8"
        if response.status_code != 200:
            continue

        L1 = json.loads(response.text, strict=False)
        for index in range(len(L1['data'])):
            item = L1['data'][index]
            if('object' not in item.keys() or 'type' not in item['object'].keys()):
                continue
            if (item['object']['type'] != 'answer'):
                continue

            link = "https://www.zhihu.com/question/" + item['object']['question']['id']
            if (collection.count_documents({"search_terms": query,
                                            "question_url": link}) != 0):
                continue

            ct += 1
            total += 1
            # print(str(ct) + ", " + str(item['index']) + ": " + item['highlight']['title'])

            (q_follow_num, q_view_num, q_top_ans_usrname,
             q_top_ans_id) = get_link_content(link, item['object']['question']['id'])


            title = item['highlight']['title'].replace("</em>", "")
            title = title.replace("<em>", "")
            # print(title + "\n")

            data = [query, ct, link, title, q_follow_num, q_view_num,
                    q_top_ans_usrname, q_top_ans_id]

            for i, entry in enumerate(entries, start=0):
                worksheet.write(total, i, label=data[i])

            update_data = {"search_terms": query,
                           "search_rank": ct,
                           "question_url": link,
                           "question_title": title,
                           "question_follow_num": q_follow_num,
                           "question_view_num": q_view_num,
                           "question_top_answer_username": q_top_ans_usrname,
                           "question_top_answer_id": q_top_ans_id}

            doc_ct = collection.estimated_document_count()
            collection.insert_one(update_data)
            doc_ct_new = collection.estimated_document_count()
            assert(doc_ct == doc_ct_new - 1)


if __name__ == '__main__':
    ct = 0
    total = 0

    excel_path = '/code/docker_result.xls'

    # creating and initializing excel workbook
    workbook = xlwt.Workbook(encoding='utf-8')

    worksheet = workbook.add_sheet('my_worksheet')
    for i, entry in enumerate(entries, start=0):
        worksheet.write(0, i, label=entry)

    workbook.save(excel_path)
    # initializing mongodb database
    # client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
    client = pymongo.MongoClient('mongodb')
    mydb = client['spiderdb']  # create a new database called spiderdb
    collist = mydb.list_collection_names()
    if "wondercv_exe" in collist:
        print("already exists collection with name "
              "wondercv_exe in database spiderdb")

    collection = mydb['wondercv_exe']
    collection.delete_many({})  # clear any preexisting data

    # getting data from queries
    for query in queries:
        ct = 0
        get_query_content(query)
        workbook.save(excel_path)
        # workbook.save('/users/k.j./Documents/GitHub/'
        #              'zhihu-spider/crontab-search_result.xls')


'''
wd.get("https://www.zhihu.com/question/295453435")
wd.find_element_by_xpath('//*[@id="root"]/div/div[2]/header/div[1]/div[2]/div/div/button[2]').click()
wd.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div/div/div[1]/div/form/div[1]/div[2]').click()
wd.find_element_by_name('username').send_keys('13718310500')
wd.find_element_by_name('password').send_keys('640315')
wd.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div/div/div[1]/div/form/button').click()
'''
