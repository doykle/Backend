

##
# Analysis.py
#
# Author: Vincent Steffens, vsteffen@ucsc.edu
# Date:   16 November 2014
#
# Produces a mean power spectrum of raw SEAD plug current 
# data, normalized by total current.
# Outputs to spectrum in a numpy array to stdout or a text 
# file, each array element on a line.
##  

##
# Modifications 
# Name: Kevin Doyle, kdoyle@ucsc.edu
# 
# Date: 18 November 2014
# Added -I option to support output of power spectrum data
#  for chunks of time, as decided by the variable 'blockwidth'
# Output goes to file: [input filename]_is.csv
#
# Date: 19 November 2014
# Added -C option
#  -C processes the input file and classifies it using a
#  a static classification routine. This classification was
#  generated in Weka. 
# Output: 
##

#For numerical analysis                                                 
import numpy as np                                                            
import math
                                                                       
#For visualization                                                      
import matplotlib.pyplot as pyp                                         
                                                                        
#For manipulating command-line arguments                                
import sys                                                              
                                                                        
#For handling files                                                      
import os 
                                                              
#For using regular expressions                                          
import re                                                               
                                                                        
def init():
   #Check for proper number of arguments, die if necessary
   #max args = 2 + number of valid options
   max_args = 9
   if len(sys.argv) < 2:
      print "Usage: <program name> [-fhIpvVw] [input file]"
      print "Call with -h for help"
      sys.exit(-1)
   if len(sys.argv) > max_args:
      print "Usage: <program name> [option] [input file]"
      print "Call with -h for help"
      sys.exit(-2)

   #handle calling with only Analysis.py -h
   if sys.argv[1] == '-h':
      print_help()
      exit()

   #Check for options. Break the option area of argv into a list of 
   #characters. Make a list of those that are valid, and a list of 
   #those that aren't. Let the user know if they endered an invalid 
   #option.
   valid_options = 'CdfhIpvVw'
   alleged_options = list(set(''.join(sys.argv[1:-1])))
   options = [x for x in alleged_options if re.search(x, valid_options)]
   non_options = [x for x in alleged_options if x not in options and x != '-']

   for i in non_options:
      print "Ignoring invalid option: \'%s\'" % (i)

   return options

#consider making times and currents an associative array
def import_and_trim():
   Currents = []
   Times = []
   
   amp_ids = [70, 66, 74, 62, 78, 58, 50, 14, 54]

   flag = 0   
   #Try to open source file for reading                                    
   filename = sys.argv[len(sys.argv) - 1]                                  
   if os.path.isfile(filename):                                                 
      with open(filename) as f:
         #discard first line
         f.readline()
         for line in f:
            line = line.strip().split(',')
            if int(line[0]) in amp_ids:
               Currents.append(line[1])
               Times.append(line[2])
   else:                                                                   
      print "Analysis: cannot open file: ", filename                    
      sys.exit(-4)  

   #Convert time since Unix epoch to intervals in microseconds             
   #Convert currents to milliamps                                          
   Times = [ int(x) - int(Times[0]) for x in Times ]                       
   Currents = [ 27*float(x)/1000 for x in Currents ] 
   
   return Currents, Times

def produce_blocklist():
   blocklist = []

   data_length = len(Currents) #or Times, just to de-specify
   i = 0
   if 'f' in Options:
      while i < data_length:
         block = []

         j = i
         while j < data_length: 
            if j + 1 < data_length and Times[j + 1] - Times[j] < 418:
               block.append(Currents[j])
            else: 
               break
            j += 1

         blocklist.append(block)
         i = j + 1
   else:
      while i < data_length:
         if i + 200 > len(Currents):                                       
            break   
         blocklist.append(Currents[i:i+blockwidth])                        
         i += blockwidth 

   return blocklist


def produce_mean_normalized_power_spectrum(blocklist):
   #question: mean then normalize, or normalized then mean?
   #doesn't matter because multiplication commutes

   #units are in square amps
   #here's why:
   #original was in amps
   #take ft (not fft)
   #break up original into frequency components
   #view from frequency perspective
   #frequency components are in amps
   #take mod square using absolute
   #mod square(a + bi) = a^2 + b^2
   #units are now in square amps per hz
   #integrate it in piecese from a to a + blockwidth
   #now you have units of amps sqared
   #put those in an array
   #oh yeah
   #so now we have a power spectrum for an amp signal (odd sounding)
   #in amps squared

   #Produce power spectrum, sum                                 
   scale_factor = float(1)/len(blocklist) 
   power_spectrum = np.square(np.absolute(np.fft.rfft(blocklist[0])))
   sum_power_spectrum = power_spectrum
   for i in xrange(1, len(blocklist)):
      power_spectrum = np.square(np.absolute(np.fft.rfft(blocklist[i])))
      ## Added by Kevin Doyle
      #  Prints the power spectrum from each individual time block
      minor_sum = float(0.0)
      new_spec = []
      if 'I' in Options or 'C' in Options:
         for val in power_spectrum:
            minor_sum += float(val)
         for val in power_spectrum:
            new_spec.append(float(val)/float(minor_sum))
         individual_spectrum_array.append(new_spec)
      ##
      sum_power_spectrum = np.add(sum_power_spectrum, power_spectrum)

   #Take integral
   total_sq_amps = 0.0
   for i in xrange(0, len(sum_power_spectrum)):
      total_sq_amps += sum_power_spectrum[i]

   #Normalize by total amps measured
   normalized_power_spectrum = sum_power_spectrum * (1/total_sq_amps)

   #Finish taking mean
   mean_normalized_spectrum = scale_factor * normalized_power_spectrum

   return mean_normalized_spectrum

def display(spectrum):
   template = np.ones(len(spectrum))
   mean_value = np.mean(spectrum)
   std_dist = np.std(spectrum)

   #Get the plot ready and label the axes
   pyp.plot(spectrum)
   max_range = int(math.ceil(np.amax(spectrum) / std_dist))
   for i in xrange(0, max_range):
      pyp.plot(template * (mean_value + i * std_dist))
   pyp.xlabel('Units?')
   pyp.ylabel('Amps Squared')    
   pyp.title('Mean Normalized Power Spectrum')
   if 'V' in Options:
      pyp.show()
   if 'v' in Options:
      tokens = sys.argv[-1].split('.')
      filename = tokens[0] + ".png"
      input = ''
      if os.path.isfile(filename):
         input = raw_input("Error: Plot file already exists! Overwrite? (y/n)\n")
         while input != 'y' and input != 'n':
            input = raw_input("Please enter either \'y\' or \'n\'.\n")
         if input == 'y':
            pyp.savefig(filename) 
         else:
            print "Plot not written."
      else:
         pyp.savefig(filename)
         
## Added by Kevin Doyle   
#  With option -C, this will output classification information    
def J48_classify():
   # These are the supported categories
   classify = {'television':0, 'microwave':0, 'computer':0}
   
   # Decision tree, as defined in Weka
   for array in individual_spectrum_array:
      if array[93] <= 0.000065:
         classify['microwave'] = classify['microwave'] + 1
      else:
         if array[6] <= 0.060487:
            if array[28] <= 0.031599:
               if array[83] <= 0.000789:
                  classify['television'] = classify['television'] + 1
               else:
                  if array[34] <= 0.000657:
                     classify['television'] = classify['television'] + 1
                  else:
                     if array[60] <= 0.004051:
                        if array[30] <= 0.005159:
                           if array[19] <= 0.003401:
                              classify['computer'] = classify['computer'] + 1
                           else:
                              classify['television'] = classify['television'] + 1
                        else:
                           classify['computer'] = classify['computer'] + 1
                     else:
                        classify['computer'] = classify['computer'] + 1
            else:
               classify['television'] = classify['television'] + 1
         else:
            classify['computer'] = classify['computer'] + 1
   
   # Flag -d will print the dictionary
   if 'd' in Options:
      print classify
   
   # Selects the classification with largest number of tallies
   # alt_str is used for output, when classification is not definitive
   decision_val = 0
   total_val = 0
   decision_str = ''
   alt_str = ''
   for device, val in classify.iteritems():
      total_val = total_val + val
      if val > decision_val:
         alt_str = decision_str
         decision_val = val
         decision_str = device
   
   # Print out classification, or possible classifications
   # Note: 19-11-2014 The percent accuracy for classification is hard coded below.
   if (float(decision_val)/total_val) > 0.7:
      print "With {1}% confidence, this is a {0}.\n".format(decision_str, (decision_val*100/total_val))
   else:
      print "Could not classify device. It might be a {0}".format(decision_str),
      if len(alt_str) > 1:
         print "or it could be a {0}.\n".format(alt_str)
      else:
         print "or it could be a {0}.\n".format("platypus")

##
   
   
def write_output():
   tokens = sys.argv[-1].split('.')
   filename = tokens[0] + ".txt"
   if os.path.isfile(filename):
      input = raw_input("Error: Output file already exists! Overwrite? (y/n)\n")
      while input != 'y' and input != 'n':
         input = raw_input("Please enter either \'y\' or \'n\'.\n")
      if input == 'n':
         print "Output not written."
      elif input == 'y':
         output(filename)
   else:
      output(filename)

## Modification by Kevin Doyle
#  19-11-2014      
def output(filename):
   out = open(filename, 'w')
   for element in Spectrum:
      out.write(str(element) + "\n")
   out.close()

## Added by Kevin Doyle
#  based on Vincent's code from write_output()
#  Outputs individual power spectrum data to CSV file
#  filename format: [input file]_is.csv
def write_indv_spectrum():

   # Collects file name from input
   tokens = sys.argv[-1].split('.')
   filename = tokens[0] + "_is.csv"
   
   # Check to see if the file exists, verify overwrite
   if os.path.isfile(filename):
      input = raw_input("Error: Output file already exists! Overwrite? (y/n)\n")
      while input != 'y' and input != 'n':
         input = raw_input("Please enter either \'y\' or \'n\'.\n")
      if input == 'n':
         print "Individual spectrum output not written."
      elif input == 'y':
         output_is(filename)
   else:
      output_is(filename)
##

## Added by Kevin Doyle
def output_is(filename):
   idx_stop = (len(individual_spectrum_array[0]) - 1)
   out = open(filename, 'w')
   for array in individual_spectrum_array:
      for idx, value in enumerate(array):
         out.write("{0}".format(float(value)))
         if idx != idx_stop:
            out.write(",")
         #else:
         #   out.write(",computer")
      out.write("\n")
   out.close()
##
      
def print_help():
   print "\nAnalysis.py."
   print "Used to produce a mean power spectrum of raw SEAD plug current data, normalized by total current"
   print "\nCall using this syntax:"
   print "$ python Analysis.py [-fhpvVw] [input file]"
   print ""
   print "Input: Raw, 4-column SEAD plug data"
   print "Output: Either or both of:"
   print "1. Numpy array printed to stdout."
   print "2. Spectrum written to text file."
   print "\nOptions may be arranged in any order, and in any number of groups"
   print "-C:\t Classify device data using J48 Decision Tree."
   print "-f:\t Fragmented data. This handles gaps in the data."
   print "-h:\t Help. Display this message."
   print "-I:\t Output individual spectrum data."
   print "-p:\t Print. Print numpy array containing spectrum to terminal."
   print "-V:\t View. Display plot of spectrum, with the mean and multiples of the standard deviation."
   print "-v:\t Visualize. Print plot to file."
   print "-w:\t Write. Write spectrum to file, each array element on its own line"

   print "\nExamples:"
   print "1: Handle fragmented data, view plot, write spectrum to file"
   print "   python Analysis.py -vfw 1_raw.csv"
   print "   python Analysis.py -f -wv 1_raw.csv"
   print "2: View plot of spectrum"
   print "   python Analysis.py -V 1_raw.csv"


#Execution begins here

if __name__ == '__main__':

   blockwidth = 200
   Currents = []
   Times = []
   ## Added by Kevin Doyle
   individual_spectrum_array = []
   ##

   Options = init()
   Currents, Times = import_and_trim()
   Blocklist = produce_blocklist()
   Spectrum = produce_mean_normalized_power_spectrum(Blocklist)
   if 'h' in Options:
      print_help()
   if 'p' in Options:
      print Spectrum
   if 'w' in Options:
      write_output()
   if 'v' in Options or 'V' in Options:
      display(Spectrum)
   ## Added by Kevin Doyle
   if 'I' in Options and not 'C' in Options:
      write_indv_spectrum()
   if 'C' in Options:
      J48_classify()
   ##