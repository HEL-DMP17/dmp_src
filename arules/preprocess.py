# Global modules
import collections
import math

# Internal modules
from utils import *

"""
This will be PREPROCESSOR class, TODO: add some docs
"""


class PreProcessor:
    def __init__(self):
        self.transactions = []
        self.unique = collections.OrderedDict()
        self.trans_count = 0
        self.mapper = PreProcessor.Mapper()
        # Parse the file
        # self.parse_file(file)
        # print(self.transactions)
        # self._print_transactions()
        # print(self.unique)

    def get_transactions(self):
        """
        Getter method for transactions list of OrderedDict
        :return: Transactions list
        """
        return self.transactions

    def get_uniques(self):
        """
        Getter method for unique itemsets (dictionary)
        :return: Counts of unique itemsets
        """
        return self.unique

    def get_transaction_count(self):
        """
        Getter method for transaction count after parsing the file
        :return: Transaction count (int)
        """
        return self.trans_count

    def parse_file(self, file):
        """
        File reader for student-level dataset
        :param file: Filepath for dataset
        :return:
        """
        mp = self.mapper

        with open(file, "r") as f:
            for line in f:
                chars = str(line)
                # Get all the necessary fields here
                sex = self.get_field(chars, mp.sex)
                race = self.get_field(chars, mp.race)
                score = self.get_field(chars, mp.score)
                # Add this into transaction. Put all the fields into the list
                fields = [sex, race, score]
                self.add_transaction(fields)
        # Return number of transactions added
        return self.trans_count

    def get_field(self, line, mapper):
        value = line[mapper['STR'] - 1: mapper['END']]
        # Check the type and execute either discretize/binarize etc.
        if mapper['TYPE'] == 'BINARY':
            return self._is_name(mapper['COL'], mapper['VALS'][int(value)])
        elif mapper['TYPE'] == 'CATEGORICAL':
            return self.binarize(mapper, int(value))  # Change here later for OTHER field
        else:
            return self.discretize(mapper, float(value))

    def add_transaction(self, fields):
        self.trans_count += 1
        items = collections.OrderedDict()
        # Add the fields here, True is only used to have
        # OrderedSet kind of data structure
        items = collections.OrderedDict({f: True for f in fields})  # more pythonic way to populate
        self.count_unique(fields)  # Updates unique dict
        # Use keys to sort the dict
        items = collections.OrderedDict(sorted(items.items(), key=lambda _: _[0]))
        t = {'ID': self.trans_count, 'ITEMS': items}
        self.transactions.append(t)

    def count_unique(self, fields):
        """
        Used to increment the unique fields
        :param fields: List of fields(str). sex, gender, score ..
        :return: Increments self.unique dictionary
        """
        for f in fields:
            if f not in self.unique:
                self.unique[f] = 1
            else:
                self.unique[f] += 1
        self.unique = collections.OrderedDict(sorted(self.unique.items(), key=lambda _: _[0]))

    def discretize(self, mapper, col_data):
        """
        Used to discretize the continous values from the given mapper and value
        :param mapper: Mapper of the continious field  (Mapper Class)
        :param col_data: Value of the continous field (float)
        :return: Returns discretized name of the field (string)
        """
        max = math.ceil(mapper['MAX'])
        min = math.floor(mapper['MIN'])
        interval = mapper['INTERVAL']
        step = (max - min) / interval
        # Initial check to decide in which range it belongs to
        lower = float(format(min, '.2f'))
        upper = float(format(lower + step, '.2f'))
        if col_data > lower and col_data < upper:
            str_interval = '[' + str(int(lower)) + '-' + str(int(upper)) + ']'
            # print('Lower : ' + str(lower) + ' Upper : ' + str(upper)
            #       + ' Value : ' + str(col_data) + ' Interval : ' + str_interval)
            return self._is_name(mapper['COL'], str_interval)

        # Check the boundries until the end of the interval value
        for i in range(1, interval):
            lower = float(format(upper, '.2f'))
            upper = float(format(upper + step, '.2f'))
            if col_data > lower and col_data < upper:
                str_interval = '[' + str(int(lower)) + '-' + str(int(upper)) + ']'
                # print('Lower : ' + str(lower) + ' Upper : ' + str(upper)
                #       + ' Value : ' + str(col_data) + ' Interval : ' + str_interval)
                return self._is_name(mapper['COL'], str_interval)

        raise ValueError('Value is not between the intervals check preprocessor::discretize')

    def binarize(self, mapper, col_data):
        """
        Binarize the attribute data using mapper
        :param col_data: Categorical data assumed to be between -9 and 25
        :param mapper: Corresponding mapper of this field
        :return: Binarized field - str
        """
        if mapper is None:
            print("Give an appropriate mapper")
            return

        if col_data < -9:
            raise ValueError('Values cannot be less than -9 - check binarize method in preprocess.py')

        # Change this, in case if we break something
        max_categorical_value = 25
        if col_data > max_categorical_value:
            raise ValueError('Values cannot be more than 25 - check binarize method in preprocess.py')

        # Return proper COL_IS_ATTR name
        if col_data in mapper['VALS'].keys():
            if mapper['OTHERS'] is not None:
                if col_data in mapper['OTHERS']:
                    # Others
                    nm = self._is_name(col=mapper['COL'], attr="OTHERS")
                elif col_data in mapper['VALS']:
                    # Map as standalone field
                    nm = self._is_name(col=mapper['COL'], attr=mapper['VALS'][col_data])
                else:
                    raise Exception("Something unusual in preprocessor::binarize happened")
            else:
                # Map as standalone field
                nm = self._is_name(col=mapper['COL'], attr=mapper['VALS'][col_data])

            # Return the name
            return nm
        else:
            raise ValueError('This key is not inside our mapper VALS - check binarize method in preprocess.py')

    def save_transactions(self, path):
        """
        Save the preprocessed transactions into a file
        :param path: Path to be saved
        :return: Returns true on successful save
        """
        print('Saving the transactions into {}'.format(path))
        return True

    def _print_transactions(self):
        """
        Used to print transactions in pretty format
        :return:
        """
        # TODO: fix printing using formatted print
        print_str = "ID   ITEMS\n"
        for t in self.transactions:
            print_str += str(" " + str(t['ID']) + " |")
            for i in t['ITEMS'].keys():
                print_str += " " + i + " "

            print_str += " \n"
        print(print_str)
        """
        | ID |              ITEMS              |
        | 1 | SEX_IS_MALE, RACE_IS_BLACK ...   |
        | 2 | SEX_IS_MALE, RACE_IS_BLACK ...   |

        """

    # Added to construct transaction item names
    # There are some attiributes having 'MISSING_VALUE' types
    # So we cannot be sure if we only add the attr type
    # Better to combine with column name as well
    def _is_name(self, col, attr):
        return col.upper() + "_IS_" + attr.upper()

    # Until getting nice representation using files(possibly JSON) use this structure
    # later we can create the file structure and parser for that.
    class Mapper:
        def __init__(self):
            # Some fields can change
            # TODO: Add 'OTHERS' field that will have fields we want to combine
            self.sex = {'COL': 'SEX', 'TYPE': 'BINARY', 'STR': 24, 'END': 25,
                        'OTHERS': None,
                        'VALS': {1: 'MALE', 2: 'FEMALE'}}

            # Combine fields that are in others together
            self.race = {'COL': 'RACE', 'TYPE': 'CATEGORICAL', 'STR': 26, 'END': 27,
                         'OTHERS': {4: 'HISP_NR', 5: 'HISP_RC', 3: 'BLACK'},
                         'VALS': {1: 'AMER', 2: 'ASIA', 3: 'BLACK',
                                  4: 'HISP_NR', 5: 'HISP_RC', 6: 'MULT',
                                  7: 'WHITE'}}

            # self.race_others = {'COL': 'RACE', 'TYPE': 'CATEGORICAL', 'STR': 26, 'END': 27,
            #              'OTHERS': None,
            #              'VALS': {1: 'AMER', 2: 'ASIA', 3: 'BLACK',
            #                      4: 'HISP_NR', 5: 'HISP_RC', 6: 'MULT',
            #                      7: 'WHITE'}}

            # SCORE_IS-20_60 , 35.12
            self.score = {'COL': 'SCORE', 'TYPE': 'CONTINIOUS', 'STR': 106, 'END': 111,
                          'MIN': 20.91, 'MAX': 81.04, 'INTERVAL': 5}
