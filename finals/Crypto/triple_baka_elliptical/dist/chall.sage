from Crypto.Util.number import getPrime, inverse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import os


# I'm not telling you!
from secrets import get_triplet_special, flag


def get_triplet(n):
    return (randint(1, n-1), randint(1, n-1), randint(1, n-1))

def generator(E, n):    
    G = randint(1, n-1) * E.gens()[0]
    return G
        
def present_point(P):
    Px = int(P[0])
    Py = int(P[1])
    
    return f"E({Px}, {Py})"

def encrypt_flag(flag, secret):
    sha1 = hashlib.sha1()
    sha1.update(str(secret).encode('ascii'))
    key = sha1.digest()[:16]
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(flag, 16))
    data = {}
    data['iv'] = iv.hex()
    data['encrypted_flag'] = ciphertext.hex()
    return data

def menu():
    print("\nI woke up in front of my computer today. Good morning!")
    print("1. Get Curve Parameters")
    print("2. Get Public Keys")
    print("3. Power up")
    print("4. Next Round")
    print("5. Re-roll Seed")
    print("6. Encrypt Message")
    print("7. Exit")

def main():
    # Curve parameters
    p = 105886573969025913437316829028340576120749917395393545078900775119795796908917
    a = 14913447334678636586744091818632544201825021590110099928928917985190272508572
    b = 8988483279631832375618715923302785696462621573188305903979148179894798461774
    
    E = EllipticCurve(GF(p), [a,b])
    order = 105886573969025913437316829028340576120707376139801067826169405348016754727097
    G = generator(E, order)

    round_state = 1  

    m, t, n = get_triplet(order)
    shared_secret = (m * t * n * G).xy()[0]
    
    while True:
        menu()
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            print(f"{p = }")
            print(f"{a = }")
            print(f"{b = }")
            print("G =", present_point(G))

        elif choice == "2":
            if round_state == 1:
                m_1 = m * G
                t_1 = t * G
                n_1 = n * G
                
                assert m_1 in E
                assert t_1 in E
                assert n_1 in E
                
                print("I'll send them all out!")
                print("M =", present_point(m_1))
                print("T =", present_point(t_1))
                print("N =", present_point(n_1))

            else:
                m_2 = m * t * G
                t_2 = t * n * G
                n_2 = n * m * G
                
                assert m_2 in E
                assert t_2 in E
                assert n_2 in E
                
                print("I'll send them all out!")
                print("MT =", present_point(m_2))
                print("TN =", present_point(t_2))
                print("NM =", present_point(n_2))

        elif choice == "3":
            if round_state != 1:
                print("A bit late for this now, hehe :3")
                continue
                
            k = input("Enter k [3, order-1]: ")
            if not k.isdigit():
                print("I asked for an integer, baka.")
                continue
                
            k = Integer(k)
            if k < 3: # Ehh??? Why the hell did he disallow k = 2??? Hmm... Maybe it's just (literally) worthless?
                print("Without something for the three of us, we won't do it!")
                continue

            if k > order - 1:
                print("We're lazy, choose something smaller.")
                continue

            thridiots = Integer(m**k + t**k + n**k)
            res = thridiots * G
            print(f"M^{k} + T^{k} + N^{k} = ", present_point(res))
                

        elif choice == "4":
            round_state = 2
            
            print("I take off to a world unknown, giving a ride to hopes~")
        
        elif choice == "5":
            pw = input("Input password: ")
            same = False

            md5 = hashlib.md5()
            md5.update(pw.encode())
            pw = md5.hexdigest()
            
            if pw == "d8ee97d78c13c9f094e4048c8427a4fd":
                same = True

            if same:
                print("Admin powers granted! Welcome back, LamazeP-senpai~")
                m, t, n = get_triplet_special(G, order)
                shared_secret = (m * t * n * G).xy()[0]
                
                print()
                print("Psst~~ A gift for you, senpai!")
                print((m+t+n))
               
            else:
                print("Re-rolled!")
                m, t, n = get_triplet(order)
                shared_secret = (m * t * n * G).xy()[0]
        
        elif choice == "6":
            encrypted = encrypt_flag(flag, shared_secret)
            print(encrypted)                
            
        elif choice == "7":
            print("Instead of coming up with a good solution, I instantly gave up~")
            break

        else:
            print("Teto: \'You really are stupid.\'")


if __name__ == "__main__":
    main()



