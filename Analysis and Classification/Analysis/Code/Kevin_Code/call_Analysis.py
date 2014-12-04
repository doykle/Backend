
import os


if __name__ == '__main__':
   
      dir = './'
      
      for subdir, dirs, files in os.walk( dir ):
         for file in files:
            if file.endswith('.csv'):
               os.system("Analysis.py -w " + file )