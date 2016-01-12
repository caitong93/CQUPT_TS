# -*- coding: utf-8 -*-

import json
from time import sleep
from copy import deepcopy

import requests

from . import db
from .models import Submission

HEADER = {
    'Host': 'acm.hust.edu.cn',
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0",
    'Accept': "application/json, text/javascript, */*; q=0.01",
    'Accept-Encoding': "gzip, deflate",
    'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
    'X-Requested-With': "XMLHttpRequest",
    'Referer': "http://acm.hust.edu.cn/vjudge/problem/status.action"
}

COLUMN = {
    'data': '',
    'name': '',
    'searchable': 'true',
    'orderable': 'false',
    'search': {
        'value': '',
        'regex': 'false'
    }
}

JSON = {
    'draw': '1',
    'columns': {},
    'order': {
        '0':    {
            'column': '0',
            'dir': 'desc'
        }
    },
    'start': '0',
    'length': '20',
    'search': {
        'value': '',
        'regex': 'false'
    },
    'un': '',
    'OJId': 'All',
    'probNum': '',
    'res': '0',
    'language': '',
    'orderBy': 'run_id'
}

URL = 'http://acm.hust.edu.cn/vjudge/problem/fetchStatus.action'


Result = {
    1: ['accepted'],
    2: ['presentation'],
    3: ['wrong answer'],
    4: ['time limit'],
    5: ['memory limit'],
    6: ['output limit'],
    7: ['runtime'],
    8: ['compile', 'compilation'],
}

DEFAULT = 99

Lang = {
    'C++': 0,
    'Java': 1,
    'Python': 2,
    'C': 3,
    'Pascal': 4,
    'C#': 5,
    'Ruby': 6,
    'Other': 99
}


def getLangIdFromString(s):
    return Lang['Other']


def getResultIdFromString(s):
    s = s.lower()
    for k, v in Result.items():
        for pattern in v:
            if pattern in s:
                return k
    return DEFAULT


class Crawler(object):

    def __init__(self):
        self.s = requests.session()
        self.s.headers.update(HEADER)

    def run(self, Ids):
        """

        :param Ids: Handle list.
        :return: None.
        """
        result = {}
        for _id in Ids:
            print u'[ start ] %s ......' % _id
            retry = 5
            while retry:
                try:
                    result[_id] = self.craw_by_id(_id)
                    print u'[ done ] %s, %d records fetched' % (_id, len(result[_id]))
                    break
                except:
                    print u'[ retry ] %s ......' % _id
                    continue
            sleep(3)

        assert len(result) == len(Ids)

        failed_list = []
        _s = {}
        for i in Submission.query.all():
            _s[i.rid] = i
        for user in result:
            try:
                for submission in result[user]:
                    rid = int(submission[0])
                    tmp = None
                    if rid in _s:
                        tmp = _s[rid]
                        if tmp.result != DEFAULT:
                            continue
                        else:
                            tmp.result = getResultIdFromString(submission[3])
                    else:
                        tmp = Submission(
                            rid=int(submission[0]),
                            username=submission[1],
                            result=getResultIdFromString(submission[3]),
                            lang=getLangIdFromString(submission[6]),
                            oj=submission[11],
                            pid=submission[12]
                        )
                    if tmp:
                        db.session.add(tmp)
                db.session.commit()
            except Exception, e:
                failed_list.append(user)
        return failed_list

    def craw_by_id(self, _id):
        start = 0
        step = 1000
        payload = self.build_payload(un=_id, length=str(step))

        ret = []
        while True:
            payload['start'] = str(start)
            r = self.s.post(URL, data=payload)
            data = r.json()['data']
            if data:
                ret.extend(r.json()['data'])
            if (len(data) < step):
                break
            start += step

        return ret


    def build_payload(self, **kw):
        payload = deepcopy(JSON)

        for col in range(0, 12):
            tmp = deepcopy(COLUMN)
            tmp['data'] = str(col)
            payload['columns'][str(col)] = tmp

        for k, v in kw.items():
            payload[k] = v

        return payload


def test():
    payload = deepcopy(JSON)
    payload['un'] = 'slowlight'

    payload['start'] = '0'

    for col in range(0, 12):
        tmp = deepcopy(COLUMN)
        tmp['data'] = str(col)
        payload['columns'][str(col)] = tmp

    r = requests.post(URL, headers=HEADER, data=payload)
    print r.status_code
    # print json.dumps(r.json(), ensure_ascii=False, indent=4)

if __name__ == '__main__':
    # test()
    c = Crawler()
    c.run()