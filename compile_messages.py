"""Compile .po files to .mo files using Python's built-in msgfmt module."""
import os
import struct
import array

def compile_po(po_file, mo_file):
    """Compile a .po file into a .mo file."""
    messages = {}
    msgid_parts = []
    msgstr_parts = []
    in_msgid = in_msgstr = False
    
    with open(po_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if not line or line.startswith('#'):
                if in_msgstr:
                    key = ''.join(msgid_parts)
                    val = ''.join(msgstr_parts)
                    messages[key] = val
                msgid_parts = []
                msgstr_parts = []
                in_msgid = in_msgstr = False
                continue
            
            if line.startswith('msgid '):
                if in_msgstr:
                    key = ''.join(msgid_parts)
                    val = ''.join(msgstr_parts)
                    messages[key] = val
                    msgid_parts = []
                    msgstr_parts = []
                in_msgid = True
                in_msgstr = False
                msgid_parts.append(line[6:].strip('"'))
            elif line.startswith('msgstr '):
                in_msgid = False
                in_msgstr = True
                msgstr_parts.append(line[7:].strip('"'))
            elif line.startswith('"') and line.endswith('"'):
                content = line[1:-1]
                if in_msgid:
                    msgid_parts.append(content)
                elif in_msgstr:
                    msgstr_parts.append(content)
        
        # Last entry
        if in_msgstr:
            key = ''.join(msgid_parts)
            val = ''.join(msgstr_parts)
            messages[key] = val

    # Process escape sequences in all values
    def unescape(s):
        return s.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
    
    processed = {}
    for k, v in messages.items():
        processed[unescape(k)] = unescape(v)
    messages = processed

    # Generate .mo file
    keys = sorted(messages.keys())
    offsets = []
    ids = strs = b''
    
    for key in keys:
        key_bytes = key.encode('utf-8')
        val_bytes = messages[key].encode('utf-8')
        offsets.append((len(ids), len(key_bytes), len(strs), len(val_bytes)))
        ids += key_bytes + b'\x00'
        strs += val_bytes + b'\x00'
    
    # The header is 7 32-bit unsigned integers
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]
    
    offsets_array = koffsets + voffsets
    
    with open(mo_file, 'wb') as output:
        output.write(struct.pack(
            'Iiiiiii',
            0x950412de,       # Magic
            0,                # Version
            len(keys),        # Number of strings
            7 * 4,            # Offset of table with original strings
            7 * 4 + len(keys) * 8,  # Offset of table with translation strings
            0,                # Size of hashing table
            0,                # Offset of hashing table
        ))
        output.write(array.array('i', offsets_array).tobytes())
        output.write(ids)
        output.write(strs)
    
    print(f"Compiled {po_file} -> {mo_file} ({len(keys)} messages)")


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    locale_dir = os.path.join(base_dir, 'locale')
    
    for lang in ['uz', 'ru']:
        po_path = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'django.po')
        mo_path = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'django.mo')
        if os.path.exists(po_path):
            compile_po(po_path, mo_path)
        else:
            print(f"Warning: {po_path} not found")
    
    print("Done!")
