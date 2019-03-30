#!/usr/bin/env python3


import csv
import random
import sys


d=dict()

def creatDataDict(isAdn=True):
	d=dict()
	with open('data.csv') as f:
		for l in f:
			parts=str.strip(l).split(",");
			if isAdn:
				parts[0] = parts[0].replace("U", "T")
			d[parts[0]]=parts[1]
	return d


def ARN_TO_PRIMARY(file):

		d =creatDataDict()
		with open(file) as f:
			l =f.read()
			res=[[]]
			i=0
			j=0
			while i< len(l)-2:
				a=l[i]+l[i+1]+l[i+2]
				if(a in d):
					if(d[a]!='STOP'):
						res[j].append(d[a])
					else :
						j+=1
						if(i+3<len(l)-2):
							res.append([])	
				i+=3
		return res	

if __name__ == '__main__':

	# pass the name of the file you want ti convert to primary
		if(len(sys.argv)>1):
			print(ARN_TO_PRIMARY(sys.argv[1]))
		else :
			print("Non file given")
