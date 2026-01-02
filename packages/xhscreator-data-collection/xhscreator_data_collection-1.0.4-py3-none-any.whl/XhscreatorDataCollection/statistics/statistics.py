"""
Copyright (c) now Martian Bugs All rights reserved.
Build Date: 2025-12-29
Author: Martian Bugs
Description: 统计分析模块
"""

from collections.abc import Callable
from functools import partial
from time import sleep

from BrowserAutomationLauncher import Browser, DataPacketProcessor
from BrowserAutomationLauncher._utils.tools import DictUtils
from DrissionPage._pages.mix_tab import MixTab

from ._dict import StatisticsDict


class Urls:
    content_analysis = 'https://creator.xiaohongshu.com/statistics/data-analysis'


class DataPacketUrls:
    note_list = 'https://creator.xiaohongshu.com/api/galaxy/creator/datacenter/note/analyze/list'


class Statistics:
    def __init__(self, browser: Browser):
        self._browser = browser

    def __wait__content_analysis_datapacket(self, page: MixTab, func: Callable):
        """等待内容分析数据包"""

        page.listen.start(
            targets=DataPacketUrls.note_list, method='GET', res_type='XHR'
        )
        func()
        datapacket = page.listen.wait(timeout=20)
        if not datapacket:
            raise TimeoutError('等待内容分析数据包超时')

        datapacket_data = DataPacketProcessor(datapacket).filter(
            ['data.note_infos', 'success', 'msg']
        )
        if 'success' not in datapacket_data:
            raise RuntimeError(datapacket_data.get('msg'))

        note_infos: list[dict] = datapacket_data.get('note_infos')

        return note_infos

    def get__content_analysis(self, new_tab=False):
        """
        获取内容分析数据

        Args:
            new_tab: 是否在新标签页中操作, 如果是则会在操作完成后自动关闭页面
        """

        page = (
            self._browser.chromium.new_tab()
            if new_tab is True
            else self._browser.chromium.latest_tab
        )

        note_infos = self.__wait__content_analysis_datapacket(
            page, lambda: page.get(Urls.content_analysis)
        )
        if not note_infos:
            return

        all_note: list[dict] = [*note_infos]
        sleep(1)
        while True:
            next_page_btn = page.ele('c:.d-pagination-page:last-of-type', timeout=3)
            if not next_page_btn or 'disabled' in next_page_btn.attr('class'):
                break

            func = partial(next_page_btn.click, by_js=True)
            note_infos = self.__wait__content_analysis_datapacket(page, func)
            if not note_infos:
                break
            all_note.extend(note_infos)
            sleep(1)

            if len(note_infos) < 10:
                break

        all_note = [
            DictUtils.dict_mapping(note, StatisticsDict.content_analysis__detail)
            for note in all_note
        ]
        return all_note
