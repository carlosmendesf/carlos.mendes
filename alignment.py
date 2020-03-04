from math import sqrt
import numpy as np
import pandas as pd
from easygui import fileopenbox #responsável por importar arquivos excel

def generate_matrix(x,y,z):

	'''matriz de translacao e rotacao para pequenos angulos
	as variaveis de entrada sao as coordenadas cartesianas de um vetor 

	'''
	tr_matriz=[[1,0,0,0,z,-y],
		      [0,1,0,-z,0,x],
		      [0,0,1,y,-x,0]]
	#h=(1+x**2+y**2+z**2)
	#tr_matriz=[[1,0,0,(1+x**2-y**2-z**2)/h,(2*x*y-2*z)/h,(2*y+2*x*z)/h],
	#          [0,1,0,(2*x*y+2*z)/h,(1-x**2+y**2-z**2)/h,(2*y*z-2*x)/h],
	#          [0,0,1,(2*x*z-2*y)/h,(2*x+2*y*z)/h,(1-x**2-y**2+z**2)/h]] 

	return tr_matriz
	
def findvector(x,y,z,dx,dy,dz,rx,ry,rz):
	'''realiza a translacao e rotacao de um vetor qualquer
	x: coordenada eixo x
	y: coordenada eixo y
	z: coordenada eixo z
	dx: deslocamento no eixo x
	dy: deslocamento no eixo y
	dz: deslocamento no eixo z
	'''
	vect=[dx,dy,dz,rx,ry,rz]	

	tr_matriz=generate_matrix(x,y,z)
	n_vect=[0,0,0]

	for i in range(3):
		for j in range(6):
			n_vect[i]=n_vect[i]+tr_matriz[i][j]*vect[j] # vetor do ponto apos a translacao e rotacao

	return n_vect

def alignment1(n_apalpadores,dx,dy,dz,rx,ry,rz,*argv):
	'''Gera uma lista com os valores de deslocamento em metros dos apalpadores, ou atuadores, apos rotacao e translacao
	   alignment(n_apalpadores,*argv)
	   n_apalpadores: numero de apalpadores ou atuadores
	   *agv: lista 1x6, de coordenadas do vetor direcao do apalpador e posicao, respectivamente 
	   Exemplo:
	   alignment1(6,[1,0,0,0.5,0,0.1],[1,0,0,0.3,0.4,0.4],[0,1,0,0.2,0,0.05],[0,0,1,0.1,0.5,0.2],[0,1,0,0.6,0.02,0.3],[0,0,1,0.8,0.8,0.8])'''
	if (len(argv)==n_apalpadores):
		indice=0 #apenas para indicar os apalpadores
		desl_apalp=[0]*n_apalpadores #lista vazio para alocacao dos deslocamentos 
	
	
		for vet in argv:

			#fator de normalizacao do vetor do apalpador
			x=vet[3]
			y=vet[4]
			z=vet[5]
			n_vect=findvector(x,y,z,dx,dy,dz,rx,ry,rz)
			v_dir=[vet[0],vet[1],vet[2]]
			
			scale_factor=np.linalg.norm(v_dir)
			v_dir=v_dir/scale_factor

			#parte de calculo dos produtos escalares
			scalar_produt=np.dot(v_dir,n_vect)
			desl_apalp[indice]=scalar_produt
			indice=indice+1



		#print('deslocamento dos apalpadores l1,l2,l3...ln: \n')
		#print(desl_apalp)
		return desl_apalp	

	else:
		print('Numero de variaveis incorreta. As variaveis de entrada devem ser numero de apalpadores, vetores de 6 elementos (vetor direcao e posicao) de cada apalpador')
	


	

	return

def alignment2(l1,l2,l3,l4,l5,l6,*argv):
	''' Fornece as rotacoes em x,y,z e deslocamento em x,y,z. 
	As variaveis de entrada sao:
	l1,l2..l6: leitura dos apalpadores 1,2,3..,6, respectivamente.
	#argv= conjunto de 6 listas de dimensao 6, contendo os dados dos vetores direcao e posicao dos apalpadores 1,2,3...,6, respectivamente e em coordenadas cartesianas [m]. Para facilidade do programa, colocar os vetores iguais juntos.
	Exemplo:
	alignment2(1,2,3,4,5,6,[1,0,0,1,2,3],[1,0,0,5,3,1],[0,1,0,1,1,1],[0,1,0,0,12,3],[0,0,1,1,2,3],[0,0,1,1,3,3] )
	'''
	linear_solution=[]
	sensors=np.array([l1,l2,l3,l4,l5,l6])
	for vet in argv:
		Vect=[vet[0],vet[1],vet[2]]
		Vect=Vect/np.linalg.norm(Vect)
		matrix_trans_rot=generate_matrix(vet[3],vet[4],vet[5])
		linear_solution.append(np.dot(Vect,matrix_trans_rot))

	if np.linalg.det(linear_solution)==0:
		linear_solution=np.linalg.pinv(linear_solution)
		print('\nO sistema é indeterminado, desta forma sera considerada a matriz pseudo-inversa para solucao\n')
		variables=np.dot(linear_solution,sensors)
	else:	
		variables=np.linalg.solve(linear_solution,sensors)

	return variables


def main():
	'''O aplicativo de alinhamento deve ocorrer com a leitura de dos apalpadores e dos atuadores de maneira simultanea. desta forma, as duas funcoes de alinhamento estarao ocorrendo juntamente. 
	As entradas devem ser leitura dos atuadores e apalpadores, deslocamentos e rotacoes nos eixos x,y,z
	No código, os vetores dos apalpadores estao nomeados como "ap" e atuadores como "atu", ambos enumerados de 1 a 6.'''
	print('SISTEMA DE ALINHAMENTO, PARA SAIR DO PROGRAMA, DIGITE CTRL+C')
	filename=fileopenbox()
	if filename!=None and len(pd.read_excel(filename).index)==6:
		x=pd.read_excel(filename)

		try:
			while True:


				atu1=x.iloc[0,1:7]
				atu2=x.iloc[1,1:7]
				atu3=x.iloc[2,1:7]
				atu4=x.iloc[3,1:7]
				atu5=x.iloc[4,1:7]
				atu6=x.iloc[5,1:7]


				ap1=x.iloc[0,8:14] 
				ap2=x.iloc[1,8:14]
				ap3=x.iloc[2,8:14]
				ap4=x.iloc[3,8:14]
				ap5=x.iloc[4,8:14]
				ap6=x.iloc[5,8:14]

				choice=input('\nEscolha o programa a ser realizado, selecionando o numero indicado.\n 1-Leitura de Apalpalpadores e indicadores \t 2-Rotacao e translacao do sistema\n')
				if choice=='1':

					#nesta parte sera colocado as variaveis de entrada pelo usuario, sendo estas as translacoes e rotacoes em cada eixo de coordenada. As variaveis tem formato String, portanto devem ser alteradas para outro formato.
					dx=float(input('Digite o valor para deslocamento no eixo x[m]: '))
					dy=float(input('Digite o valor para deslocamento no eixo y[m]: '))
					dz=float(input('Digite o valor para deslocamento no eixo z[m]: '))
					rx=float(input('Digite o valor para rotacao no eixo x[rad]: '))
					ry=float(input('Digite o valor para rotacao no eixo y[rad]: '))
					rz=float(input('Digite o valor para rotacao no eixo z[rad]: '))


					ap=alignment1(6,dx,dy,dz,rx,ry,rz,ap1,ap2,ap3,ap4,ap5,ap6) #valores deslocamento de cada apalpador			
					atu=alignment1(6,dx,dy,dz,rx,ry,rz,atu1,atu2,atu3,atu4,atu5,atu6) #valores deslocamento de cada atuador

					print('\nLEITURA DOS ATUADORES\n')
					print('\nAtuador 1:  %2.6f \tAtuador 2:  %2.6f \tAtuador 3:  %2.6f \tAtuador 4:  %2.6f \tAtuador 5:  %2.6f \tAtuador 6:  %2.5f \n\n' %(atu[0],atu[1],atu[2],atu[3],atu[4],atu[5]))

					print('\nLEITURA DOS APALPADORES\n')
					print('\nApalpador 1:  %2.6f \tApalpador 2:  %2.6f \tApalpador 3:  %2.6f \tApalpador 4:  %2.6f \tApalpador 5:  %2.6f \tApalpador 6:  %2.6f \n\n' %(ap[0],ap[1],ap[2],ap[3],ap[4],ap[5]))	
				

				elif choice=='2':
					at=[]
					for i in range(6):
						at.append(float(input('\nleitura do atuador/apalpador %i: ' %(i+1))))
					atu_or_ap=input('\nSELECIONE SE AS LEITURAS SÃO PARA ATUADOR OU APALPADOR PELOS NUMEROS INDICADOS \n 1-Atuador \t Qualquer outro digito-Apalpador\n')
					
					if atu_or_ap=='1':
						var=alignment2(at[0],at[1],at[2],at[3],at[4],at[5],atu1,atu2,atu3,atu4,atu5,atu6)
					
					else:
						var=alignment2(at[0],at[1],at[2],at[3],at[4],at[5],ap1,ap2,ap3,ap4,ap5,ap6)
					
					print('    \u0394x:  %2.6f \t    \u0394y:  %2.6f \t    \u0394z:  %2.6f \t         Rx:  %2.6f \t         Ry:  %2.6f \t         Rz:  %2.6f \n\n\n\n\n' %(var[0],var[1],var[2],var[3],var[4],var[5]))			
				
				
		except (KeyboardInterrupt):
			print('\n\nPrograma finalizado')

	elif filename ==None:
		print('NENHUM ARQUIVO SELECIONADO, APLICATIVO ENCERRADO')
	elif len(pd.read_excel(filename).index)!=6:
		print('Numero de Apalpador/Atuador abaixo do que esperado')

	return

main()
