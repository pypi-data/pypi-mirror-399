# XNOR_module/__init__.py

import base64
import random
import hashlib
import sys
import string

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

ESCAPE_MAP = {'-': '<dash>', '<': '<lt>', '>': '<gt>', '|': '<pipe>', '_': '<us>'}
UNESCAPE_MAP = {v: k for k, v in ESCAPE_MAP.items()}

def copy_to_clipboard(text: str):
    if CLIPBOARD_AVAILABLE:
        pyperclip.copy(text)
        print("[Copied to clipboard]")
    else:
        print("[Install pyperclip for automatic clipboard copy]")

def escape_text(text: str) -> str:
    for k, v in ESCAPE_MAP.items():
        text = text.replace(k, v)
    return text

def unescape_text(text: str) -> str:
    for k, v in UNESCAPE_MAP.items():
        text = text.replace(k, v)
    return text

def shuffled_alphabet(key: int):
    letters = list(string.ascii_lowercase)
    random.seed(key)
    random.shuffle(letters)
    return letters

def generate_salt():
    return random.randint(1000, 9999)

def checksum(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:8]

def encode_to_cv_format(text: str, base_key: int):
    salt = generate_salt()
    chk = checksum(text)
    out = [f"<salt:{salt}>"]
    for i, char in enumerate(text):
        if char == ' ':
            out.append('<sp>')
        elif char.isalpha():
            key = base_key + salt + i
            alphabet = shuffled_alphabet(key)
            index = alphabet.index(char.lower()) + 1
            pipes = '|' * index
            case = '++' if char.isupper() else '--'
            out.append(pipes + case + '_')
        else:
            out.append(char)
    out.append(f"<chk:{chk}>")
    return ''.join(out)

def decode_from_cv(encoded_text: str, base_key: int):
    salt_start = encoded_text.find("<salt:") + 6
    salt_end = encoded_text.find(">")
    if salt_start == -1 or salt_end == -1:
        raise ValueError("Missing salt token")
    salt = int(encoded_text[salt_start:salt_end])
    encoded_text = encoded_text[salt_end + 1:]

    decoded = []
    i = 0
    pos = 0
    chk_token = ''

    while i < len(encoded_text):
        if encoded_text.startswith('<sp>', i):
            decoded.append(' ')
            i += 4
            pos += 1
            continue
        if encoded_text.startswith('<chk:', i):
            chk_token = encoded_text[i:]
            break

        chunk = ''
        while i < len(encoded_text) and encoded_text[i] != '_':
            chunk += encoded_text[i]
            i += 1
        i += 1

        pipe_count = chunk.count('|')
        if pipe_count == 0:
            continue

        key = base_key + salt + pos
        alphabet = shuffled_alphabet(key)
        letter = alphabet[pipe_count - 1]
        if '++' in chunk:
            letter = letter.upper()
        decoded.append(letter)
        pos += 1

    decoded_text = ''.join(decoded)
    if not chk_token.startswith('<chk:'):
        raise ValueError("Missing checksum token")
    chk_value = chk_token[5:13]
    if checksum(decoded_text) != chk_value:
        raise ValueError("Checksum failed — wrong key or tampered data")
    return decoded_text

def encode_via_64Xcv(text: str, key: int):
    safe = escape_text(text)
    stage1 = encode_to_cv_format(safe, key)
    result = base64.b64encode(stage1.encode()).decode()
    copy_to_clipboard(result)
    return result

def decode_via_64Xcv(text: str, key: int):
    stage1 = base64.b64decode(text).decode()
    decoded = decode_from_cv(stage1, key)
    result = unescape_text(decoded)
    copy_to_clipboard(result)
    return result

def user_mode():
    print("USER MODE (interactive)")
    print("1: Encode text")
    print("2: Decode text")
    print("3: Encode then decode text")

    try:
        choice = int(input("Enter a choice (1-3): "))
    except ValueError:
        print("Invalid input, must be a number 1-3")
        sys.exit(1)

    if choice not in [1, 2, 3]:
        print("Choice must be 1, 2, or 3")
        sys.exit(1)

    text = input("Enter your text: ")
    try:
        key = int(input("Enter a key (integer): "))
    except ValueError:
        print("Key must be an integer")
        sys.exit(1)

    if choice == 1:
        encoded = encode_via_64Xcv(text, key)
        print("Encoded:", encoded)
    elif choice == 2:
        try:
            decoded = decode_via_64Xcv(text, key)
            print("Decoded:", decoded)
        except Exception as e:
            print("Decode failed:", e)
    elif choice == 3:
        encoded = encode_via_64Xcv(text, key)
        print("Encoded:", encoded)
        try:
            decoded = decode_via_64Xcv(encoded, key)
            print("Decoded:", decoded)
        except Exception as e:
            print("Decode failed:", e)

def auto_mode(args):
    mode = args[1].lower()
    try:
        key = int(args[2])
    except ValueError:
        print("Key must be an integer")
        sys.exit(1)

    text = " ".join(args[3:])

    if mode == "encode":
        print(encode_via_64Xcv(text, key))
    elif mode == "decode":
        try:
            print(decode_via_64Xcv(text, key))
        except Exception as e:
            print("Decode failed:", e)
    else:
        print("Invalid mode. Use 'encode' or 'decode'.")
        sys.exit(1)
