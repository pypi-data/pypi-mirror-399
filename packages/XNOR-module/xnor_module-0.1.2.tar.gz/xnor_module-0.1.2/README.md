# XNOR_module

A Python module for encoding and decoding text with a custom CV format and Base64.

## Example

```python
from XNOR_module import encode_via_64Xcv, decode_via_64Xcv

encoded = encode_via_64Xcv("Hello", 123)
print(encoded)

decoded = decode_via_64Xcv(encoded, 123)
print(decoded)