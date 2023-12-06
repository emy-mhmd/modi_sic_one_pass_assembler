import pandas as pd
import dic as d

class File:
    def __init__(self):
       self.df=0 
    def read_file(self):
        self.df = pd.read_csv('Input.csv', delimiter=';',header=None)
        self.df = self.df.apply(lambda x: x.str.replace(';', ''))



class Onepass:
    def __init__(self):
        self.locationcounter=[]
        self.hteRecord = []
        self.symboltable={}
        self.symboltable_ForwardReferencing={}
        self.objectcode=[]
        self.pointerLC=0
        self.hline=''
        self.endline=''
        self.relocation_dic = {}
        self.lc_obj = {}
        self.collect_trecord_locationCounter = []
        self.relocation = ""
        self.interrupt_trecord = False
        self.modi_TRecord = False
        self.res_start = 0
        self.counter_bits = 0
        self.end_trecord = ""
        self.tRecord_started = True
        self.locationCounter_ForwarReferencing = ""
        self.Reference_ForwarReferencing = ""

    def read_line(self,f):
        self.locationcounter.append(f.df.iloc[0,2])
        self.pointerLC = hex(int(f.df.iloc[0,2],16))
        self.pointerLC = self.pointerLC[2:].upper()
        self.pointerLC = self.pointerLC.zfill(4)

        tline = ""
        tline += 'T00'+self.pointerLC
        start_trecord = self.pointerLC

        start_trecord2 = ""
        obj = ""
        
        
        for index,row in f.df.iloc[1:-1].iterrows():

            if row[0].strip() !='':
                self.symboltable[row[0].strip()]=self.locationcounter[-1]

            if row[1].strip() != "RSUB" and self.check_format3(row[1].strip()) and self.interrupt_trecord == True:
                self.tRecord_started = False
                self.interrupt_trecord = False
            
            if row[0].strip() in self.symboltable_ForwardReferencing.keys():
                self.locationCounter_ForwarReferencing = self.symboltable[row[0].strip()]
                self.Reference_ForwarReferencing = row[0].strip()
                self.tRecord_started = False
                self.modi_TRecord = True
                start_trecord2 = self.locationcounter[index-1]  


            if(not self.tRecord_started or self.counter_bits >= 30 or 
               ( (self.check_resW(row[1]) or self.check_resB(row[1])) and 
                (f.df.iloc[index-1][1].strip() != "RESW" or f.df.iloc[index-1][1].strip() != "RESB") )):
                self.relocation = ""
                for i in range (len(self.collect_trecord_locationCounter)):
                    self.relocation += self.relocation_dic[self.collect_trecord_locationCounter[i]]
                self.relocation = self.relocation + "0" * (12 - len(self.relocation))
                self.relocation = hex(int(self.relocation, 2))[2:].zfill(3).upper() 
                
                # get TRecord END
                self.end_trecord = self.pointerLC
                
                # CALCULATE THE SIZE  
                if self.end_trecord and start_trecord:
                    size_trecord = int(self.end_trecord, 16) - int(start_trecord, 16)
                    size_trecord = hex(size_trecord)[2:].upper()
                    size_trecord = size_trecord.zfill(2)

                # INSERT THE SIZE AND RELOCATION BITS TO THE TRECORD
                if len(tline) >= 7:
                    tline =  tline[:7] + size_trecord + self.relocation + tline[7:]
        
                if self.res_start == 0:  
                    self.hteRecord.append(tline)  
                    tline = ""            
                
                self.counter_bits = 0
                self.collect_trecord_locationCounter = []

                if(self.modi_TRecord):
                    list = self.get_tForwardReferencing(self.locationCounter_ForwarReferencing, self.Reference_ForwarReferencing)
                    for i in range(len(list)):
                        self.hteRecord.append(list[i])

                if ( (self.check_resW(row[1]) or self.check_resB(row[1])) and 
                (f.df.iloc[index-1][1].strip() != "RESW" or f.df.iloc[index-1][1].strip() != "RESB") ):
                    self.tRecord_started = True


    
            if((not (self.check_resW(row[1]) or self.check_resB(row[1])) and 
              (f.df.iloc[index-1][1].strip() == "RESW" or f.df.iloc[index-1][1].strip() == "RESB"))):
                self.tRecord_started = False

            if((not self.tRecord_started and self.counter_bits == 0 and
              not (self.check_resW(row[1]) or self.check_resB(row[1]))) or 
              (not (self.check_resW(row[1]) or self.check_resB(row[1])) and 
              (f.df.iloc[index-1][1].strip() == "RESW" or f.df.iloc[index-1][1].strip() == "RESB"))):
                if(not self.modi_TRecord):
                    start_trecord = self.pointerLC
                else:
                    start_trecord = start_trecord2
                tline += 'T00'+start_trecord
                if self.modi_TRecord:
                    self.modi_TRecord = False
                self.tRecord_started = True
                self.counter_bits = 0
                self.res_start = 0


            if self.check_byte(row[1]):
                self.relocation_dic[self.pointerLC] = "0"  
                self.collect_trecord_locationCounter.append(self.pointerLC)
                
                if self.check_byte_c(row[2]):
                    obj=''
                    for char in row[2][2:-1]:
                        obj += d.ASCII[char]
                    self.lc_obj[self.pointerLC] = obj    
                    self.objectcode.append(obj)
                    tline += obj
                    self.pointerLC = hex(int(self.pointerLC, 16) + int(len(row[2][2:-1])))
                    self.counter_bits += int(len(row[2][2:-1]))
                    if len(row[2][2:-1]) != 3:
                        self.interrupt_trecord = True

                if self.check_byte_x(row[2]):
                    self.relocation_dic[self.pointerLC] = "0"  
                    self.objectcode.append(row[2][2:-1])
                    self.lc_obj[self.pointerLC] = row[2][2:-1]
                    tline += row[2][2:-1]
                    self.pointerLC = hex(int(self.pointerLC, 16) + int(len(row[2][2:-1])/2))
                    self.counter_bits += int(len(row[2][2:-1])/2) 
                    if len(row[2][2:-1])/2 != 3:
                        self.interrupt_trecord = True
               
            elif self.check_word(row[1]):
                self.relocation_dic[self.pointerLC] = "0"  
                self.collect_trecord_locationCounter.append(self.pointerLC)
                hex_value=int(row[2],10)
                hex_value=hex(hex_value)[2:].zfill(6)
                self.lc_obj[self.pointerLC] = hex_value
                self.objectcode.append(hex_value)
                tline += hex_value
                self.pointerLC = hex(int(self.pointerLC, 16) + 3)
                self.counter_bits += 3


            elif self.check_resW(row[1]):
                self.lc_obj[self.pointerLC] = None
                hex_value=int(row[2],10)
                hex_value=hex_value*3
                self.pointerLC = hex(int(self.pointerLC, 16) + hex_value)
                self.res_start += 1

            elif self.check_resB(row[1]):
                self.lc_obj[self.pointerLC] = None
                hex_value=int(row[2],10) 
                self.pointerLC = hex(int(self.pointerLC, 16) + hex_value)
                self.res_start += 1

            elif self.check_format3(row[1]) or self.check_format3(row[1][1:-1]):
                opcode = 0
                for key,value in d.opcode_3.items():
                    if value==row[1].strip() or (value==row[1][1:-1].strip() and self.check_imm(row[1][0])):
                        opcode = key
                if self.check_indix(str(row[2])[-1]):
                    if isinstance(row[2], str):
                        self.relocation_dic[self.pointerLC] = "1"
                        

                        if row[2][0:-2].strip() in self.symboltable:
                            obj=opcode+self.symboltable[row[2][0:-2].strip()]
                            obj=int(obj,16)
                            value=int('8000',16)
                            obj+=value
                            obj=hex(obj)[2:].upper()

                        elif row[2][0:-2].strip() not in self.symboltable_ForwardReferencing.keys():
                            arr = []
                            arr.append(hex(int(self.pointerLC, 16) + 1)[2:])
                            self.symboltable_ForwardReferencing[row[2].strip()] = arr
                            obj=opcode+'0000'

                        elif row[2][0:-2].strip() in self.symboltable_ForwardReferencing.keys():
                            self.symboltable_ForwardReferencing[row[2].strip()].append(hex(int(self.pointerLC, 16) + 1)[2:]) 
                            obj=opcode+'0000'

                                    
                else:
                    
                    if isinstance(row[2], str):

                        if(self.check_imm(row[2][0])):
                            opcode = int(opcode, 16) + 1
                            opcode = hex(opcode)[2:].zfill(2).upper()

                            if  self.check_directImm(row[2][1:]):
                                address  = hex(int(row[2][1:], 16))[2:].zfill(4).upper()
                                obj=opcode+address
                                self.relocation_dic[self.pointerLC] = "0"
                            else:
                                row[2] = row[2][1:]



                        elif row[2].strip() in self.symboltable:
                            self.relocation_dic[self.pointerLC] = "1"
                            obj=opcode+self.symboltable[row[2].strip()]
                
                        elif row[2].strip() not in self.symboltable_ForwardReferencing.keys():
                            self.relocation_dic[self.pointerLC] = "1"
                            arr = []
                            arr.append(hex(int(self.pointerLC, 16) + 1)[2:])
                            self.symboltable_ForwardReferencing[row[2].strip()] = arr
                            obj=opcode+'0000'

                        elif row[2].strip() in self.symboltable_ForwardReferencing.keys():
                            self.relocation_dic[self.pointerLC] = "1"
                            self.symboltable_ForwardReferencing[row[2].strip()].append(hex(int(self.pointerLC, 16) + 1)[2:]) 
                            obj=opcode+'0000'


                    elif row[1].strip()=='RSUB': 
                        self.relocation_dic[self.pointerLC] = "0"  
                        obj="4C0000"
                

                self.lc_obj[self.pointerLC] = obj
                self.collect_trecord_locationCounter.append(self.pointerLC)
                self.pointerLC = hex(int(self.pointerLC, 16) + 3)
                self.objectcode.append(obj)
                tline += obj
                self.counter_bits += 3
                
            elif self.check_format1(row[1]): 
                self.interrupt_trecord = True
                self.relocation_dic[self.pointerLC] = "0"
                self.collect_trecord_locationCounter.append(self.pointerLC)
                self.pointerLC = hex(int(self.pointerLC, 16) +1) 
                for key,value in d.opcode_1.items():
                    if value==row[1].strip():                       
                        self.objectcode.append(key)
                        tline += key 

                      
            
            self.pointerLC = hex(int(self.pointerLC, 16))
            self.pointerLC = self.pointerLC[2:].upper()
            self.pointerLC = self.pointerLC.zfill(4)
            self.locationcounter.append(self.pointerLC)
            
        
        if(self.counter_bits != 0):
            self.relocation = ""
            for i in range (len(self.collect_trecord_locationCounter)):
                self.relocation += self.relocation_dic[self.collect_trecord_locationCounter[i]]
            self.relocation = self.relocation + "0" * (12 - len(self.relocation))
            self.relocation = hex(int(self.relocation, 2))[2:].zfill(3).upper() 
                
                # get TRecord END
            self.end_trecord = self.pointerLC
            
            # CALCULATE THE SIZE  
            if self.end_trecord and start_trecord:
                size_trecord = int(self.end_trecord, 16) - int(start_trecord, 16)
                size_trecord = hex(size_trecord)[2:].upper()
                size_trecord = size_trecord.zfill(2)

            # INSERT THE SIZE AND RELOCATION BITS TO THE TRECORD
            if len(tline) >= 7:
                tline =  tline[:7] + size_trecord + self.relocation + tline[7:]
            self.hteRecord.append(tline)

            if(self.modi_TRecord):
                list = self.get_tForwardReferencing(self.locationCounter_ForwarReferencing, self.Reference_ForwarReferencing)
                for i in range(len(list)):
                    self.hteRecord.append(list[i])
        

        # print(self.locationcounter)
        # print(self.objectcode)    
        # print(self.symboltable_ForwardReferencing)
        # print(self.relocation_dic)
        # print(self.lc_obj)
        # print(self.symboltable)
        # print(self.locationCounter_ForwarReferencing)
        #print(self.hteRecord)

        self.hte(f)

        return self.hteRecord
                     
    def hte(self,f):
        name=str(f.df.iloc[0,0]).strip().upper()
        name=name.ljust(6,'X')
        start=str(f.df.iloc[0,2]).zfill(6).strip()
        hex1=self.locationcounter[-1]
        hex2=self.locationcounter[0]
        int1=int(hex1,16)
        int2=int(hex2,16)
        prog_len=int1-int2
        prog_len=hex(prog_len)[2:]
        prog_len=prog_len.zfill(6).upper()
        self.hline=('H'+name+start+prog_len).strip()
        self.hteRecord.insert(0,self.hline)
        self.endline='E'+self.symboltable["FIRST"].zfill(6).upper()
        self.hteRecord.append(self.endline)
        print(self.hteRecord)

    def check_byte(self, row):
       
        if row.strip()== 'BYTE':  
            return True
        else:
            return False
    def check_byte_c(self, row):
        if row[0]=='C':
            
            return True
        else:
            return False
    def check_byte_x(self, row):  
         if row[0]=='X':
             return True
         else:
             return False      

    def check_word(self, row):
        if row.strip()=='WORD':
            return True
        else:
            return False

    def check_resB(self, row):
        if row.strip() =='RESB':
            return True
        else:
            return False
        
    def check_resW(self, row):
        if row.strip() == 'RESW':
            return True
        else:
            return False
        
    def check_format3(self, row):
       
        if row.strip() in d.opcode_3.values():
            return True
        else:
            return False
        
    def check_format1(self, row):
        if row.strip() in d.opcode_1.values():
            return True
        else:
            return False
        
    def check_indix(self, row):
        if row.strip()=='X':
            return True
        else:
            return False
        
    def check_imm(self, row):
        if row.strip()=='#':
            return True
        else:
            return False
        
    def check_directImm(self, imm):
        try:
            float(imm)
            return True
        except ValueError:
            return False 
    
    def get_tForwardReferencing(self, lc, reference):
        list_values = []
        list_hte = []
        tline = ""
        for key,value in self.symboltable_ForwardReferencing.items():
            if(key == reference):
                list_values = value
                break
        for i in range(len(list_values)):
            tline = "T00"+list_values[i].upper()+"02000"+lc
            list_hte.append(tline)
        return list_hte
