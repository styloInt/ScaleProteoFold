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
			res=[[]]
			i=0
			a=l[:3]
			j=0
			while(i<len(l)-2):
				while(a in d and d[a]!='M'):
					i+=3
					a=l[i:i+3]
				while i< len(l)-2 and a in d and  d[a]!='_':
					res[j].append(d[a])
					a=l[i:i+3]
					i+=3
				if(a not in d):
					print("ERR: séquence non connu :",a)
					return ""
				else :
					if(i>len(l)-2):
						res.append([])
						j+=1

					
			return res	


if __name__ == '__main__':

	# pass the name of the file you want ti convert to primary
		if(len(sys.argv)>1):

			l=ARN_TO_PRIMARY(sys.argv[1])
			for l1 in l :
				print("".join(l1))
		else :
			print("Non file given")
