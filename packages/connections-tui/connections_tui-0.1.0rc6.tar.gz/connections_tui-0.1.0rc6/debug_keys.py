#!/usr/bin/env python3
"""Debug script to identify handheld device button key codes."""

import readchar

print("Handheld Device Button Debugger")
print("=" * 50)
print("Press buttons on your device to see their key codes.")
print("Press 'q' to quit.")
print("=" * 50)
print()

while True:
    try:
        key = readchar.readkey()
        
        if key.lower() == 'q':
            print("\nExiting...")
            break
        
        # Print detailed information about the key
        print("Key received:")
        print(f"  String representation: {repr(key)}")
        print(f"  Length: {len(key)}")
        
        if len(key) == 1:
            ord_val = ord(key)
            print(f"  Ordinal value: {ord_val}")
            print(f"  Hex value: 0x{ord_val:02x}")
            print(f"  Binary: {bin(ord_val)}")
        else:
            print("  Multi-byte sequence:")
            for i, byte in enumerate(key):
                ord_val = ord(byte)
                print(f"    Byte {i}: ord={ord_val}, hex=0x{ord_val:02x}, char={repr(byte)}")
            
            # Try to interpret as different formats
            if len(key) >= 2:
                # Little-endian 16-bit
                val_le = ord(key[0]) | (ord(key[1]) << 8)
                print(f"  As little-endian 16-bit: {val_le} (0x{val_le:04x})")
                
                # Big-endian 16-bit
                val_be = (ord(key[0]) << 8) | ord(key[1])
                print(f"  As big-endian 16-bit: {val_be} (0x{val_be:04x})")
            
            if len(key) >= 4:
                # Try 32-bit interpretations
                val_le32 = (ord(key[0]) | 
                            (ord(key[1]) << 8) | 
                            (ord(key[2]) << 16) | 
                            (ord(key[3]) << 24))
                print(f"  As little-endian 32-bit: {val_le32} (0x{val_le32:08x})")
                
                val_be32 = ((ord(key[0]) << 24) | 
                            (ord(key[1]) << 16) | 
                            (ord(key[2]) << 8) | 
                            ord(key[3]))
                print(f"  As big-endian 32-bit: {val_be32} (0x{val_be32:08x})")
        
        print()
        print("Expected values:")
        print("  U = 0x1, D = 0x2, L = 0x4, R = 0x8")
        print("  L1 = 0x400, R1 = 0x800, L2 = 0x1000, R2 = 0x2000")
        print("-" * 50)
        print()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted. Exiting...")
        break
    except Exception as e:
        print(f"\nError: {e}")
        print(f"Key was: {repr(key) if 'key' in locals() else 'unknown'}")
        print()

