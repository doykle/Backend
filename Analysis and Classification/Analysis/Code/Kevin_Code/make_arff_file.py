#make_arff_file.py


def output( file_lines ):
   output_dir = "output_folder/"
   output_file = "data_file.arff"
   
   if not os.path.exists( output_dir ):
      os.makedirs( output_dir )
   
   template_lines = open( "template.arff", 'r' ).readlines()
   
   out = open( os.path.join( output_dir, output_file ), 'w' )
   
   for line in template_lines:
      out.write( line )
   
   for lines in file_lines:
      for line in lines:
         out.write( line )
      
   out.close()
   

def process_file( file_dir ):
   
   if file_dir.endswith('.csv'):   
      file_lines = open( file_dir, 'r' ).readlines()
      lines.append( file_lines )
      
   else:
      pass
   
   

if __name__ == '__main__':
   import os
   import sys
   
   # make_arff_file.py [input directory]
   dir = sys.argv[1]

   lines = []
   
   for subdir, dirs, files in os.walk( dir ):
      for file in files:
         process_file( os.path.join( subdir, file ) )
         
   if len( lines ) > 0:
      output( lines )