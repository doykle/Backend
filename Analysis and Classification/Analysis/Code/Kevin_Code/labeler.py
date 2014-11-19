file_name = "tv.csv"

file = open( file_name, 'r' ).readlines()

new_file = []

for line in file:
   
   #print "{0},{1}".format(line.strip(),"tv")
   new_file.append("{0},{1}".format(line.strip(),"tv\n"))
   
outfile = "tv_out.arff"

out = open( outfile, 'w')

for line in new_file:
   out.write(line)
   
out.close()