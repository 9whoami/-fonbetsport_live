#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import settings
from grab import Grab
from lxml import etree
from commons import WebDriver

__author__ = "whoami"
__version__ = "0.0.0"
__date__ = "27.04.16 20:27"
__description__ = """"""


class Parser:
    tables_data_file = 'tables'
    site_dump_file = 'web.htm'

    target_url = 'https://live.fonbetsport.com/?locale=ru'

    xpath = './/table[@id="lineTable"]/tbody/tr'
    xpath2 = ".//table[@id='lineTable']/tbody/tr/td/div[1]"
    xpath3 = ".//table[@id='lineTable']/tbody/tr[@id={!r}]/td/div[1]"

    target_events = list()

    def __init__(self):
        # self.tables_data = self.load_tables_data()
        self.parser = etree.HTMLParser(encoding='utf-8')

        self.driver = WebDriver()
        self.driver.get(self.target_url)
        self.script_disable()
        self.show_details()

    def mark_for_load_tables(self, id):
        self.target_events.append(id)

    def load_site(self):
        self.dump_site()
        self.page = etree.parse(self.site_dump_file, parser=self.parser)

    @staticmethod
    def _get_segment(cnt, tr):
        td = tr.getchildren()[0]
        div = td.getchildren()[0].getchildren()[1]
        segment_id = tr.attrib['id'][len('segment'):]

        return dict(name=div.text, segment=int(segment_id), games=list())

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
        details_json = list()
        div = []

        for td in tr.getchildren():
            if str(td.attrib.get('class')) not in 'detailsTD':
                continue
            else:
                div = td.getchildren()[0]
                break

        for table in div.getchildren():
            # print(table.attrib['id'])
            table_json = dict()

            thead = table.getchildren()[0]
            tbody = table.getchildren()[1]

            headers = ['description', 'name']
            body_trs = tbody.getchildren()

            for i, tr in enumerate(reversed(thead)):
                for j, th in enumerate(tr):
                    if i == 1:
                        table_json[headers[i]] = th.text
                    else:
                        for body_tr in body_trs:
                            if not table_json.get(headers[i]):
                                table_json[headers[i]] = list()
                            body_td = body_tr.getchildren()[j]
                            table_json[headers[i]].append({th.text: body_td.text if i == 0 else ''})

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

        trs = self.page.xpath(self.xpath)

        for cnt, tr in enumerate(trs):
            tr_id = tr.attrib['id']

            if event_id.startswith('event') and not event_id.endswith('details'):
                if event_id not in tr_id:
                    event_div_id = 'eventName{}'.format(event_id[len('event'):])
                    self.send_onclick(event_div_id)
                    # self.driver.btn_click(xpath=self.xpath3.format(event_id), screen=False)
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
                self.driver.btn_click(xpath=self.xpath3.format(event_id), screen=False)
        print('OK')

    def show_details(self):
        print('Shoing tables')
        events = self.driver.get_elements_by_xpath(self.xpath2)
        for event in events:
            # self.driver.btn_click(event)
            event_id = self.driver.get_element_info(event, 'id')
            if event_id:
                self.send_onclick(event_id)
        print('OK')

    def dump_site(self):
        print('Dumping site')
        self.driver.take_screenshot()
        with open('web.htm', 'w') as f:
            f.write(self.driver.page_source)
        print('OK')

    def script_disable(self):
        print('Disabling scripts')
        self.driver.execute_script('client.lineUpdateBuff = client.lineUpdate;')
        self.driver.execute_script('client.lineUpdate = null;')
        print('OK')

    def script_enable(self):
        print('Enabling scripts')
        self.driver.execute_script('client.lineUpdate = client.lineUpdateBuff;')
        print('OK')

    def load_json(self):
        with open('json.txt', 'r') as f:
            return json.loads(f.read())

    def send_onclick(self, elem_id):
        # eventName5839025
        print('Attempting to open the table')
        try:
            self.driver.execute_script('document.getElementById({!r}).onclick()'.format(elem_id))
        except Exception:
            return
        finally:
            print('OK')

    def save_json(self):
        if settings.send_to_url:
            print('Sending json data to url')
            api_url = 'http://rustraf.com/fonbet.php'

            g = Grab(connect_timeout=120, timeout=60)
            try:
                g.go(api_url, post=dict(data=json.dumps(self.result_json, indent=1, ensure_ascii=0)))
            except Exception as e:
                print(e)
            finally:
                print('Sending complete')
                del g

        if settings.save_to_file:
            print('Save json to file')
            with open('json.txt', 'w') as f:
                f.write(str(self.result_json))
                json.dump(self.result_json, f, indent=1, ensure_ascii=0)
            print('json saved')

    @staticmethod
    def rm_html_tags(source):
        text = re.sub(r'\s+', ' ', re.sub(r'\<[^\>]*\>', '', source))
        return text

from time import sleep

parser = Parser()

while True:
    parser.script_enable()
    sleep(1)
    parser.script_disable()

    parser.load_site()
    parser.parsing_site()
    parser.save_json()
    exit()
