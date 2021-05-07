import errno
import os

'''
Kontrollib, kas fail eksisteerib etteantud asukohas.  
Parameetrid:    filepath - failitee.
Väljund: True/False, kui fail eksisteerib/ei eksisteeri.  
'''
def check_file(filepath):
    if os.path.isfile(filepath):
        return True
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filepath)


'''
Kontrollib, kas failid eksisteerivad etteantud asukohas.  
Parameetrid:    directory - kataloogitee.
                files - failide nimed.
Väljund: True/False, kui kõik failid eksisteerivad/ei eksisteeri.
'''
def check_files(path, files):
    for file in files:
        filepath = path + file
        if not os.path.isfile(filepath):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filepath)

    return True


'''
Kontrollib, kas kaust eksisteerib etteantud asukohas.  
Parameetrid:    directory - kataloogitee.
Väljund: True/False, kui kaust eksisteerib/ei eksisteeri.
'''
def check_directory(directory):
    return os.path.isdir(directory)


'''
Loob kausta, kui kaust ei eksisteeri etteantud asukohas.
Parameetrid:    directory - kataloogitee.
'''
def ensure_dir(directory):
    if not check_directory(directory):
        os.makedirs(directory)


'''
Kontrollib ja muudab kataloogi.
Parameetrid:    directory - kataloogitee.
'''
def change_dir(directory_path):
    ensure_dir(directory_path)
    os.chdir(directory_path)
