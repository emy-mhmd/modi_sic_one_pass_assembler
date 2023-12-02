import pandas as pd
import dic as d

class File:
    def __init__(self):
       self.df=0 
    def read_file(self):
        self.df = pd.read_csv('modi_sic_one_pass_assembler\ASSEMBLY.csv', delimiter=';',header=None)
        self.df = self.df.apply(lambda x: x.str.replace(';', ''))
        #print(self.df.head(40))

class Onepass:
    def __init__(self):
        self.locationcounter=[]
        self.symboltable={}
        self.objectcode=[]
        self.pointerLC=0

    def read_line(self,f):
        self.locationcounter.append(f.df.iloc[0,2])
        self.pointerLC = hex(int(f.df.iloc[0,2],16))
        self.pointerLC = self.pointerLC[2:].upper()
        self.pointerLC = self.pointerLC.zfill(4)
        
        for index,row in f.df.iloc[1:-1].iterrows():

            if row[0].strip() !='':
                self.symboltable[row[0].strip()]=self.locationcounter[-1]

            if self.check_byte(row[1]):
                if self.check_byte_c(row[2]):
                    obj=''
                    for char in row[2][2:-1]:
                        obj+=d.ASCII[char]
                    self.objectcode.append(obj)
                    self.pointerLC = hex(int(self.pointerLC, 16) + int(len(row[2][2:-1])))

                if self.check_byte_x(row[2]):
                    self.objectcode.append(row[2][2:-1])
                    self.pointerLC = hex(int(self.pointerLC, 16) + int(len(row[2][2:-1])/2))

            elif self.check_word(row[1]):
                hex_value=int(row[2],10)
                hex_value=hex(hex_value)[2:].zfill(6)
                self.objectcode.append(hex_value)
                self.pointerLC = hex(int(self.pointerLC, 16) + 3)
                
            elif self.check_resW(row[1]):
                hex_value=int(row[2],10)
                 
                hex_value=hex_value*3
                self.pointerLC = hex(int(self.pointerLC, 16) + hex_value)

            elif self.check_resB(row[1]):
                hex_value=int(row[2],10) 
                self.pointerLC = hex(int(self.pointerLC, 16) + hex_value)

            elif self.check_imm(row[1][0]):
                self.pointerLC = hex(int(self.pointerLC, 16) + 3)
                if self.check_format3(row[1][1:-1]):
                    print("dw")

            elif self.check_format3(row[1]):
                    self.pointerLC = hex(int(self.pointerLC, 16) + 3)
                    if self.check_indix(str(row[2])[-1]):
                        if isinstance(row[2], str):
                            if row[2][0:-2].strip() in self.symboltable:
                                for key,value in d.opcode_3.items():
                                    if value==row[1].strip():
                                        obj=key+self.symboltable[row[2][0:-2].strip()]
                                        obj=int(obj,16)
                                        value=int('8000',16)
                                        obj+=value
                                        obj=hex(obj)[2:]
                                        self.objectcode.append(obj)

                                
                    else:
                        if isinstance(row[2], str):
                            if row[2].strip() in self.symboltable:
                                for key,value in d.opcode_3.items():
                                    if value==row[1].strip():
                                        obj=key+self.symboltable[row[2].strip()]
                                        self.objectcode.append(obj)

                        elif row[1].strip()=='RSUB':                 
                            obj="4C0000"
                            self.objectcode.append(obj)


                
            elif self.check_format1(row[1]): 
                self.pointerLC = hex(int(self.pointerLC, 16) +1) 
                for key,value in d.opcode_1.items():
                    if value==row[1].strip():                       
                        self.objectcode.append(key) 
                 

            
            self.pointerLC = hex(int(self.pointerLC, 16))
            self.pointerLC = self.pointerLC[2:].upper()
            self.pointerLC = self.pointerLC.zfill(4)
            self.locationcounter.append(self.pointerLC)
        print (self.objectcode)    


                     

          

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
    



