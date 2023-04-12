# # -*- coding: utf-8 -*-
import rsa
import base64


class PasswordRSAer(object):
    public_key = """-----BEGIN RSA PUBLIC KEY-----
    MIGJAoGBAKCSKlSiayggESgvrQyTBMN74FlmkBi69B/1MPfj6rja3S5z250Sb78R
    llcGjcJ7iHsa1rhTsv1EMZY+5kt+6+nNEFjVzXePWMTqc54vccCYuobAhF8nAHxv
    cKID8Xr+PWmkiqgIZoHPV5V8zBSe3lHy8oazfv6+dgGUjOjZDgYVAgMBAAE=
    -----END RSA PUBLIC KEY-----
    """
    private_key = """-----BEGIN RSA PRIVATE KEY-----
    MIICXwIBAAKBgQCgkipUomsoIBEoL60MkwTDe+BZZpAYuvQf9TD34+q42t0uc9ud
    Em+/EZZXBo3Ce4h7Gta4U7L9RDGWPuZLfuvpzRBY1c13j1jE6nOeL3HAmLqGwIRf
    JwB8b3CiA/F6/j1ppIqoCGaBz1eVfMwUnt5R8vKGs37+vnYBlIzo2Q4GFQIDAQAB
    AoGAWt79Z9JXNGkZbJW2qHQXcQ4NBGs/x08eU2uun8tzjdQG8oAM3FKPvSEV5QBH
    f7XrokepFr3/gMd0DKRhxsAsew+6SxrNa2wOkrF1Etz6KS4SU1nbUdV/GCxo5a1E
    2C85HSGcosSCGE5KpMpTHOrSxunMdA3IntPOw8uai0v5JKECRQC3T3BcNl67GW93
    9IP3sISNGpPSzmuJlnX6Uf5VCVkmBXAvxK4gRRMZYPvG9H4cYf1S6WeSvTumxFdb
    98LEKAk62pM3XQI9AOA+XUF3b+zlrez0QZH3URdSGbbthrt4DwaNwXwmpHGHZg2M
    x30lqa+uR33KAgqEnWt7PJu7v14QDwA2GQJEIwQqu4KrT+RI9cogl2UBvQ6RpFhI
    FI1IVhvpkIbrn6a0Snuwo3tubY+oKNY1bOiPApKRdWduiKnC4k+Oxfe746EzNAUC
    PBDBeDRpGUrpSpq3EaM3iK6matd5XiTp7q19sCR3urfk9yIyD8HxK4G+Ewd6Lbbd
    e+nJFplIaR89MfHBGQJEWk8fpLDx1iV4mjQ/XZXISAK9b0d8LRSAVjRXn82kbcUt
    kmg6fHGjT/to8gBrTIh3h6QL06nMEprSRthh40792XdH4MI=
    -----END RSA PRIVATE KEY-----"""

    def rsa_encrypt_password(self, encrypted_password):
        """
        rsa加密
        """
        return base64.b64encode(rsa.encrypt(encrypted_password.encode('utf-8'),
                                            rsa.PublicKey.load_pkcs1(self.public_key.encode('utf-8')))).decode()

    def rsa_decrypt_password(self, encrypted_password):
        """
        rsa解密
        """
        return rsa.decrypt(base64.decodebytes(encrypted_password.encode('utf-8')),
                           rsa.PrivateKey.load_pkcs1(self.private_key.encode('utf-8'))).decode()


if __name__ == '__main__':
    p = PasswordRSAer()
    a = p.rsa_encrypt_password('1qaz!QAZ')
    print(a)

    b = p.rsa_decrypt_password(a)
    print(b)
