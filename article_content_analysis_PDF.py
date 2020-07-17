import tikapp
from tikapp import TikaApp
from collections import Counter
from string import punctuation
import pandas as pd
import csv
import string
import itertools
import unicodedata


#Set variables to file names/locations
pdf_csv = 'pdfnames.csv' # csv file containing the names of each pdf file to be analysed
keyword_csv = 'keywords.csv' # keywords to search for
tika_file_jar = 'C:/tika/tika-app-1.21.jar' #tika app jar location
outfile_name = 'outfile.csv'

def analyse_pdf_archive(pdf_csv, keyword_csv, tika_file_jar, outfile_name):
	# PDF for each day saved as welt_mmdd. File names listed in csv file 'welt_pdf'. Create list of PDF names. 
	with open(pdf_csv, 'r', encoding = 'utf-8-sig') as f:
		reader = csv.reader(f)
		pdf_names = list(reader)
	pdf_names = list(itertools.chain(*pdf_names)) # acts as main data frame to contain individual data frames

	pdf_list = []
	for name in pdf_names:
		pdf_list.append(name + '.pdf')

	# Create list of keywords from 'keyword_stems.csv'
	with open(keyword_csv, 'r', encoding = 'utf-8-sig') as f:
		reader = csv.reader(f)
		keywords = list(reader)
	keywords = list(itertools.chain(*keywords))

	tika_client = TikaApp(file_jar=tika_file_jar)

	a = 1 #set counter to 1

	keyword_counter = []
	for pdf in pdf_list:
		rawText = tika_client.extract_only_content(pdf)
		print("pdf {0} extracted".format(a))
		rawList = rawText.split( )
		
		rawList_nopunct = [word.translate(str.maketrans('', '', string.punctuation)) for word in rawList]
		counts = Counter(rawList_nopunct)
		list_words = counts.most_common()

		keyword_hits_list = []
		for x in range(0, len(list_words)):
			temp = list(list_words[x]) # convert from tuple to list
			temp[1] = str(temp[1]) # change number (at index 1) into string
			n_temp = [(unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore')).lower().decode() for word in temp] #normalised umlauts in data
			
			#check word (at index 0) against list of keywords, add new column = 1 if match, = 0 otherwise.
			hits = 0 
			for i in range(0, len(keywords)):
				if keywords[i] in n_temp[0]:
					hits = hits + 1
			if hits != 0:
				n_temp.append(1)
			else:
				n_temp.append(0)

			keyword_hits = int(n_temp[1])*int(n_temp[2])
			keyword_hits_list.append(keyword_hits)
		
		keyword_counts = sum(keyword_hits_list)
		keyword_counter.append(keyword_counts)

		print("day {0} complete".format(a))

		if list_words != []:
			a = a + 1
		else:
			break
	
	df = pd.DataFrame({"id": pdf_names, "keywords": keyword_counter})
	df.to_csv(outfile_name, index=False)

	
analyse_pdf_archive(pdf_csv, keyword_csv, tika_file_jar, outfile_name)

