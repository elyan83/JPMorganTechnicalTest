# PyAlgoTrade
#
# Copyright 2011-2015 Gabriel Martin Becedillas Ruiz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
"""

import csv


# A faster (but limited) version of csv.DictReader
class FastDictReader(object):
    def __init__(self, f, fieldnames=None, dialect="excel", *args, **kwargs):
        self.__fieldNames = fieldnames
        self.reader = csv.reader(f, dialect, *args, **kwargs)
        self.__fieldNames = next(self.reader)
        
        if self.__fieldNames is None:
            self.__fieldNames = next(self.reader)
         
        self.__dict = {}

    def __iter__(self):
        return self

    def __next__(self):
        # Skip empty rows.
        row = next(self.reader)
        while row == []:
            row = next(self.reader)

        # Check that the row has the right number of columns.
        assert(len(self.__fieldNames) == len(row))

        # Copy the row values into the dict.
        for i in range(len(self.__fieldNames)):
            self.__dict[self.__fieldNames[i]] = row[i]

        return self.__dict
