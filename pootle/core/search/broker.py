#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) Pootle contributors.
#
# This file is a part of the Pootle project. It is distributed under the GPL3
# or later license. See the LICENSE file for a copy of the license and the
# AUTHORS file for copyright and authorship information.

from . import SearchBackend

import importlib

from django.conf import settings


class SearchBroker(SearchBackend):
    def __init__(self, config_name=[]):
        self._setup_settings()
        self._servers = {}
        if self._settings is None:
            return
        for server in self._settings:
            if config_name == [] or server in config_name:
                _module = ('.').join(self._settings[server]['ENGINE'].split('.')[:-1])
                _search_class = self._settings[server]['ENGINE'].split('.')[-1]
                module = importlib.import_module(_module)
                self._servers[server] = getattr(module, _search_class)(server)

    def search(self, unit):
        results = []
        counter = {}
        if not self._servers:
            return []
        for server in self._servers:
            for result in self._servers[server].search(unit):
                translation_pair = result['source'] + result['target']
                if translation_pair not in counter:
                    counter[translation_pair] = result['count']
                    results.append(result)
                else:
                    counter[translation_pair] += result['count']

        for item in results:
            item['count'] = counter[item['source']+item['target']]

        return results

    def update(self, language, obj):
        for server in self._servers:
            self._servers[server].update(language, obj)
