def to_signed32(n):
    return n if n < 0x80000000 else n - 0x100000000

def reverse_bit_order32(n: int) -> int:
    n = ((n >> 1) & 0x55555555) | ((n & 0x55555555) << 1)
    n = ((n >> 2) & 0x33333333) | ((n & 0x33333333) << 2)
    n = ((n >> 4) & 0x0F0F0F0F) | ((n & 0x0F0F0F0F) << 4)
    n = ((n >> 8) & 0x00FF00FF) | ((n & 0x00FF00FF) << 8)
    n = (n >> 16) | (n << 16)
    return n & 0xFFFFFFFF

def compute_crc32_on_words(words):
    count = 0
    reverse_bit_order_target = 0xFFFFFFFF
    while count < len(words) and words[count] != 0:
        v4 = reverse_bit_order32(words[count])
        for i in range(8):
            xorVal = to_signed32(v4 ^ reverse_bit_order_target)
            if xorVal >= 0:
                reverse_bit_order_target = (reverse_bit_order_target << 1) & 0xFFFFFFFF
            else:
                reverse_bit_order_target = ((reverse_bit_order_target << 1) ^ 0x04C11DB7) & 0xFFFFFFFF
            v4 = (v4 << 1) & 0xFFFFFFFF
        count += 1
    return reverse_bit_order32(~reverse_bit_order_target) & 0xFFFFFFFF

def string_to_word_array(s):
    arr = []
    encoded = s.encode('utf-16le')
    for i in range(0, len(encoded), 2):
        arr.append(encoded[i] + (encoded[i+1] << 8))
    arr.append(0)
    return arr

target_crc = 0xA7DC6E73

candidates = [
    "ntdll.dll",
    "kernel32.dll",
    "user32.dll",
    "advapi32.dll",
    "msvcrt.dll",
    "kernelbase.dll"
]

for candidate in candidates:
    words = string_to_word_array(candidate.lower())
    crc = compute_crc32_on_words(words)
    print(f"string: {candidate}, CRC: 0x{crc:08X}")
    if crc == target_crc:
        print(f" match: {candidate}")
