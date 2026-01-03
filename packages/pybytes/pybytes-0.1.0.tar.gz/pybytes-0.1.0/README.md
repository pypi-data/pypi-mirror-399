# pybytes

Byte'ı insan okuyabilir hale çeviren süper basit Python kütüphanesi.

```python
from pybytes import human_bytes, hb

print(human_bytes(123456789))  # 117.74 MB
print(hb(1073741824))          # 1.0 GB
print(human_bytes(1099511627776 * 1024))  # 1024.00 TB+