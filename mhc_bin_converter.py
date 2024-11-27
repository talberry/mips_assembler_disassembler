def mhc_file_to_bin (mhc_file_path, bin_file_path):
    mhc_file = open(mhc_file_path, 'rb')
    bin_file = open(bin_file_path, 'w')
    for byte in mhc_file.read():
        bin_byte = '{0:08b}'.format(byte)
        bin_file.write(bin_byte)

mhc_file_to_bin("program2.mhc", "program2.bin")