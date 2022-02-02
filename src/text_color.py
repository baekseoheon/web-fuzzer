import sys

def specify_text_color():
    what_OS = sys.platform.startswith('win')
    if what_OS:
        # Windows deserves coloring too :D
        G = '\033[92m'  # green
        Y = '\033[93m'  # yellow
        B = '\033[94m'  # blue
        R = '\033[91m'  # red
        W = '\033[0m'   # white
        try:
            import win_unicode_console , colorama
            win_unicode_console.enable()
            colorama.init()
            #Now the unicode will work ^_^
        except:
            print("[!] Error: Coloring libraries not installed, no coloring will be used")
            G = Y = B = R = W = G = Y = B = R = W = ''
    else:
        G = '\033[92m'  # green
        Y = '\033[93m'  # yellow
        B = '\033[94m'  # blue
        R = '\033[91m'  # red
        W = '\033[0m'   # white

def no_color():
   global G,B,Y,R,W
   G=B=R=Y=W=''

if __name__=='__main__':
    specify_text_color()
    print(sys.platform.startswith('win'))