#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import time
import settings
from grab import Grab
from lxml import etree
from commons import WebDriver

__author__ = "whoami"
__version__ = "0.0.0"
__date__ = "27.04.16 20:27"
__description__ = """"""


class Parser:
    site_dump_file = 'web.htm'
    json_file = 'json.txt'
    target_url = 'https://live.fonbetsport.com/?locale=ru'
    api_url = 'http://rustraf.com/fonbet.php'

    events_xpath = './/table[@id="lineTable"]/tbody/tr'
    event_arrow_xpath = ".//table[@id='lineTable']/tbody/tr/td/div[1]"

    def __init__(self):
        self.parser = etree.HTMLParser(encoding='utf-8')

        self.driver = WebDriver()
        self.driver.get(self.target_url)
        self.script_disable()
        self.show_details()

    def load_site(self):
        self.dump_site()
        self.page = etree.parse(self.site_dump_file, parser=self.parser)

    @staticmethod
    def _get_segment(cnt, tr):
        td = tr.getchildren()[0]

        div = td.getchildren()[0].getchildren()[1]

        segment_id = tr.attrib['id'][len('segment'):]

        return dict(name=div.text if div else 'unknown', segment=int(segment_id), games=list())

    def _get_root_event(self, segment_index, event_id, tr):
        root_json = dict()
        for td in tr.getchildren():
            if td is None:
                continue
            if 'eventCellName' in td.attrib.get('class', ''):
                if td.getchildren():
                    for div in td.getchildren():
                        if div.attrib.get('class') in 'event':
                            span = div.getchildren()[0]
                            root_json['eventNumber'] = span.text
                            separator = ['/', '—']
                            if separator[1] in span.tail:
                                root_json['play1'] = span.tail.split(separator[1])[0]
                                root_json['play2'] = span.tail.split(separator[1])[1]
                            else:
                                root_json['play1'] = span.tail.split(separator[0])[0]
                                root_json['play2'] = span.tail.split(separator[0])[1]
                        elif div.attrib.get('class') in 'eventDataWrapper':
                            for in_div in div.getchildren():
                                if in_div.attrib.get('class') in ['eventTimeLive', 'eventScore']:
                                    root_json[in_div.attrib['class']] = in_div.text
            else:
                try:
                    if td.attrib['class'].startswith('eventArrow') or td.attrib['class'].startswith('eventStar'):
                        continue
                    root_json[td.attrib['id'][len(event_id):]] = td.text
                except KeyError:
                    print(td.attrib)

        if root_json:
            self.result_json['actions'][segment_index]['games'].append(root_json)

    def _get_child_event(self, segment_index, event_index, event_id, tr):
        chid_json = dict()
        for td in tr.getchildren():
            if td is None:
                continue
            if 'eventCellName' in td.attrib.get('class'):
                if td.getchildren():
                    for div in td.getchildren():
                        if div.attrib.get('class') in 'event':
                            span = div.getchildren()[0]
                            chid_json['eventNumber'] = span.text
                            chid_json["eventName"] = span.tail
                        elif div.attrib.get('class') in 'eventDataWrapper':
                            for in_div in div.getchildren():
                                if in_div.attrib.get('class') in ['eventTimeLive', 'eventScore']:
                                    chid_json[in_div.attrib['class']] = in_div.text
            else:
                try:
                    if td.attrib['class'].startswith('eventArrow') or td.attrib['class'].startswith('eventStar'):
                        continue
                    chid_json[td.attrib['id'][len(event_id):]] = td.text
                except KeyError:
                    print(td.attrib)

        if chid_json:
            if not self.result_json['actions'][segment_index]['games'][event_index].get('round'):
                self.result_json['actions'][segment_index]['games'][event_index]['round'] = list()
            self.result_json['actions'][segment_index]['games'][event_index]['round'].append(chid_json)

    def _get_event_details(self, segment_index, tr, child_index=None, root_index=None):

        def row_wrapper_p2p(str_point):
            out_wrapper = list()
            inner_wrapper = list()
            ths = thead.getchildren()[1]
            for body_tr in body_trs:
                for i, td in enumerate(body_tr):
                    if str_point in ths[i].text.lower():
                        if inner_wrapper:
                            out_wrapper.append(inner_wrapper)
                        inner_wrapper = list()
                    inner_wrapper.append({ths[i].text: td.text})
            else:
                if inner_wrapper:
                    out_wrapper.append(inner_wrapper)
                table_json['description'].append(out_wrapper)

        def row_wrapper(*args):
            ths = thead.getchildren()[len(thead) - 1]
            for tr in body_trs:
                wrapper = list()
                for i, td in enumerate(tr):
                    wrapper.append({ths[i].text: td.text})
                else:
                    table_json['description'].append(wrapper)

        details_json = list()
        div = []

        for td in tr.getchildren():
            if str(td.attrib.get('class')) not in 'detailsTD':
                continue
            else:
                div = td.getchildren()[0]
                break

        for table in div.getchildren():
            table_json = dict()

            thead = table.getchildren()[0]
            body_trs = table.getchildren()[1].getchildren()

            name = thead.getchildren()[0].getchildren()[0].text

            if name:
                table_json['name'] = name
            table_json['description'] = list()

            target_point = {'Индивидуальный тотал': 'тотал', 'Форы': 'фора'}
            case_of = {'Индивидуальный тотал': row_wrapper_p2p, 'Форы': row_wrapper_p2p}
            case_of.get(name, row_wrapper)(target_point.get(name, None))

            details_json.append(table_json)

        if details_json:
            if child_index is not None:
                if not self.result_json['actions'][segment_index]['games'][root_index]['round'][child_index].get('detailsTD'):
                    self.result_json['actions'][segment_index]['games'][root_index]['round'][child_index]['detailsTD'] = list()
                self.result_json['actions'][segment_index]['games'][root_index]['round'][child_index]['detailsTD'].append(details_json)
            else:
                if not self.result_json['actions'][segment_index]['games'][root_index].get('detailsTD'):
                    self.result_json['actions'][segment_index]['games'][root_index]['detailsTD'] = list()
                self.result_json['actions'][segment_index]['games'][root_index]['detailsTD'].append(details_json)

    def parsing_site(self):
        print('Parsing site')
        self.result_json = dict(time=0, actions=list())
        segment_index = 0
        event_index = 0
        child_event_index = 0
        event_id = ''

        trs = self.page.xpath(self.events_xpath)

        for cnt, tr in enumerate(trs):
            tr_id = tr.attrib['id']

            if event_id.startswith('event') and not event_id.endswith('details'):
                if event_id not in tr_id:
                    self.send_onclick(event_id)
            event_id = tr_id

            if tr_id.startswith('segment'):
                self.result_json['actions'].append(dict(self._get_segment(cnt, tr)))
                segment_index = len(self.result_json['actions']) -1
            elif tr_id.startswith('event') and not tr_id.endswith('details'):
                if 'level1' in tr.attrib['class']:
                    self._get_root_event(segment_index, tr_id, tr)
                    event_index = len(self.result_json['actions'][segment_index]['games']) -1
                else:
                    self._get_child_event(segment_index, event_index, tr_id, tr)
                    child_event_index = len(self.result_json['actions'][segment_index]['games'][event_index]['round']) -1
            elif tr_id.endswith('details'):
                if 'level1' in tr.attrib['class']:
                    self._get_event_details(segment_index, tr, root_index=event_index)
                else:
                    self._get_event_details(segment_index, tr, child_index=child_event_index, root_index=event_index)
        else:
            if not event_id.endswith('details'):
                self.send_onclick(event_id)
        print('Parsing site...OK')

    def show_details(self):
        print('Shoing tables')
        try:
            events = self.driver.get_elements_by_xpath(self.event_arrow_xpath)
            for event in events:
                # self.driver.btn_click(event)
                event_id = self.driver.get_element_info(event, 'id')
                if event_id:
                    self.send_onclick(event_id)
        except Exception as e:
            print('Shoing tables...ERROR')
        else:
            print('Shoing tables...OK')

    def dump_site(self):
        print('Dumping site')
        try:
            with open('web.htm', 'w') as f:
                f.write(self.driver.page_source)
        except Exception as e:
            print('Dumping site...ERROR')
        else:
            print('Dumping site...OK')

    def script_disable(self):
        print('Disabling scripts')
        try:
            self.driver.execute_script('client.lineUpdateBuff = client.lineUpdate;')
            self.driver.execute_script('client.lineUpdate = null;')
        except Exception:
            print('Disabling scripts...ERROR')
        else:
            print('Disabling scripts...OK')

    def script_enable(self):
        print('Enabling scripts')
        try:
            self.driver.execute_script('client.lineUpdate = client.lineUpdateBuff;')
        except Exception:
            print('Enabling scripts...ERROR')
        else:
            print('Enabling scripts...OK')

    def load_json(self):
        print('### Loading JSON data ###')
        try:
            with open(self.json_file, 'r') as f:
                return json.loads(f.read())
        except Exception as e:
            print('Error with message: {!r}'.format(e))
        else:
            print('### JSON loaded ###')

    def send_onclick(self, elem_id):
        try:
            event_div_id = 'eventName{}'.format(elem_id[len('event'):])
            self.driver.execute_script('document.getElementById({!r}).onclick()'.format(event_div_id))
        except Exception:
            print('Send event "onclick" to element id "{}"...ERROR'.format(elem_id))

    def save_json(self):
        if settings.send_to_url:
            print('### Sending json data to url ###')

            g = Grab(connect_timeout=120, timeout=60)
            try:
                print('Send post data to {!r}'.format(self.api_url))
                g.go(self.api_url, post=dict(data=json.dumps(self.result_json, indent=1, ensure_ascii=0)))
            except Exception as e:
                print('Error with message: {!r}'.format(e))
            finally:
                print('### Sending complete ###')
                del g

        if settings.save_to_file:
            print('### Save JSON to file ###')
            try:
                with open(self.json_file, 'w') as f:
                    json.dump(self.result_json, f, indent=1, ensure_ascii=0)
            except Exception as e:
                print('Error with message: {!r}'.format(e))
            else:
                print('### JSON saved ###')

    @staticmethod
    def rm_html_tags(source):
        text = re.sub(r'\s+', ' ', re.sub(r'\<[^\>]*\>', '', source))
        return text


class Timer(object):
    def __enter__(self):
        self._startTime = time.monotonic()

    def __exit__(self, type, value, traceback):
        print("Elapsed time: {:.9f} sec".format(time.monotonic() - self._startTime))


def timer(fun):
    time_story = list()
    max_time = 0.0
    min_time = 999.9
    average_time = 0.0

    def wrapper(*args, **kwargs):
        nonlocal max_time, min_time, average_time, time_story

        start_time = time.monotonic()
        fun(*args, **kwargs)
        end_time = time.monotonic() - start_time

        if min_time > end_time:
            min_time = end_time

        if max_time < end_time:
            max_time = end_time

        time_story.append(end_time)
        buffer = 0
        for t in time_story:
            buffer += t
        average_time = buffer / len(time_story)

        print("*" * 20,
              "Elapsed time: {:.9f} sec".format(end_time),
              "Min. time {:.9f} sec".format(min_time),
              "Max. time {:.9f} sec".format(max_time),
              "Average time {:.9f} sec".format(average_time),
              "*" * 20, sep='\n')

    return wrapper


@timer
def parse():
    parser.script_enable()
    time.sleep(1)
    parser.script_disable()

    parser.load_site()
    parser.parsing_site()
    parser.save_json()

parser = Parser()
import random

while True:
    parse()
    if random.randint(1, 5) == 5:
        parser.driver.refresh()
        # del parser
        # parser = Parser()
