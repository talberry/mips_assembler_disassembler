import sys

op_codes = {
    '000000': 'R-type',
    '100011': 'lw',
    '101011': 'sw',  
    '000100': 'beq',  
    '000101': 'bne'
}

func_codes = {
    '100000': 'add', 
    '100010': 'sub',  
    '100100': 'and',  
    '100101': 'or',  
    '101010': 'slt'
}

registers = {
    '00000': '$zero',
    '01001': '$t1', '01010': '$t2', '01011': '$t3',
    '01100': '$t4', '01101': '$t5', '01110': '$t6', '01111': '$t7',
    '10000': '$s0', '10001': '$s1', '10010': '$s2', '10011': '$s3',
    '10100': '$s4', '10101': '$s5', '10110': '$s6', '10111': '$s7'
}

def disassemble_from_mhc_file(mhc_file_path, asm_file_path):
    """Convert machine code file back to assembly.
    
    Args:
        mhc_file_path (str): Path to input machine code file
        asm_file_path (str): Path to output assembly file
        
    Raises:
        IOError: If there are issues with file operations
        ValueError: If the machine code is invalid
    """
    try:
        with open(mhc_file_path, 'rb') as mhc_file:
            content = mhc_file.read()
            if not content:
                raise ValueError("Input file is empty")
            output = ''.join(f'{byte:08b}' for byte in content)
            
        if len(output) % 32 != 0:
            raise ValueError("Invalid machine code format")
            
        asm = disassemble_bin(output)
        
        with open(asm_file_path, 'w') as asm_file:
            asm_file.write('\n'.join(asm) + '\n')
            
    except IOError as e:
        print(f"Error accessing files: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error processing machine code: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

def disassemble_bin(bin_str):
    """Convert binary string to assembly instructions."""
    instructions = []
    
    for i in range(0, len(bin_str), 32):
        instruction = bin_str[i:i+32]
        opcode_bin = instruction[:6]
        
        try:
            if opcode_bin == '000000':  # R-type
                instructions.append(handle_r_type_disassembly(instruction))
            elif opcode_bin in op_codes:  # I-type
                instructions.append(handle_i_type_disassembly(instruction))
            else:
                raise ValueError(f"Unknown opcode: {opcode_bin}")
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error in instruction {i//32}: {e}")
            
    return instructions

def handle_r_type_disassembly(instruction):
    """Handle R-type instruction decoding."""
    try:
        rs_bin = instruction[6:11]
        rt_bin = instruction[11:16]
        rd_bin = instruction[16:21]
        func_bin = instruction[26:32]
        
        if func_bin not in func_codes:
            raise ValueError(f"Invalid function code: {func_bin}")
            
        return f"{func_codes[func_bin]} {registers[rd_bin]}, {registers[rs_bin]}, {registers[rt_bin]}"
    except KeyError as e:
        raise ValueError(f"Invalid register or function code: {e}")

def handle_i_type_disassembly(instruction):
    """Handle I-type instruction decoding."""
    try:
        opcode_bin = instruction[:6]
        rs_bin = instruction[6:11]
        rt_bin = instruction[11:16]
        offset_bin = instruction[16:32]
        
        opcode = op_codes[opcode_bin]
        offset = int(offset_bin, 2)
        if offset & 0x8000:  # Handle negative numbers
            offset -= 0x10000
            
        if opcode in ('lw', 'sw'):
            return f"{opcode} {registers[rt_bin]}, {offset}({registers[rs_bin]})"
        else:  # beq, bne
            return f"{opcode} {registers[rs_bin]}, {registers[rt_bin]}, {offset}"
    except KeyError as e:
        raise ValueError(f"Invalid register or opcode: {e}")

if __name__ == '__main__':
    disassemble_from_mhc_file("program.mhc", "disassembled.asm")