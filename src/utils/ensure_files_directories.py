import errno
import os

'''
Kontrollib, kas fail eksisteerib etteantud asukohas.  
Parameetrid:    filepath - faili nime sisaldav failitee.
Väljund: True/False, kui fail eksisteerib/ei eksisteeri.  
'''
def check_file(filepath):
    if os.path.isfile(filepath):
        return True
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filepath)


'''
Kontrollib, kas failid eksisteerivad etteantud asukohas.  
Parameetrid:    filepath - failitee.
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
Parameetrid:    directory - failitee kaustani.
Väljund: True/False, kui kaust eksisteerib/ei eksisteeri.
'''
def check_directory(directory):
    return os.path.isdir(directory)


'''
Loob kausta, kui kaust ei eksisteeri etteantud asukohas.
Parameetrid:    directory - failitee kaustani.
'''
def ensure_dir(directory):
    if not check_directory(directory):
        os.makedirs(directory)


'''
Kontrollib ja muudab failiteeks kausta asukoha.
Parameetrid:    directory - failitee kaustani.
'''
def change_dir(directory_path):
    ensure_dir(directory_path)
    os.chdir(directory_path)
