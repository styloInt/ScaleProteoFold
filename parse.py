#!/usr/bin/env python3
import csv
import random
import sys


d=dict()
isAdn = True

def convertRmnaToDna(seq):
	seq = seq.replace("T", "U")
	return seq

def ConvertToProt():
	d=dict()
	with open('data.csv') as f:
		for l in f:
			parts=str.strip(l).split(",");
			d[parts[0]]=parts[1]
	return d

def convertToAA(d):
	d1=dict()
	with open('ProtToA.csv') as f:
		for l in f:
			parts=str.strip(l).split(",")
			d1[parts[0]]=parts[1]
	
	res=dict()
	for c,p in d.items():
		if(p in d1):
			res[c]=d1[p]
	return res

def ARN_TO_PRIMARY(file):
		d0=ConvertToProt()
		d=convertToAA(d0) 
		with open(file) as f:
			l = str.strip(f.read())
			if isAdn:
				l = convertRmnaToDna(l)
			res=[]
			i=0
			a=l[:3]
			if(d[a]!='M'):
				print("ERR : entrée")
				return ""
			else :
				while i< len(l)-2:
					a=l[i:i+2]
					if(a in d):
						if(d[a]!='_'):
							res.append(d[a])
						else :
							break
					else :
						print("ERR")
					i+=3
			return res	


if __name__ == '__main__':

	# pass the name of the file you want ti convert to primary
		if(len(sys.argv)>1):
			print("".join(ARN_TO_PRIMARY(sys.argv[1])))
		else :
			print("Non file given")
