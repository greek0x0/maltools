import pefile

def reverse_bits32(n):
    n = ((n >> 1) & 0x55555555) | ((n & 0x55555555) << 1)
    n = ((n >> 2) & 0x33333333) | ((n & 0x33333333) << 2)
    n = ((n >> 4) & 0x0F0F0F0F) | ((n & 0x0F0F0F0F) << 4)
    n = ((n >> 8) & 0x00FF00FF) | ((n & 0x00FF00FF) << 8)
    n = (n >> 16) | (n << 16)
    return n & 0xFFFFFFFF

def compute_crc32(name: str) -> int:
    accumulate_crc_value = 0xFFFFFFFF
    for ch in name:
        current_word = reverse_bits32(ord(ch))
        for _ in range(8):
            xorVal = (current_word ^ accumulate_crc_value)
            if (xorVal & 0x80000000) == 0:
                accumulate_crc_value = (accumulate_crc_value << 1) & 0xFFFFFFFF
            else:
                accumulate_crc_value = ((accumulate_crc_value << 1) ^ 0x04C11DB7) & 0xFFFFFFFF
            current_word = (current_word << 1) & 0xFFFFFFFF
    return reverse_bits32(~accumulate_crc_value) & 0xFFFFFFFF

kernel32_crcs = {
    0xADA2AFC2
}

ntdll_crcs = {
    0x4C3CB59B
}

msvcrt_crcs = {
    0xADA2AFC2
}
kernelbase_crcs = [ 
    0xADA2AFC2
]
user32_crcs = [
    0xE84B90E, 0xBDB44B02, 0x94DD41DA
]
shell32_crcs = [
    0x74BAEF5F
]
def check_exports(dll_path, target_crcs, label):
    pe = pefile.PE(dll_path)
    found_any = False
    print(f"\n=== Checking {label} ===")
    for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        if exp.name is None:
            continue
        name = exp.name.decode('utf-8')
        crc = compute_crc32(name)
        if crc in target_crcs:
            print(f" Function name: {name}")
            print(f" CRC: 0x{crc:08X}")
            print(f" Address: 0x{pe.OPTIONAL_HEADER.ImageBase + exp.address:08X}")
            found_any = True
    if not found_any:
        print()

check_exports("/mnt/c/Windows/System32/kernel32.dll", kernel32_crcs, "kernel32.dll")
check_exports("/mnt/c/Windows/System32/ntdll.dll", ntdll_crcs, "ntdll.dll")
check_exports("/mnt/c/Windows/System32/msvcrt.dll", msvcrt_crcs, 'msvcrt.dll')
check_exports('/mnt/c/Windows/System32/kernelbase.dll', kernelbase_crcs, 'kernelbase.dll')
check_exports('/mnt/c/Windows/System32/user32.dll', user32_crcs, 'user32.dll')
check_exports('/mnt/c/Windows/System32/shell32.dll', user32_crcs, 'shell32.dll')
