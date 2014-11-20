Author: Kevin Doyle
Date: 20 November 2014

Folders:

   copied_data/
      This file is a copy from Vincent's_Code/data/

   labeled_data/
      Contains data files which contain power spectrums, output from
      Analysis.py. Each row is ended with a label, identifying the 
      type of device which created the spectrum. These files can be 
      used to assemble an .arff file, for use with Weka
      
      normalized/
         Where I put the files I wish to assemble into an .arff file.
   
   output_folder/
      This is the hard coded output folder for make_arff_file.py
      
Files:
   
   Analysis.py
      Read the comments in the code for more information. This is a  
      modified version of Vincent's Analysis.py. I have added -I, which
      takes a seadplug csv data file and outputs power spectrum data.
      I also added -C which is a hard coded classification tree, as 
      defined by Weka using J48 and the .arff file in /output_folder
      To use new data, you will need to manually change the selection
      of labels in J48_classify(), but I imagine you'll notice that 
      while re-writing the classification tree.
      
   labeler.py
      Not of much use, this adds labels to the end of the power
      spectrum files output by Analysis.py -I  Instead of using
      this file, I have opted to add the labels by editing Analysis.py
      when making the spectrum files. Look for commented code in 
      output_is() if you would like to see how this is done.
      
   make_arff_file.py
      This assembles the labelled spectrum data files from a directory 
      into an .arff file for use with Weka. It calls upon the template.arff 
      in order to get this done, so make sure template.arff is in the same
      directory. You will need to manually change the selection of labels.
      
   make_classifier.py
      is empty. 
      
   template.arff
      This is a template used by make_arff_file.py to put together an .arff file.