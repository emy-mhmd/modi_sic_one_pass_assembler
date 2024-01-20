<h1 align="center">modi_sic_one_pass_assembler</h1>

## OVERVIEW
  The One Pass Assembler is a tool designed to process assembly code in a single pass, generating object code, symbol tables, and other relevant records. This README provides essential information on how to use and understand the functionalities of the One Pass Assembler.

## FEATURES
1. **INPUT PROCESSING:**
    -  The assembler reads assembly code from a CSV file using the Pandas library.
    -  Initializes a location counter and modifies it based on instruction format and type.
2. **SYMBOL TABLE**
    - Utilizes two dictionaries: "symbol_table" for declared references and "symboltable_forwardreferencing" for references not yet declared.
    - Handles forward referencing by assigning provisional addresses until their actual values are determined.
3. **MASKING BIT CALCULATION**
    - Determines the masking bit for object codes, indicating whether they can be modified.
    - For format-3 instructions (excluding RSUB), the masking bit is set to "1," while for byte, word, RSUB, and format-1 instructions, it is set to "0."
4. **T RECORDS MANAGEMENT**
    - Three flags, namely "trecord_start," "modi_trecord," and "interrupt_trecord," govern the creation and interruption of T records.
    - Initiates a new T record based on specific conditions such as encountering "ResW," "ResB," or a length of 1E.
    - Facilitates forward referencing T records by activating the "modi_trecord" flag.
    - Segments T records with the "interrupt_trecord" flag based on zero relocation bits and the first occurrence of a one bit in the relocation dictionary.
5. **OUTPUT GENERATION**
    - Produces HTE (Header, Text, End) records, symbol tables, and other relevant output.

## HOW TO USE

1. **INPUT FILE**
    - Prepare your assembly code in CSV format, ensuring proper columns for labels, opcodes, and operands.
2. **CODE EXECUTION**
    - Execute the one-pass assembler code, providing the path to your input CSV file.
3. **REVIEW OUTPUT**
    - Examine the generated symbol tables, HTE records, and any other relevant output files.

## DEPENDENICES
  - Python 3.x
  - Pandas library

## Sample Execution

```bash
python server.py
```


## SCREENSHOTS

![Untitled](https://github.com/emy-mhmd/modi_sic_one_pass_assembler/assets/113525757/7443b503-b092-4485-8530-ad891ffabe8d)
