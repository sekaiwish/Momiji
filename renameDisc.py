import os

def replace(fpath):
    i = 0
    for path, subdirs, files in os.walk(fpath):
        for name in files:
            i += 1
            filename = os.path.join(path,name)
            extension = os.path.splitext(filename)[1]
            try:
                os.rename(filename, os.path.join(path, "000" + str(i) + extension))
            except FileExistsError:
                os.rename(filename, os.path.join(path, str(i)+ "_" + extension))
            #if i == 20:
            #    break

def main():
    replace("correctchat")
    #replace("horse_porn_and_sans_and_animal_crossing")
    #replace("vape-and-ddlc-and-niko")

main()
