def getDACList(board):
    dacList={}
    if board==2:
        dacList[(2,5,0)]=350
        dacList[(2,6,0)]=360
        dacList[(2,7,0)]=350
        dacList[(2,8,0)]=330
        dacList[(2,10,0)]=380
        dacList[(2,12,0)]=320
        dacList[(2,13,0)]=340
        dacList[(2,14,0)]=330
    elif board==3:
        dacList[(3,1,0)]=408
        dacList[(3,2,0)]=310
        dacList[(3,3,0)]=348
        dacList[(3,4,0)]=334
        dacList[(3,5,0)]=374
        dacList[(3,6,0)]=362
        dacList[(3,7,0)]=344
        dacList[(3,8,0)]=356      
        dacList[(3,10,0)]=340
        dacList[(3,11,0)]=374
        dacList[(3,12,0)]=360
        dacList[(3,13,0)]=382
        dacList[(3,14,0)]=418        
    elif board==8:
        dacList[(8,0,4)]=412#B8,3,1.00,ok 
        dacList[(8,1,4)]=406#B8,3,0.96,ok 
        dacList[(8,2,4)]=340#B8,3,1.00,ok 
        dacList[(8,3,4)]=412#3,0.99,ok 
        dacList[(8,4,4)]=350#3,0.99,ok 
        dacList[(8,5,4)]=408#3,0.99,ok 
        dacList[(8,6,4)]=388#3,0.72,PRB!!!!!!!!! 
        dacList[(8,7,4)]=356#3,0.97,ok 
        dacList[(8,8,4)]=404#3,0.97,ok 
        dacList[(8,9,4)]=298#3,0.98,ok 
        dacList[(8,10,4)]=426#3,0.98,ok 
        dacList[(8,11,4)]=418#3,0.98,ok 
        dacList[(8,12,4)]=388#3,0.99,ok 
        dacList[(8,13,4)]=436#3,0.17,PRB!!!!!!!!! 
        dacList[(8,14,4)]=308#5,0.95,ok 
    elif board==9:
        dacList[(9,0,4)]=416#B9,3,1.00,ok 
        dacList[(9,10,4)]=420#B9,3,0.99,ok 
        dacList[(9,1,4)]=408#B9,3,0.97,ok 
        dacList[(9,2,4)]=410#B9,3,0.99,ok 
        dacList[(9,3,4)]=446#B9,3,0.99,ok 
        dacList[(9,4,4)]=306#B9,3,0.96,ok 
        dacList[(9,5,4)]=420#B9,3,0.96,ok 
        dacList[(9,6,4)]=396#B9,3,0.96,ok 
        dacList[(9,7,4)]=482#B9,3,0.98,ok 
        dacList[(9,8,4)]=420#B9,3,0.98,ok 
        dacList[(9,9,4)]=348#B9,3,1.00,ok
        #dacList[(9,11,4)]=1020#B9,3,0.99,ok AMWAYS TRIGGERING
        dacList[(9,12,4)]=456#B9,3,1.00,ok 
        dacList[(9,13,4)]=382#B9,3,0.99,ok 
        dacList[(9,14,4)]=348#B9,5,0.97,ok 
        pass
    elif board==10:
        dacList[(10,0,4)]=458#3,0.97,ok 
        dacList[(10,1,4)]=396#3,0.98,ok 
        dacList[(10,2,4)]=428#3,0.99,ok 
        dacList[(10,3,4)]=402#3,1.00,ok 
        dacList[(10,4,4)]=322#3,0.99,ok 
        dacList[(10,5,4)]=354#3,1.00,ok 
        dacList[(10,6,4)]=412#3,0.95,ok 
        dacList[(10,7,4)]=352#3,1.00,ok 
        dacList[(10,8,4)]=402#3,1.00,ok 
        dacList[(10,9,4)]=330#3,0.96,ok
        dacList[(10,10,4)]=384#3,1.00,ok 
        #dacList[(10,11,4)]=1022#3,1.00,ok
        dacList[(10,12,4)]=358#3,0.99,ok 
        dacList[(10,13,4)]=408#3,0.96,ok 
        dacList[(10,14,4)]=326#5,0.89,ok 
        pass
    elif board==11:
        dacList[(11,0,4)]=390#3,1.00,ok 
        dacList[(11,1,4)]=406#3,1.00,ok 
        #dacList[(11,2,4)]=1022#3,0.12,PRB!!!!!!!!! 
        dacList[(11,3,4)]=442#3,0.97,ok 
        dacList[(11,4,4)]=374#3,0.99,ok 
        dacList[(11,5,4)]=514#3,0.96,ok 
        dacList[(11,6,4)]=408#3,0.95,ok 
        dacList[(11,7,4)]=398#3,0.97,ok 
        dacList[(11,8,4)]=426#3,1.00,ok 
        dacList[(11,9,4)]=368#3,1.00,ok 
        dacList[(11,10,4)]=410#3,0.97,ok
        dacList[(11,11,4)]=428#3,0.99,ok 
        dacList[(11,12,4)]=412#3,0.96,ok
        dacList[(11,13,4)]=410#3,0.99,ok 
        dacList[(11,14,4)]=342#5,0.97,ok 
        pass


        
    elif board==12:#cd4
        dacList[(12,0,4)]=400#3,0.97,ok 
        dacList[(12,1,4)]=380#3,0.99,ok 
        dacList[(12,2,4)]=348#3,0.97,ok 
        dacList[(12,3,4)]=402#3,0.97,ok 
        dacList[(12,4,4)]=326#3,1.00,ok 
        dacList[(12,5,4)]=426#3,0.97,ok 
        dacList[(12,6,4)]=396#3,0.98,ok 
        dacList[(12,7,4)]=400#3,0.99,ok 
        dacList[(12,8,4)]=380#3,1.00,ok 
        dacList[(12,9,4)]=346#3,0.97,ok
        dacList[(12,10,4)]=394#3,0.98,ok 
        dacList[(12,11,4)]=380#3,0.99,ok 
        #dacList[(12,12,4)]=1022#3,1.00,ok 
        dacList[(12,13,4)]=416#3,0.97,ok 
        dacList[(12,14,4)]=360#5,0.98,ok 

        pass
    elif board==13:
        dacList[(13,0,0)]=320#B13,3,0.96,ok 
        dacList[(13,1,0)]=302#B13,3,0.99,ok 
        dacList[(13,2,0)]=324#B13,3,0.96,ok 
        dacList[(13,3,0)]=312#B13,3,0.98,ok 
        dacList[(13,4,0)]=294#B13,3,0.96,ok 
        dacList[(13,5,0)]=380#B13,3,0.99,ok 
        dacList[(13,7,0)]=304#B13,3,1.00,ok 
        dacList[(13,8,0)]=334#B13,3,0.99,ok 
        dacList[(13,9,0)]=312#B13,3,0.99,ok
        dacList[(13,10,0)]=316#B13,3,0.98,ok 
        dacList[(13,11,0)]=336#B13,3,0.98,ok 
        dacList[(13,12,0)]=354#B13,3,0.99,ok 
        dacList[(13,13,0)]=342#B13,3,0.97,ok
        #dacList[(13,14,0)]=324#B13,3,0.01,PRB!!!!!!!!! 
        dacList[(13,14,0)]=338#B13,5,0.95,ok
    elif board==14:
        #dacList[(14,0,4)]=1022#3,1.00,ok 
        dacList[(14,1,4)]=728#3,0.95,ok 
        #dacList[(14,2,4)]=1022#3,1.00,ok 
        dacList[(14,3,4)]=912#3,0.91,ok 
        dacList[(14,4,4)]=636#3,0.96,ok 
        #dacList[(14,5,4)]=1022#3,1.00,ok 
        dacList[(14,6,4)]=622#3,0.99,ok 
        #dacList[(14,7,4)]=1022#3,1.00,ok 
        dacList[(14,8,4)]=478#3,0.94,ok 
        dacList[(14,9,4)]=678#3,0.89,ok 
        #dacList[(14,10,4)]=1022#3,1.00,ok 
        #dacList[(14,11,4)]=1022#3,1.00,ok 
        dacList[(14,12,4)]=660#3,0.97,ok 
        dacList[(14,13,4)]=732#3,0.91,ok 
        #dacList[(14,14,4)]=592#3,0.65,PRB!!!!!!!!!    
        dacList[(14,14,4)]=676#5,0.02,PRB!!!!!!!!! 
        pass
    elif board==15:
        pass
    elif board==18:
        pass
        
    return dacList                       
