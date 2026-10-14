import importlib.util
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from backend.tests.support import Harness


class ProtocolTests(unittest.TestCase):
    def protocol(self):
        self.assertIsNotNone(importlib.util.find_spec('backend.app.services.evidence_protocol'),'Versioned private protocol missing')
        from backend.app.services import evidence_protocol
        return evidence_protocol

    def test_unicode_order_and_large_money_canonicalization(self):
        p=self.protocol()
        self.assertEqual(p.canonical_bytes({'z':'9000000000000000000','a':'e\u0301\n/','n':None,'b':True}),b'{"a":"\xc3\xa9\\n/","b":true,"n":null,"z":"9000000000000000000"}')

    def test_numbers_surrogates_duplicates_and_secret_material_are_rejected(self):
        p=self.protocol()
        for data in [{'x':1},{'x':1.5},{'x':'\ud800'},{'payout_code':'123456'},{'pin':'1234'},{'raw_signed_tx':'0x01'}]:
            with self.assertRaises(ValueError): p.canonical_bytes(data)
        with self.assertRaises(ValueError): p.parse_canonical(b'{"a":"x","a":"y"}')

    def test_raw_upload_is_immutable_and_changed_missing_bytes_fail(self):
        self.protocol()
        from backend.app.services.evidence import prepare_upload,original_bytes
        from backend.app.commands import DomainError
        with TemporaryDirectory() as root:
            data=b'\x89PNG\r\n\x1a\nsynthetic photo bytes'
            item=prepare_upload(data,'image/png',root=Path(root))
            self.assertEqual(original_bytes(item,root=Path(root)),data)
            file=Path(root)/item['storage_key']
            file.write_bytes(b'\x89PNG\r\n\x1a\nchanged synthetic photo')
            with self.assertRaisesRegex(DomainError,'evidence_mismatch'): original_bytes(item,root=Path(root))
            file.unlink()
            with self.assertRaisesRegex(DomainError,'evidence_unavailable'): original_bytes(item,root=Path(root))

    def test_invalid_file_type_and_size_are_rejected(self):
        self.protocol()
        from backend.app.services.evidence import prepare_upload
        from backend.app.commands import DomainError
        with TemporaryDirectory() as root:
            for data,mime in [(b'<svg/>','image/png'),(b'','application/pdf'),(b'%PDF-'+b'a'*10485760,'application/pdf')]:
                with self.assertRaises(DomainError): prepare_upload(data,mime,root=Path(root))


if __name__=='__main__': unittest.main()
