# mediafireDL

A simple python module to extract **MediaFire direct download link** and **file size**.detalls Give You This Module

## ✨ Features
- Get direct download URL
- Get file size
- Easy to use
- fast usage

## 🛠️ Usage 
```python
from __init__ import mf

url = "https://www.mediafire.com/file/2i79lqfyntphq4m/BAT.apk/file"

result = mf(url)

print(result)
print(result['data']['download'])
```
----
## Sample result:-
```ts
{                                                     status: 'true',
  data: {
    download: 'https://download2284.mediafire.com/nkvs7ouadgkgMBXBx1yovQ6yqL-kWX4OigWbpn38a8edX-vyIpb7qjbwXHwlvhdimTwM2OBgMJKXZ0tCj0PHa8ZZCzx3tS806yRxwy0i4gZaxe8ex5lu77D4_gYxJVewt0-rg9NlaHia6eivA88wI490_GpPnwp6WDmLkPZCuhYKXQE/2i79lqfyntphq4m/BAT.apk',
    fileSize: '5.76MB',
    uploadInfo: 'This file was uploaded from Sri Lanka on August 10, 2025 at 10:22 PM'
  }
}
```
## 📦 Installation

```bash
pip install mediafireDL
```