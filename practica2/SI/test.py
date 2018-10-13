import os
from random import randint


lista = os.listdir(str(os.getcwd())+"/usuarios")
print lista
if "maria.bh" in lista:
	print "bien"

path = str(os.getcwd())+"/usuarios/lacasito"
os.mkdir(path)

f=open(path+"/datos.txt","w")
f.write("nombre =\n")
f.write("password =\n")
f.write("email =\n")
f.write("tarjeta =\n")
saldo = randint(0,100)
f.write("saldo = "+ str(saldo) +"\n")
