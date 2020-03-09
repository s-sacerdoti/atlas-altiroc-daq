def getDACList(board):
    dacList={}
    if board==2:
        dacList[(5,0)]=350
        dacList[(6,0)]=360
        dacList[(7,0)]=350
        dacList[(8,0)]=330
        dacList[(10,0)]=380
        dacList[(12,0)]=320
        dacList[(13,0)]=340
        dacList[(14,0)]=330
    elif board==3:
        dacList[(1,0)]=408
        dacList[(2,0)]=310
        dacList[(3,0)]=348
        dacList[(4,0)]=334
        dacList[(5,0)]=374
        dacList[(6,0)]=362
        dacList[(7,0)]=344
        dacList[(8,0)]=356      
        dacList[(10,0)]=340
        dacList[(11,0)]=374
        dacList[(12,0)]=360
        dacList[(13,0)]=382
        dacList[(14,0)]=418        
    elif board==8:
        dacList[(0,4)]=444#B8,4,0.98,ok 
        dacList[(1,4)]=440#B8,4,0.96,ok 
        dacList[(2,4)]=362#B8,4,1.00,ok 
        dacList[(3,4)]=444#B8,4,0.98,ok 
        dacList[(4,4)]=364#B8,4,0.97,ok 
        dacList[(5,4)]=440#B8,4,0.97,ok 
        dacList[(6,4)]=412#B8,4,0.83,ok 
        dacList[(7,4)]=378#B8,4,0.98,ok 
        dacList[(8,4)]=434#B8,4,0.99,ok 
        dacList[(9,4)]=310#B8,4,0.96,ok
        dacList[(10,4)]=456#B8,4,0.96,ok 
        dacList[(11,4)]=448#B8,4,1.00,ok 
        dacList[(12,4)]=416#B8,4,0.95,ok 
        dacList[(13,4)]=466#B8,4,0.26,PRB!!!!!!!!! 
        dacList[(14,4)]=308#B8,5,0.95,ok 

        #for lower cd
        dacList[(4,0)]=420#B8,4,0.99,ok 
        dacList[(4,1)]=396#B8,4,0.94,ok 
        dacList[(4,2)]=378#B8,4,1.00,ok 
        dacList[(4,3)]=370#B8,4,0.97,ok 
        #dacList[(4,4)]=362#B8,4,1.00,ok 
        dacList[(4,5)]=358#B8,4,0.97,ok 
        dacList[(4,6)]=354#B8,4,0.97,ok 
        dacList[(4,7)]=352#B8,4,0.98,ok 
        dacList[(9,0)]=346#B8,4,0.99,ok 
        dacList[(9,1)]=330#B8,4,0.99,ok 
        dacList[(9,2)]=320#B8,4,0.97,ok 
        dacList[(9,3)]=314#B8,4,0.98,ok 
        #dacList[(9,4)]=308#B8,4,1.00,ok 
        dacList[(9,5)]=306#B8,4,0.97,ok 
        dacList[(9,6)]=302#B8,4,1.00,ok 
        dacList[(9,7)]=300#B8,4,0.94,ok 
    elif board==9:
        dacList[(0,4)]=416#B9,3,1.00,ok 
        dacList[(10,4)]=420#B9,3,0.99,ok 
        dacList[(1,4)]=408#B9,3,0.97,ok 
        dacList[(2,4)]=410#B9,3,0.99,ok 
        dacList[(3,4)]=446#B9,3,0.99,ok 
        dacList[(4,4)]=306#B9,3,0.96,ok 
        dacList[(5,4)]=420#B9,3,0.96,ok 
        dacList[(6,4)]=396#B9,3,0.96,ok 
        dacList[(7,4)]=482#B9,3,0.98,ok 
        dacList[(8,4)]=420#B9,3,0.98,ok 
        dacList[(9,4)]=348#B9,3,1.00,ok
        #dacList[(11,4)]=1020#B9,3,0.99,ok AMWAYS TRIGGERING
        dacList[(12,4)]=456#B9,3,1.00,ok 
        dacList[(13,4)]=382#B9,3,0.99,ok 
        dacList[(14,4)]=348#B9,5,0.97,ok 
        pass
    elif board==10:
        pass
    elif board==11:
        pass


        
    elif board==12:#cd4
        dacList[(0,4)]=435#B12,4,0.990000  
        dacList[(1,4)]=410#B12,4,1.000000 
        dacList[(2,4)]=370#B12,4,1.000000 
        dacList[(3,4)]=465#B12,4,0.960000 
        dacList[(4,4)]=340#B12,4,1.000000 
        dacList[(5,4)]=460#B12,4,1.000000 
        dacList[(6,4)]=430#B12,4,0.990000 
        dacList[(7,4)]=435#B12,4,0.990000 
        dacList[(8,4)]=415#B12,4,1.000000 
        dacList[(9,4)]=360#B12,4,0.990000
        dacList[(10,4)]=425#B12,4,1.000000 
        dacList[(11,4)]=410#B12,4,1.000000 
        #dacList[(12,4)]=1195#B12,4,0.990000 Always triggering
        dacList[(13,4)]=455#B12,4,0.990000 
        dacList[(14,4)]=360#B12,5,0.99,ok
    elif board==13:
        # dacList[(0,0)]=326#B13,4,0.98,ok 
        # dacList[(1,0)]=308#B13,4,0.98,ok 
        # dacList[(2,0)]=332#B13,4,0.97,ok 
        # dacList[(3,0)]=320#B13,4,0.97,ok 
        # dacList[(4,0)]=302#B13,4,0.89,ok 
        # dacList[(5,0)]=394#B13,4,0.97,ok 
        # dacList[(7,0)]=312#B13,4,0.99,ok 
        # dacList[(8,0)]=342#B13,4,0.99,ok 
        # dacList[(9,0)]=320#B13,4,0.95,ok
        # dacList[(10,0)]=322#B13,4,1.00,ok 
        # dacList[(11,0)]=344#B13,4,0.93,ok 
        # dacList[(12,0)]=364#B13,4,0.96,ok 
        # dacList[(13,0)]=352#B13,4,0.96,ok 
        # #dacList[(14,0)]=330#B13,4,0.16,PRB!!!!!!!!!
        # dacList[(14,0)]=338#B13,5,0.95,ok 


        dacList[(0,0)]=320#B13,3,0.96,ok 
        dacList[(1,0)]=302#B13,3,0.99,ok 
        dacList[(2,0)]=324#B13,3,0.96,ok 
        dacList[(3,0)]=312#B13,3,0.98,ok 
        dacList[(4,0)]=294#B13,3,0.96,ok 
        dacList[(5,0)]=380#B13,3,0.99,ok 
        dacList[(7,0)]=304#B13,3,1.00,ok 
        dacList[(8,0)]=334#B13,3,0.99,ok 
        dacList[(9,0)]=312#B13,3,0.99,ok
        dacList[(10,0)]=316#B13,3,0.98,ok 
        dacList[(11,0)]=336#B13,3,0.98,ok 
        dacList[(12,0)]=354#B13,3,0.99,ok 
        dacList[(13,0)]=342#B13,3,0.97,ok
        #dacList[(14,0)]=324#B13,3,0.01,PRB!!!!!!!!! 
        dacList[(14,0)]=338#B13,5,0.95,ok
    elif board==14:
        pass



        
        
    elif board==15:
        dacList[(0,4)]=330
        dacList[(1,4)]=310
        dacList[(2,4)]=340
        dacList[(3,4)]=330
        dacList[(4,4)]=320
        dacList[(5,4)]=400
        dacList[(7,4)]=320
        dacList[(8,4)]=350      
        dacList[(9,4)]=340  
        dacList[(10,4)]=330
        dacList[(11,4)]=350
        dacList[(12,4)]=370
        dacList[(13,4)]=360
        dacList[(14,4)]=360
        dacList[(15,4)]=300
        dacList[(16,4)]=380
        dacList[(17,4)]=330
        dacList[(18,4)]=390
        dacList[(19,4)]=370      
        dacList[(20,4)]=350
        dacList[(21,4)]=340
        dacList[(22,4)]=430
        dacList[(23,4)]=400
        dacList[(24,4)]=360        
    elif board==18:
        dacList[(0,0)]=360
        dacList[(1,0)]=390
        dacList[(2,0)]=406
        dacList[(3,0)]=340
        #dacList[(4,0)]=440
        dacList[(5,0)]=360
        #dacList[(6,0)]=
        #dacList[(7,0)]=
        #dacList[(8,0)]=      
        dacList[(9,0)]=356  
        dacList[(10,0)]=344
        dacList[(11,0)]=336
        dacList[(12,0)]=326
        dacList[(13,0)]=376
        dacList[(14,0)]=376
        
    return dacList
