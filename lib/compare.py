#!/usr/bin/env python
import csv
import re
import pprint
import os.path

class Compare:  
  def __init__(self, source, comparator, subset):
    self.subset = subset
    self.source_name = source
    self.source_file = csv.DictReader(open(os.path.dirname(__file__) + "/../csv-input/" + source))

    self.comparator = comparator
    self.comparator_file = csv.DictReader(open(os.path.dirname(__file__) + "/../csv-input/" + comparator))

    self.source_order_numbers = []
    self.source_dupes = []
    self.source_dict = {}

    self.comparator_order_numbers = []
    self.comparator_dupes = []
    self.comparator_dict = {}

    self.diff = []

  def setup(self):
    self.source_to_dict()
    self.comparator_to_dict()
    if self.subset is 'exclude':
      self.find_diff_exclude()
    elif self.subset is 'include':
      self.find_diff_include()
    self.print_results()
    return

  def source_to_dict(self):
    for row in self.source_file:
      order_key = str(row['order_number'])

      #report possible duplicates
      if self.source_dict.has_key(order_key):
        self.source_dupes.append(order_key)

      # Create Hash of Keys and Rows
      self.source_dict[order_key] = row

      # Create list of order numbers
      self.source_order_numbers.append(order_key)
    return

  def comparator_to_dict(self):
    regex = r"\bMoment-\b"
    
    for row in self.comparator_file:
      ref_key = str(row["Reference"]).strip().replace(" ", "")
      ref_key = re.sub(regex, "", ref_key)

      #report possible duplicates
      if self.comparator_dict.has_key(ref_key):
        self.comparator_dupes.append(ref_key)

      # Create Hash of Keys and Rows
      self.comparator_dict[ref_key] = row

      # Create list of ref numbers
      self.comparator_order_numbers.append(ref_key)
    
    return

  def find_diff_exclude(self):
    for source_key in self.source_order_numbers:
      is_match = self.comparator_dict.get(source_key)
      # if it's not a match that means a key exists in the source that doesn't exist in the comparator
      if is_match is None:
        self.diff.append(self.source_dict.get(source_key))
    return

  def find_diff_include(self):
    for source_key in self.source_order_numbers:
      is_match = self.comparator_dict.get(source_key)
      if is_match is not None and type(is_match) is dict:
        self.diff.append(self.source_dict.get(source_key))
    return

  def write_to_csv(self):
    if len(self.diff) > 0:
      keys = self.diff[0].keys()
      with open(os.path.dirname(__file__) + '/../csv-output/' + self.subset + '-' +self.source_name, 'wb') as output_file:
          dict_writer = csv.DictWriter(output_file, keys)
          dict_writer.writeheader()
          dict_writer.writerows(self.diff)
          print 'csv generated'
    else:
      print "No results to write to csv"
    return

  def print_results(self):
    print "========== Source Data =========="
    print "Source to dict: " + str(len(self.source_dict.keys()))
    print "Source order numbers: " + str(len(self.source_order_numbers))

    print "========== Comparator Data =========="
    print "Comparator to dict: " + str(len(self.comparator_dict.keys()))
    print "Comparator order numbers: " + str(len(self.comparator_order_numbers))

    print "========== Possible Duplicates =========="
    print "Possible Dupes in source: " + str(list(set(self.source_dupes)))
    print "Possible Dupes in comparator: " + str(list(set(self.comparator_dupes)))

    print "========== Summary =========="
    print "Diff (" + self.subset + ") " + str(len(self.diff))