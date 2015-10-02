'''
Scraping Quora questions and answers
https://www.quora.com/sitemap/questions - a list of ~100 questions.
https://www.quora.com/sitemap/questions?page_id=2 - get the next batch of questions

Cookies are stolen from the browser session and are in cookies.txt in json format
Credentials are in credentials.txt (email and password) in json format

Header is used to not get blocked (or to decrease the chance of getting blocked), to ensure
same-origin policy

From each question page we want:
question (title + body)
date - last asked
answer + date + upvotes
? list of related questions (not sure if we need it yet)
'''

import sys
# import urllib.request
import requests
from bs4 import BeautifulSoup as bs
import re
import json
import datetime
from datetime import timedelta
import random
import time

# for dynamic scraping
# from PyQt4.QtGui import *
# from PyQt4.QtCore import *
# from PyQt4.QtWebKit import *
# from PyQt4.QtNetwork import *
#
#



COOKIES = 'cookies.txt'
CREDENTIALS = 'credentials.txt'
INIT_URL = 'https://www.quora.com/sitemap/questions'
DATASET_FILE = 'quoradataset.txt'
NEW_QUESTIONS_DATASET = 'new_questions.txt'
LOG_FILE = open('log.txt', 'a')

NEW_QUESTION = 'NEW'
OTHER_ERROR = 'ERROR'
SUCCESS = 'SUCCESS'
SUCCES_CODE = [NEW_QUESTION, OTHER_ERROR, SUCCESS]

QUESTION_HREF = 'href'
QUESTION_TITLE = 'qtitle'
QUESTION_BODY = 'qbody'
QUESTION_DATE = 'qdate'


ANSWERS = 'answers'
ANSWER_DATE = 'adate'
ANSWER_TEXT = 'atext'
ANSWER_UPVOTES = 'aupvotes'

RELATED_QUESTIONS = 'rel_q'
DATE_COLLECTED = 'date_collctd'

# how old should a question be, to be harvested by us
DAYS_OLD = 7

DAYS_OF_WEEK = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}

# load cookies to enable logged in session
cookies = json.loads(open(COOKIES).read())

# # This class is coming from
# # https://impythonist.wordpress.com/2015/01/06/ultimate-guide-for-scraping-javascript-rendered-web-pages/
# class Render(QWebPage):
#   def __init__(self, url):
#     self.app = QApplication(sys.argv)
#     QWebPage.__init__(self)
#
#
#     # list of QNetworkCookie
#     self.networkcookies = []
#     for cookie_name in cookies.keys():
#         cookie = QNetworkCookie(name=QByteArray(cookie_name), value=QByteArray(cookies[cookie_name]))
#         self.networkcookies.append(cookie)
#
#     # cookiejar
#     self.cookieJar = QNetworkCookieJar()
#     self.cookieJar.setAllCookies(self.networkcookies)
#
#     # manager
#     self.manager = QNetworkAccessManager()
#     self.manager.setCookieJar(self.cookieJar)
#
#     # QWebPage.setNetworkAccessManager(self.manager)
#     self.setNetworkAccessManager(self.manager)
#
#     self.loadFinished.connect(self._loadFinished)
#     self.mainFrame().load(QUrl(url))
#     self.app.exec_()
#
#   def _loadFinished(self, result):
#     self.frame = self.mainFrame()
#     self.app.quit()

def scrape_page(soup):
    '''
    :param soup:
    :return:
    given a url, scrapes question text and its answers (if any)
    question consists of a title and description
    answer consists just of the answer text
    '''

    # The title of the question is in the span tag with the class, containing 'question_text'
    # div = soup.find_all('span', id=re.compile('question_text'))
    # title = div[0].text
    # print(title)

    # question text
    # div = soup.find_all(class_=re.compile('question_details_text'))
    # text = div[0].text
    # print(text)

    # answers
    answer_divs = soup.find_all('div', class_='AnswerListDiv')[0].find_all('div', id=re.compile('answer_content'))
    answers = []
    for d in answer_divs:
        a = d.find_all(id=re.compile('container'))
        answers.append(a[0].text)
    #
    # for a in answers:
    #     print(a)
    i = 0


def normalize_date(date_str, delim):

    today = datetime.date.today()
    today.weekday()
    date_str = ''.join(date_str.split(delim))

    date_asked = None

    # 2am
    timeonly = re.match('[0-9]{1,2}[a,p]m}', date_str)
    ago = re.match('[0-9]{1,2}[mh] ago$', date_str)
    if ago or timeonly:
        date_asked = today

    dow = date_str in list(DAYS_OF_WEEK.keys())
    if dow:
        # what's the difference btw today and day published
        if DAYS_OF_WEEK[date_str] > today.weekday():
            diff = len(list(DAYS_OF_WEEK.keys())) - DAYS_OF_WEEK[date_str] + today.weekday()
        else:
            diff = today.weekday() - DAYS_OF_WEEK[date_str]

        date_asked = today - timedelta(diff)

    if not (ago or dow):
        try:
            date_asked = datetime.datetime.strptime(date_str, '%d %b, %Y').date()
        except ValueError:
            date_asked = datetime.datetime.strptime(date_str + ', ' + str(today.year), '%d %b, %Y').date()

    # day_month = re.match('^[0-9]{1,2} [A-Za-z]{3}$', date_str)
    # day_month_year = re.match('^[0-9]{1,2} [A-Za-z]{3}, [0-9]{4}$', date_str)

    return date_asked


'''
this html contains a page with questions listed on it
ex.: https://www.quora.com/sitemap/questions?page_id=2

This function returns a list of question titles and there corresponding urls

'''
def scrape_questions_list(html):
    '''
    :param html: a page with questions listed on it
ex.: https://www.quora.com/sitemap/questions?page_id=2
    :return: a list of dicts, where dict = {'href': <href>, 'title': <title>}
    '''
    soup = bs(html)
    content_div = soup.find('div', class_='content contents main_content fixed_header ContentWrapper').contents[0]
    list_div = content_div.find('div')

    # iterating through the list of questions
    questions = []
    for q_div in list_div.children:
        a = q_div.a
        questions.append({QUESTION_HREF: a['href'], QUESTION_TITLE: a.text})

    return questions


def scrape_single_question(html):
    '''
    :param html: html code of a page with single question
     ex: https://www.quora.com/I-am-visiting-Berlin-next-month-What-are-my-chances-to-get-hook-with-some-woman
    :return: a json object with the following fields:
    qbody, qdate, related_questions:[list of hrefs], answers: [atext, aupvotes, adate]
    '''

    soup = bs(html)
    q_json = {}
    today = datetime.date.today()

    try:
        # question date
        last_asked = soup.find('div', class_='QuestionLastActivityTime')
        if not last_asked:
            date_asked = today
        else:
            last_asked = last_asked.text
            date_asked = normalize_date(last_asked, 'Last asked: ')

        # we don't process questions asked less than 2 weeks ago.
        if abs((today - date_asked).days) < DAYS_OLD:
            print('The question was asked less than a week ago.')
            return None, NEW_QUESTION

        q_date = str(date_asked)

        body = soup.find('span', id=re.compile('full_text_content')).text

        q_json[DATE_COLLECTED] = str(today)
        q_json[QUESTION_DATE] = q_date
        q_json[QUESTION_BODY] = body

        # related questions
        related_list = soup.find('div', class_='question_related list').ul.find_all('li', class_='related_question')
        related_questions = []
        for rel_q in related_list:
            rel_href = rel_q.div.div.a['href']
            related_questions.append('https://www.quora.com' + rel_href)
        q_json[RELATED_QUESTIONS] = related_questions

        q_json[ANSWERS] = []
        # find answers
        answer_divs = soup.find('div', class_='AnswerPagedList PagedList').find_all('div', class_='pagedlist_item')
        for a_div in answer_divs[:-1]:
            answer = {}
            a_date = a_div.find('div', class_='ContentFooter AnswerFooter').span.a.text
            if a_date.startswith('Written'):
                a_date = str(normalize_date(a_date, 'Written '))
            else:
                a_date = str(normalize_date(a_date, 'Updated '))

            a_upvotes = a_div.find('div', class_='Answer ActionBar').contents[0].a.contents[1].text
            a_text = a_div.find(id=re.compile('container')).text

            answer[ANSWER_DATE] = a_date
            answer[ANSWER_TEXT] = a_text
            answer[ANSWER_UPVOTES] = a_upvotes

            q_json[ANSWERS].append(answer)
    except AttributeError as er:
        print("Attribure error: {0}".format(er))
        print(sys.exc_info()[0])
        # print("ERROR!")
        # print(er.__traceback__)
        # print(er.__cause__)
        return None, OTHER_ERROR

    return q_json, SUCCESS

def main():



    # imitating browser session to ensure same-origin policy
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'}

    # set up params (page number)
    page_num = 49


    params = {'page_id': page_num}

    output = open(DATASET_FILE, 'a')

    new_questions_dataset = open(NEW_QUESTIONS_DATASET, 'a')

    while True:

        # try:
        params = {'page_id': page_num}
        LOG_FILE.write('Starting to scrape page %d\n' % page_num )

        r = requests.get(INIT_URL, params=params, cookies=cookies, headers=headers)
        page_num += 1

        print('Processing: ' + r.url)
        LOG_FILE.write('Processing: ' + r.url + '\n')

        # get a list of questions
        questions = scrape_questions_list(r.text)

        # shuffling the list of questions to not access them one by one, perhaps reducing the chances of getting blocked
        random.shuffle(questions)

        # process each question
        for q in questions:

            print('Scraping question: ' + q[QUESTION_HREF])
            LOG_FILE.write('Scraping question: ' + q[QUESTION_HREF] + '\n')

            # r = Render(q[QUESTION_HREF])
            # q_html_js = r.frame.toHtml()
            # with open('dyn.html', 'w') as ff:
            #   ff.write(page)

            q_html = requests.get(q[QUESTION_HREF], cookies=cookies, headers=headers).text
            with open('test.html', 'w') as test:
                test.write(q_html)

            question, success = scrape_single_question(q_html)
            print('Success = %s' % success)
            LOG_FILE.write('Success = %s\n' % success)

            if not question:
                if success is NEW_QUESTION:
                    print('That was a new question. Saving its URL')
                    LOG_FILE.write('That was a new question. Saving its URL\n')

                    new_questions_dataset.write('%s\n' % q[QUESTION_HREF])
                # add idle time to reduce chances of getting blocked
                sl = random.randrange(10, 30)
                print('Sleeping for %d seconds' % sl)
                LOG_FILE.write('Sleeping for %d seconds\n' % sl)
                time.sleep(sl)

                print('Continuing')
                continue

            question[QUESTION_TITLE] = q[QUESTION_TITLE]
            question[QUESTION_HREF] = q[QUESTION_HREF]

            output.write('%s\n' % str(question))
            print('Finished scraping this question.')

            sl = random.randrange(30, 90)
            print('Sleeping for %d seconds' % sl)
            time.sleep(sl)

    output.close()

    # url = 'http://www.quora.com'
    # url = 'http://pycoders.com/archive/'
    # url = 'http://www.quora.com/How-should-a-Ph-D-student-deal-with-the-inherent-misalignment-of-incentives-between-graduate-students-and-advisers'
    # url = "http://www.quora.com/How-do-you-study-as-a-PhD-student"
    # url = "http://www.quora.com/PhD-Students/Where-can-I-find-good-topics-on-algorithms-to-write-about-for-a-paper"

    # page = requests.get(url, timeout=5)
    # soup = bs(page.text)
    # scrape_page(soup)


    #
    # page1 = requests.get(url)
    # with open('stat.html', 'w') as ff:
    #     ff.write(page1.text)

    # soup = bs(page)
    # with open('soup.html', 'w') as f:
    #     f.write(str(soup))


    # soup = bs(page)
    # soup = bs(str(page))
    # scrape_page(soup)


if __name__ == '__main__':
    # i = 9
    main()

