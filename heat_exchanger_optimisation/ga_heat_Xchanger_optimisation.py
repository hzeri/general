import random
import os
import timeit
import time
import numpy as np
from scipy.special import lambertw
import math


def remove_parents(word_array,parent1,parent2): #remove the parents i.e. the positions 1,2,3 and 4
    word_array.remove(parent1)
    word_array.remove(parent2)

def mutation_position(word_array): #chooses a random word and the position in the word where the mutation occurs
    elem= random.choice(word_array) #choose a random element from the array
    print(elem)
    pos = word_array.index(elem)
    pos =int(pos)
    return(pos)

def mutation1(word_array, factor,mut_prob): #mutaion function; hte arguments are the population and the mutation to add
    n=1/mut_prob #the mutation has a fixed probability of occuring
    n=int(n)
    num=random.randint(1,n)
    if num==1:
        pos = mutation_position(word_array) #position for the mutations
        s[pos].A0 = factor*s[pos].A0 #add the mutation in the selected position
        s[pos].t2 = factor*s[pos].t2
        s[pos].hi = factor*s[pos].hi
        s[pos].ho = factor*s[pos].ho
        s[pos].vo = factor*s[pos].vo

def fitness(word_array, throttle_time): #tests the quality of the solutions by analysisng them against the objective function; the lower value the better
   
    #n= len(word_array) #length of the array
    n =5
    i=0
    pop_num=n
    obj_func= [[None] * n,[None] * n]
    corresp={}
    while i<n:
        #r = os.system("echo hello world") #testing purposes only
        
        if word_array[i].T2 - word_array[i].T1 <0 or word_array[i].t1-word_array.t2>0 or word_array[i].v0<0 or word_array[i].vi < 0 or word_array[i].C < 0:
            #word_array[i].A0= 1000000000
            obj_func[0][i]=word_array[i].C + 10000000000000+ i
        elif word_array[i].C < 1:
            word_array[i].A0 = word_array[i].A0*100
            word_array[i].T2 = word_array[i].T2*100
        else:
            obj_func[0][i]=word_array[i].C # obj function value
            print("test: obj function=",word_array[i].C)
        obj_func[1][i]=word_array[i] #set corresponding to the obj function value
        corresp[obj_func[0][i]]=obj_func[1][i] #dictionary that corresponds the obj_func value to the corresponding set
        i+=1
        time.sleep(throttle_time) #throttle time in seconds
    obj_func[0].sort(reverse=False) #sort the values in descending order
    k=0
    obj_func_ordered=[None]*pop_num
    while k<pop_num: #places the ordered words with lower obj_func value in an array
        obj_func_ordered[k]=corresp.get(obj_func[0][k])
        k+=1
    
    #break the wordlist in half so that only the top 5 carries on to the next generation
    
    fit = [None] * pop_num
    j=0
    while j<5: #places the best words in the 'fit' array
        fit[j]=obj_func_ordered[j]
        #exec_time_word[j].strip("\n") #remove the trailing "\n"
        j+=1
    
    return obj_func_ordered


class in_vars: #create an object with the photo and all the relevant information
    def __init__(self,t2,A0,hi,ho,vo):
        
        self.A0 = A0 # outside tube surface area, cm^2
        self.hi  = hi #inside tube heat transfer coefficient
        self.ho = ho #outside tube heat transfer coefficient
        self.t2 = t2 #coolant outlet temperature
        self.vo = vo #averagev veolocity of fluiid outside tubes, cm^3/s
        #objective function variables
        self.C_C= 10 #coolant cost, EUR/yr
        self.y=5000 #operating hours/yr
        self.Ca= 100 #Annual cost of heat exchanger per unit outside tube surface area (EUR/cm^2)*yr
        self.Ci= 2 #Annual cost of supplying m*N/h to pump fluid flowing inside tubes, EUr*h/m*N*yr
        self.Co= 1 #Annual cost of supplying m*N/h to pump shell side fluid, EUr*h/m*N*yr
        #Given variables
        self.Wi = 100 #flowrate if the inside tubes, cm^3/s
        self.T1= 50 #(working fluid) hot fluid outlet temperature, ºC
        self.T2= 20 #(working fluid) hot fluid inlet temperature, ºC
        self.t1= 2 #colant fluid inlet temperature, ºC
        self.sp= 0.1 #tube spacing
        self.Di= 0.2 #inside diameter
        self.Do= 0.3 #outside diameter
        self.Q= 1000 #heat transfer rate in the heat escheanger J/s
        self.Ft = 1 #multipass exchange factor. for singlepass exchangers, this value is 1
        self.roo= 1 #density of the fluid outside the tubes in g/cm3
        self.roi= 1 #density of the fluid inside the tubes in g/cm3
        self.c = 4.18 #specific heat at constant pressure, in J/(g*K)
        self.nb =4 #number ofbafle spacing on shell side = number of baffles + 1
        
        #Unspecified variables

        #self.Wc =self.roo*self.vo*self.s0
        self.phii=0.5*0.01 #phi = 0.5*friction factor, which is being approximated to 0.01
        self.phio=0.5*0.01 #phi = 0.5*friction factor, which is being approximated to 0.01
        self.Ei=self.phii*self.hi**3.5
        self.Eo=self.phio*self.ho**4.75
        self.vi =self.Wi/self.roi #average velocity of fluiid side tubes, cm^3/s
        self.Nt =self.Wi*4/(self.vi*math.pi*self.Di**2)
        self.Lt = self.A0/(self.Nt*math.pi*self.Do) #tube length
        self.Ai = self.Di*self.Lt #outside tube surface area, cm^2
        self.fA=self.Ai/self.A0
        self.Uo =1/(1/(self.fA*self.hi)+1/self.ho)
        self.dt1=self.T1-self.t1
        self.dt2 = self.T2 - self.t2
        #self.dt2 = -self.Q/(self.Ft*self.Uo*self.A0)*lambertw(-self.Q*math.exp(self.dt1+np.log(self.dt1))/(self.Ft*self.Uo*self.A0),0)
        self.Wc = self.Q/(self.c*(self.dt1-self.dt2+self.T2-self.T1))
        self.so = self.Wc/(self.roo*self.vo)
        
        #objective function
        self.C = self.c*self.Wc*self.y+ self.Ca*self.A0 + self.Ci*self.Ei*self.A0+self.Co*self.Eo*self.A0
        #add atributes corresponding to the remaining optimisaiton variables

def short_result(s,lenght): #prints the results of the 4 optimisation variables
        print("Final result")
        print("vector [t2 ,A0, hi, ho, vo, C] : ")
        j=0
        while j<5:
            print(s[j].t2,s[j].A0,s[j].hi,s[j].ho,s[j].vo,s[j].C)
            j+=1 



def crossover(parent1,parent2,gen):

    children1= in_vars(parent1.t2,parent1.A0,parent2.hi,parent2.ho,parent2.vo)
    children2= in_vars(parent2.t2,parent2.A0,parent1.hi,parent1.ho,parent1.vo)
    gen.append(children1)
    gen.append(children2)
    remove_parents(gen,parent1,parent2)

#main
# thus far the best gen_num/num_prob ratio seems to be 1500:1/8
mut_prob = 2**-4 #probability of a random mutation occuring; you have to choose a number that corresponds to 2^(-n)
gen_num = 1500 #max number of generations until the algorithm stops
#gen_num = int((1500/0.125)*mut_prob) #use this one instead if it is desired to utilise the ideal gen_num/num_prob ratio
factor1 = 0.9
factor2 = 0.92
factor3 = 1.1
factor4 = 1.07
throttle_time =0
#popl=population(wordlist) # places the wordlist in the array
pop = [
    [100.2,4,.8,.9,2.34],
    [80,.19,.7,.85,3.6],
    [190,43,.34,.46,1.0],
    [105,84,.28,.43,2.3],
    [180,34,.89,.79,4.2],
    [60,94,1.89,.769,4.4],
    [200,50,0.10,0.20,2.1],
    [80,50,0.10,0.20,2.4],
    [100,20,0.60,0.10,1.6],
    [60,220,0.120,0.4500,4.56],
    [110,120,0.10,0.20,2.6],
    [90,90,0.10,0.20,2.3],
    [115,60,0.10,0.20,24],
    [105,70,0.10,0.20,2.7],
]

n_elem = len(pop) #number of elements per generation
i=0
s=[]

i= int(i)
while i<n_elem:
    s.append(in_vars(pop[i][0],pop[i][1],pop[i][2],pop[i][3],pop[i][4]))
    i+=1
i=0
try:
    while i<gen_num: #if clause to limit the max number of generations
        #crossover step
        crossover(s[0],s[1],s)
        crossover(s[1],s[3],s)
        crossover(s[2],s[4],s)
        #crossover(s[0],s[1],s)
        #mutation step
        mutation1(s,factor1, mut_prob)
        mutation1(s,factor2, mut_prob)
        mutation1(s,factor3, mut_prob)
        mutation1(s,factor4, mut_prob)
        #selection of the fittest elements
        s= fitness(s,throttle_time)
        short_result(s,n_elem)
        i+=1
    #else:
        #long_result(s,n_elem)
except KeyboardInterrupt: #shows the final result even if the program is interrupted
    short_result(s,n_elem)
