#coding=utf-8

import time
import json
import datetime

import requests

from flask import g

from clover.common.utils.mongo import Mongo
from clover.common.utils import get_timestamp
from clover.common.utils import get_friendly_id
from clover.common.utils.helper import derivation
from clover.common.interface.expect import Expect


class Service(object):

    def __init__(self):
        self.db = Mongo()
        g.data = []

    def replace_variable(self, data):
        """
        # 这里对请求数据进行变量替换，将变量替换为具体值。
        # 变量和其值可以在"配置管理 -> 全局变量"里设置。
        # 目前支持host，header与param的变量替换。
        # 变量与值存储使用团队与项目进行区分，不同的团队与项目允许出现同名变量。
        :param data:
        :return:
        """
        filter = {
            'team': data['environment'].get('team'),
            'project': data['environment'].get('project')
        }
        _, results = self.db.search("environment", "variable", filter)
        results.extend(g.data)
        print(50 * '*')
        print(results)

        data['request']['host'] = derivation(data['request'].get('host'), results)
        data['request']['path'] = derivation(data['request'].get('path'), results)

        if 'header' in data['request']:
            for header in data['request']['header']:
                header['key'] = derivation(header['key'], results)

        if 'param' in data['request']:
            for param in data['request']['param']:
                param['key'] = derivation(param['key'], results)

        return data

    def make_request(self, data):
        """
        :param data:
        :return:
        """
        # 发送http请求
        method = data['request'].get("method")
        host = data['request'].get("host")
        path = data['request'].get("path")
        header = data['request'].get('header', {})
        payload = data['request'].get('param', {})
        url = host + path

        # 将[{'a': 1}, {'b': 2}]转化为{'a': 1, 'b': 2}
        if header:
            header = {key: val for key, val in header}

        # 将[{'a': 1}, {'b': 2}]转化为{'a': 1, 'b': 2}
        if payload:
            payload = {key: val for key, val in payload}

        if method == 'get':
            response = requests.request(method, url, params=payload, headers=header)
        else:
            response = requests.request(method, url, data=payload, headers=header)

        # 这里将响应的状态码，头信息和响应体单独存储，后面断言或提取变量会用到
        data['response'] = {
            'status': response.status_code,
            'header': dict(response.headers),
            'content': response.text
        }
        print(response.url)
        # 如果是json相应，这里对原始相应进行替换。
        if data['response']['header']['Content-Type'].find("application/json") != -1:
            data['response']['json'] = json.loads(data['response']['content'])

        return data

    def convert_format(self, data):
        """
        # 这个函数暂时保留，如有必要，用于后续讲xml等其它格式数据进行转换。
        :param data:
        :return:
        """
        return data

    def execute_assertion(self, data):
        """
        :param data:
        :return:
        """
        expect = Expect(data)
        expect.test()
        return data

    def extract_variables(self, data):
        """
        :param data:
        :return:
        """
        if 'extract' not in data or not data['extract']:
            return data

        for extract in data['extract']:
            sel = extract['selector']
            expr = extract['expression']
            name = extract['expected']
            # 从这里开始使用分隔符取数据
            tmp = data['response']['json']
            for item in expr.split('.'):
                try:
                    item = int(item)
                    tmp = tmp[item]
                except ValueError:
                    tmp = tmp.get(item, None)
                    if tmp is None:
                        break
            g.data.append({'name': name, 'value': tmp})

        return data

    def record_result(self, data):
        """
        :param data:
        :return:
        """
        data['_id'] = get_friendly_id()
        self.db.insert("interface", "history", data)
        return data

    def execute(self, data):
        """
        :param data:
        :return: 返回值为元组，分别是flag，message和接口请求后的json数据。
        """
        self.replace_variable(data)
        self.make_request(data)
        self.convert_format(data)
        self.execute_assertion(data)
        self.extract_variables(data)
        self.record_result(data)
        print(g.data)
        return data

    def save(self, data):
        """
        # 将页面数据保存到数据库。
        :param data:
        :return:
        """
        data['_id'] = get_friendly_id()
        data['created'] = datetime.datetime.now()

        # 这里对数据进行解包
        request = data.pop('request')
        data['name'] = request['name']
        data['host'] = request['host']
        data['path'] = request['path']
        data['method'] = request['method']
        data['header'] = request['header']
        data['params'] = request['param']
        environment = data.pop('environment')
        data['team'] = environment['team']
        data['project'] = environment['project']

        self.db.insert("interface", "case", data)
        return data['_id']

    def trigger(self, data):
        """
        :param data:
        :return:
        """
        # 需要通过case_id先查询到数据库里的测试用例。
        # run_id是一次运行的记录，查测试报告时使用。
        run_id = get_friendly_id()
        cases = []
        ids = data['cases']
        for id in ids.split(','):
            results = self.db.search('interface', 'case', {'_id': id})
            if not results:
                continue
            cases.append(results[0])

        # 这个data是要存储到数据库的测试报告数据。
        data = {
            'run_id': run_id,
            'time': {
                'start': 0,
                'end': 0,
                'cost': 0,
            },
            'count': {
                'total': 0,
                'run': 0,
                'success': 0,
                'fail': 0,
                'skip': 0
            },
            'result': []
        }
        start = time.time()
        # 判断每一个测试用例是否通过。
        for case in cases:
            case.setdefault('status', 0)
            case.setdefault('message', '测试通过！')
            data['count']['total'] += 1
            data['count']['run'] += 1
            status, message, _ = self.execute(case)
            if status == 0:
                data['count']['success'] += 1
            else:
                data['count']['fail'] += 1
                case['status'] = status
                case['message'] = message
            data['result'].append(case)
        print("{0} {1} {2} {3}".format(data['count']['total'], data['count']['run'], \
                                       data['count']['success'], data['count']['fail']))
        end = time.time()
        # 通过start与end时间戳计算整个测试耗时
        data['time']['start'] = get_timestamp(start)
        data['time']['end'] = get_timestamp(end)
        data['time']['cost'] = "共执行{0:0.3}秒".format(end - start)
        print(data)
        # 将测试报告数据写入数据库。
        self.db.insert('interface', 'report', data)
        print(run_id)
        return run_id

    def delete(self, data):
        """
        :param data:
        :return:
        """
        count, id_list = 0, data.pop('id_list')
        for id in id_list:
            count += self.db.delete("interface", "case", {'_id': id})
        return count

    def list(self, data):
        """
        :param data:
        :return:
        """
        count, results = self.db.search("interface", "case", data)
        return (count, results) if results else (0, [])

    def __del__(self):
        if self.db:
            self.db.close()
