import pandas as pd
import dic as d
class File:
    def __init__(self):
       self.df=0 
    def read_file(self):
        self.df = pd.read_csv('modi_sic_one_pass_assembler\ASSEMBLY.csv', delimiter=';')
        self.df = self.df.apply(lambda x: x.str.replace(';', ''))
        print(self.df.head(5)) 

