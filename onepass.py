import pandas as pd
import dic as d

class File:
    def __init__(self):
       self.df=0 
    def read_file(self):
        self.df = pd.read_csv('ASSEMBLY.csv', delimiter=';',header=None)
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

    def read_line(self,f):
        self.locationcounter.append(f.df.iloc[0,2])
        self.pointerLC = hex(int(f.df.iloc[0,2],16))
        self.pointerLC = self.pointerLC[2:].upper()
        self.pointerLC = self.pointerLC.zfill(4)

        tline = ""
        tline += 'T00'+self.pointerLC
        start_trecord = self.pointerLC
        tRecord_started = 1

        counter_bits = 0
        res_start = 0
        end_trecord = ""
        reach_end = 0
        modi_TRecord = 0
        start_trecord2 = ""
        locationCounter_ForwarReferencing = ""
        Reference_ForwarReferencing = ""
        temp_obj = ""

        for index,row in f.df.iloc[1:-1].iterrows():
            

            if(tRecord_started == 0 or counter_bits >= 30 or 
               ( (self.check_resW(row[1]) or self.check_resB(row[1])) and 
                (f.df.iloc[index-1][1].strip() != "RESW" or f.df.iloc[index-1][1].strip() != "RESB") )):
                if(counter_bits > 30):
                    end_trecord = self.locationcounter[index-2]
                elif modi_TRecord == 1:
                    end_trecord = self.locationcounter[index-2]
                    temp_obj = tline[-6:]
                    tline = tline[:-6]
                else:
                    end_trecord = self.locationcounter[index-1]
                   
                if end_trecord and start_trecord:
                    size_trecord = int(end_trecord, 16) - int(start_trecord, 16)
                    size_trecord = hex(size_trecord)[2:].upper()
                    size_trecord = size_trecord.zfill(2)


                if len(tline) >= 7:
                    tline =  tline[:7] + size_trecord + tline[7:]
        
                if res_start == 0:  
                    self.hteRecord.append(tline)  
                    tline = ""            
                    reach_end = 1
                
                counter_bits = 0

                if(modi_TRecord == 1):
                    list = self.get_tForwardReferencing(locationCounter_ForwarReferencing, Reference_ForwarReferencing)
                    for i in range(len(list)):
                        self.hteRecord.append(list[i])

                if ( (self.check_resW(row[1]) or self.check_resB(row[1])) and 
                (f.df.iloc[index-1][1].strip() != "RESW" or f.df.iloc[index-1][1].strip() != "RESB") ):
                    tRecord_started = 1
                    reach_end = 0


            if reach_end:
                tRecord_started = 0
                reach_end = 0

    
            if((not (self.check_resW(row[1]) or self.check_resB(row[1])) and 
              (f.df.iloc[index-1][1].strip() == "RESW" or f.df.iloc[index-1][1].strip() == "RESB"))):
                tRecord_started = 0

            if((tRecord_started == 0 and counter_bits == 0 and
              not (self.check_resW(row[1]) or self.check_resB(row[1]))) or 
              (not (self.check_resW(row[1]) or self.check_resB(row[1])) and 
              (f.df.iloc[index-1][1].strip() == "RESW" or f.df.iloc[index-1][1].strip() == "RESB"))):
                if(modi_TRecord == 0):
                    start_trecord = self.pointerLC
                else:
                    start_trecord = start_trecord2
                tline += 'T00'+start_trecord
                if modi_TRecord == 1:
                    tline += temp_obj
                    modi_TRecord = 0
                tRecord_started = 1
                counter_bits = 0
                res_start = 0


            if row[0].strip() !='':
                self.symboltable[row[0].strip()]=self.locationcounter[-1]

            if self.check_byte(row[1]):
                if self.check_byte_c(row[2]):
                    obj=''
                    for char in row[2][2:-1]:
                        obj += d.ASCII[char]
                    self.objectcode.append(obj)
                    tline += obj
                    self.pointerLC = hex(int(self.pointerLC, 16) + int(len(row[2][2:-1])))
                    counter_bits += int(len(row[2][2:-1]))

                if self.check_byte_x(row[2]):
                    self.objectcode.append(row[2][2:-1])
                    tline += row[2][2:-1]
                    self.pointerLC = hex(int(self.pointerLC, 16) + int(len(row[2][2:-1])/2))
                    counter_bits += int(len(row[2][2:-1])/2)   
               
            elif self.check_word(row[1]):
                hex_value=int(row[2],10)
                hex_value=hex(hex_value)[2:].zfill(6)
                self.objectcode.append(hex_value)
                tline += hex_value
                self.pointerLC = hex(int(self.pointerLC, 16) + 3)
                counter_bits += 3

            elif self.check_resW(row[1]):
                hex_value=int(row[2],10)
                hex_value=hex_value*3
                self.pointerLC = hex(int(self.pointerLC, 16) + hex_value)
                res_start += 1

            elif self.check_resB(row[1]):
                hex_value=int(row[2],10) 
                self.pointerLC = hex(int(self.pointerLC, 16) + hex_value)
                res_start += 1

            elif self.check_format3(row[1]) or self.check_format3(row[1][1:-1]):
                opcode = 0
                for key,value in d.opcode_3.items():
                    if value==row[1].strip() or (value==row[1][1:-1].strip() and self.check_imm(row[1][0])):
                        opcode = key
                if self.check_indix(str(row[2])[-1]):
                    if isinstance(row[2], str):
                        
                        if row[0].strip() in self.symboltable_ForwardReferencing.keys():
                            locationCounter_ForwarReferencing = self.symboltable[row[0].strip()]
                            Reference_ForwarReferencing = row[0].strip()
                            tRecord_started = 0
                            modi_TRecord = 1
                            start_trecord2 = self.locationcounter[index-1]


                        if row[2][0:-2].strip() in self.symboltable:
                            obj=opcode+self.symboltable[row[2][0:-2].strip()]
                            obj=int(obj,16)
                            value=int('8000',16)
                            obj+=value
                            obj=hex(obj)[2:]

                        elif row[2][0:-2].strip() not in self.symboltable_ForwardReferencing.keys():
                            arr = []
                            arr.append(hex(int(self.pointerLC, 16) + 1)[2:])
                            self.symboltable_ForwardReferencing[row[2].strip()] = arr
                            obj=opcode+'0000'

                        elif row[2][0:-2].strip() in self.symboltable_ForwardReferencing.keys():
                            self.symboltable_ForwardReferencing[row[2].strip()].append(hex(int(self.pointerLC, 16) + 1)[2:]) 
                            obj=opcode+'0000'
                
                elif self.check_imm(row[1][0]):
                    if isinstance(row[2], str):

                        if row[0].strip() in self.symboltable_ForwardReferencing.keys():
                            locationCounter_ForwarReferencing =  self.symboltable[row[0].strip()]
                            Reference_ForwarReferencing = row[0].strip()
                            tRecord_started = 0
                            modi_TRecord = 1
                            start_trecord2 = self.locationcounter[index-1]

                        if row[2].strip() in self.symboltable:
                            obj=opcode+self.symboltable[row[2].strip()]

                        elif row[2].strip() not in self.symboltable_ForwardReferencing.keys():
                            arr = []
                            arr.append(hex(int(self.pointerLC, 16) + 1)[2:])
                            self.symboltable_ForwardReferencing[row[2].strip()] = arr
                            obj=opcode+'0000'

                        elif row[2].strip() in self.symboltable_ForwardReferencing.keys():
                            self.symboltable_ForwardReferencing[row[2].strip()].append(hex(int(self.pointerLC, 16) + 1)[2:]) 
                            obj=opcode+'0000'

                else:
                    if isinstance(row[2], str):

                        if row[0].strip() in self.symboltable_ForwardReferencing.keys():
                            locationCounter_ForwarReferencing =  self.symboltable[row[0].strip()]
                            Reference_ForwarReferencing = row[0].strip()
                            tRecord_started = 0
                            modi_TRecord = 1
                            start_trecord2 = self.locationcounter[index-1]
            

                        if row[2].strip() in self.symboltable:
                            obj=opcode+self.symboltable[row[2].strip()]
                        
                        elif row[2].strip() not in self.symboltable_ForwardReferencing.keys():
                            arr = []
                            arr.append(hex(int(self.pointerLC, 16) + 1)[2:])
                            self.symboltable_ForwardReferencing[row[2].strip()] = arr
                            obj=opcode+'0000'

                        elif row[2].strip() in self.symboltable_ForwardReferencing.keys():
                            self.symboltable_ForwardReferencing[row[2].strip()].append(hex(int(self.pointerLC, 16) + 1)[2:]) 
                            obj=opcode+'0000'

                    

                    elif row[1].strip()=='RSUB':                 
                        obj="4C0000"
                
                self.pointerLC = hex(int(self.pointerLC, 16) + 3)
                self.objectcode.append(obj)
                tline += obj
                counter_bits += 3

        


                
            elif self.check_format1(row[1]): 
                self.pointerLC = hex(int(self.pointerLC, 16) +1) 
                for key,value in d.opcode_1.items():
                    if value==row[1].strip():                       
                        self.objectcode.append(key)
                        tline += key 
                 

            
            self.pointerLC = hex(int(self.pointerLC, 16))
            self.pointerLC = self.pointerLC[2:].upper()
            self.pointerLC = self.pointerLC.zfill(4)
            self.locationcounter.append(self.pointerLC)
        
        if(counter_bits != 0):
            end_trecord = self.pointerLC
            size_trecord = int(end_trecord, 16) - int(start_trecord, 16)
            size_trecord = hex(size_trecord)[2:].upper()
            size_trecord = size_trecord.zfill(2)
            if len(tline) >= 7:
                    tline =  tline[:7] + size_trecord + tline[7:]
            self.hteRecord.append(tline)
        if(modi_TRecord == 1):
                    list = self.get_tForwardReferencing(locationCounter_ForwarReferencing, Reference_ForwarReferencing)
                    for i in range(len(list)):
                        self.hteRecord.append(list[i])   
        

        self.hte(f)
        return self.hteRecord                     
    



    def check_byte(self,row):
       
        if row.strip()== 'BYTE':  
            return True
        else:
            return False
    def check_byte_c(self,row):
        if row[0]=='C':
            
            return True
        else:
            return False
    def check_byte_x(self,row):  
         if row[0]=='X':
             return True
         else:
             return False      

    def check_word(self,row):
        if row.strip()=='WORD':
            return True
        else:
            return False

    def check_resB(self,row):
        if row.strip() =='RESB':
            return True
        else:
            return False
        
    def check_resW(self,row):
        if row.strip()== 'RESW':
            return True
        else:
            return False
        
    def check_format3(self,row):
       
        if row.strip() in d.opcode_3.values():
            return True
        else:
            return False
        
    def check_format1(self,row):
        if row.strip() in d.opcode_1.values():
            return True
        else:
            return False
        
    def check_indix(self,row):
        if row.strip()=='X':
            return True
        else:
            return False
        
    def check_imm(self,row):
      
        if row.strip()=='#':
            return True
        else:
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
            tline = "T00"+list_values[i].upper()+"02"+lc
            list_hte.append(tline)
        return list_hte
    
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
        self.endline='E'+start
        self.hteRecord.append(self.endline)
        print(self.hteRecord)