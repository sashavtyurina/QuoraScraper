
import sys
import urllib.request
import requests
from bs4 import BeautifulSoup as bs
import re

# for dynamic scraping
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *


# This class is coming from
# https://impythonist.wordpress.com/2015/01/06/ultimate-guide-for-scraping-javascript-rendered-web-pages/
class Render(QWebPage):
  def __init__(self, url):
    self.app = QApplication(sys.argv)
    QWebPage.__init__(self)
    self.loadFinished.connect(self._loadFinished)
    self.mainFrame().load(QUrl(url))
    self.app.exec_()

  def _loadFinished(self, result):
    self.frame = self.mainFrame()
    self.app.quit()

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



def main():
    # url = 'http://www.quora.com'
    # url = 'http://pycoders.com/archive/'
    url = 'http://www.quora.com/How-should-a-Ph-D-student-deal-with-the-inherent-misalignment-of-incentives-between-graduate-students-and-advisers'
    # url = "http://www.quora.com/How-do-you-study-as-a-PhD-student"
    # url = "http://www.quora.com/PhD-Students/Where-can-I-find-good-topics-on-algorithms-to-write-about-for-a-paper"

    # page = requests.get(url, timeout=5)
    # soup = bs(page.text)
    # scrape_page(soup)

    r = Render(url)
    page = r.frame.toHtml()
    with open('dyn.html', 'w') as ff:
        ff.write(page)

    page1 = requests.get(url)
    with open('stat.html', 'w') as ff:
        ff.write(page1.text)

    # soup = bs(page)
    # with open('soup.html', 'w') as f:
    #     f.write(str(soup))


    # soup = bs(page)
    # soup = bs(str(page))
    # scrape_page(soup)


if __name__ == '__main__':
    main()

