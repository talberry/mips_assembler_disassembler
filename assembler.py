import sys

op_codes = {
    'add': '000000', 'sub': '000000', 'lw': '100011',
    'sw': '101011', 'beq': '000100', 'bne': '000101'
}

func_codes = {
    'add': '100000', 'sub': '100010', 'and': '100100',
    'or': '100101', 'slt': '101010'
}

registers = {
    '$zero': '00000', '$t1': '01001', '$t2': '01010', '$t3': '01011',
    '$t4': '01100', '$t5': '01101', '$t6': '01110', '$t7': '01111',
    '$s0': '10000', '$s1': '10001', '$s2': '10010', '$s3': '10011',
    '$s4': '10100', '$s5': '10101', '$s6': '10110', '$s7': '10111'
}

shift_logic_amount = "00000"

def assemble_file(bin_file_path, asm_file_path, mhc_file_path):
    """Convert assembly file to binary and machine code files."""
    try:
        with (open(asm_file_path, 'r') as asm_file,
              open(bin_file_path, 'w') as bin_file,
              open(mhc_file_path, 'wb') as mhc_file):
            
            error = False
            for line_num, line in enumerate(asm_file, 1):
                try:
                    if code := assemble_asm(line):
                        bin_file.write(code)
                        mhc_file.write(int(code, 2).to_bytes(4, byteorder='big'))
                except ValueError as e:
                    print(f"Error on line {line_num}: {e}")
                    error = True
            
            if error:
                print("Assembly failed due to errors")
                sys.exit(1)
                
    except IOError as e:
        print(f"Error accessing files: {e}")
        sys.exit(1)

def assemble_asm(asm_line):
    """Convert a single assembly instruction to binary.
    
    Args:
        asm_line (str): A single line of assembly code
        
    Returns:
        str: Binary representation of the instruction
        
    Raises:
        ValueError: If the instruction is invalid or cannot be processed
    """
    # Remove comments and whitespace
    asm_line = asm_line.split("#")[0].strip()
    if not asm_line:
        return ''
    
    parts = asm_line.split()
    if not parts:
        return ''
        
    op_code = parts[0]
    
    if op_code in func_codes:  # R-type instruction
        return handle_r_type(parts)
    elif op_code in op_codes:  # I-type instruction
        return handle_i_type(parts)
    else:
        raise ValueError(f"Unknown instruction: {op_code}")

def handle_r_type(parts):
    """Handle R-type instruction encoding.
    
    Raises:
        ValueError: If the instruction format is invalid
    """
    if len(parts) != 4:
        raise ValueError(f"R-type instruction requires 4 parts, got {len(parts)}")
        
    op_code, rd, rs, rt = parts
    try:
        rd, rs, rt = rd.strip(","), rs.strip(","), rt.strip(",")
        return (op_codes[op_code] + 
                registers[rs] + 
                registers[rt] + 
                registers[rd] + 
                shift_logic_amount + 
                func_codes[op_code])
    except KeyError as e:
        raise ValueError(f"Invalid register or operation: {e}")

def handle_i_type(parts):
    """Handle I-type instruction encoding.
    
    Raises:
        ValueError: If the instruction format is invalid
    """
    if len(parts) < 3:
        raise ValueError("I-type instruction requires at least 3 parts")
    
    op_code = parts[0]
    try:
        if op_code in ('lw', 'sw'):
            if '(' not in parts[2] or ')' not in parts[2]:
                raise ValueError("Invalid memory access format")
            offset, rs = parts[2].strip(")").split("(")
            rt = parts[1].strip(",")
        else:  # beq, bne
            if len(parts) != 4:
                raise ValueError(f"{op_code} requires 4 parts")
            rs, rt, offset = [p.strip(",") for p in parts[1:]]
            
        offset_val = int(offset)
        if not -32768 <= offset_val <= 32767:
            raise ValueError(f"Offset {offset_val} out of range")
            
        return (op_codes[op_code] + 
                registers[rs] + 
                registers[rt] + 
                f'{offset_val & 0xFFFF:016b}')
        
    except (KeyError, ValueError) as e:
        raise ValueError(f"Invalid instruction format: {e}")

if __name__ == '__main__':
    assemble_file("program.bin", "program.asm", "program.mhc")
