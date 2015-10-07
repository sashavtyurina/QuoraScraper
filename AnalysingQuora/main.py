"""
This script will contain the main part of what's happening.
"""
import json
dataset = open('quoradataset.txt')
long_questions = open('long_q.txt', 'w')

def select_long_questions(dataset):
    for s in dataset:
        jobj = json.loads(s.strip())

        if not (jobj['qbody'] and jobj['answers']):
            continue
        long_questions.write('%s\n' % str(jobj))


def main():
    log = open('logging.txt', 'w')
    questions = select_long_questions()
    for quest in questions:
        log.write('***QUESTION***\n%s\n' + quest)
        queries = construct_queries(quest)
        log.write('***QUERIES***\n')
        i = 1
        for q in queries:
            log.write('%d. %s\n' % (i, q))
            i += 1
            docs = askBing(q)
            for d in docs:
                log.write('%s\n' % d['href'])

if __name__ == '__main__':
    main()