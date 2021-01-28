
_mod     = None

try:
    import srp._srp
    _mod = srp._srp
except ImportError:
    pass

if not _mod:
    try:
        import srp._ctsrp
        _mod = srp._ctsrp
    except:
        pass
    
if not _mod:
    import srp._pysrp
    _mod = srp._pysrp

User                           = _mod.User
Verifier                       = _mod.Verifier
create_salted_verification_key = _mod.create_salted_verification_key

SHA1      = _mod.SHA1
SHA224    = _mod.SHA224
SHA256    = _mod.SHA256
SHA384    = _mod.SHA384
SHA512    = _mod.SHA512

NG_1024   = _mod.NG_1024
NG_2048   = _mod.NG_2048
NG_4096   = _mod.NG_4096
NG_8192   = _mod.NG_8192
NG_CUSTOM = _mod.NG_CUSTOM

        
        

   
   

    
    
