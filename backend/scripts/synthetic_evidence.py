"""Invented local evaluation files; never substitutes business transitions."""
def synthetic_pdf(text):
    lines=text.splitlines()
    commands=['BT /F1 12 Tf 40 750 Td']
    for line in lines:
        escaped=line.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
        commands.append(f'({escaped}) Tj 0 -16 Td')
    commands.append('ET')
    stream='\n'.join(commands).encode('latin-1')
    objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream']
    raw=b'%PDF-1.4\n';offsets=[0]
    for n,obj in enumerate(objects,1):offsets.append(len(raw));raw+=str(n).encode()+b' 0 obj\n'+obj+b'\nendobj\n'
    start=len(raw);raw+=b'xref\n0 6\n0000000000 65535 f \n'+b''.join(f'{o:010d} 00000 n \n'.encode() for o in offsets[1:])
    return raw+b'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n'+str(start).encode()+b'\n%%EOF\n'


def synthetic_portrait():
    """A clearly illustrated invented face in a valid PNG, for evaluation only."""
    import struct,zlib
    width,height=80,100;rows=[]
    for y in range(height):
        row=bytearray([0])
        for x in range(width):
            face=((x-40)/24)**2+((y-41)/31)**2<1
            eye=(x-31)**2+(y-38)**2<5 or (x-49)**2+(y-38)**2<5
            mouth=32<x<48 and y in {54,55}
            hair=face and y<24;body=y>76 and abs(x-40)<30
            color=(45,60,90) if eye or mouth or hair else (239,203,158) if face else (48,90,150) if body else (235,242,251)
            row.extend(color)
        rows.append(bytes(row))
    def chunk(kind,data):return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!IIBBBBB',width,height,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b'')
