from pyfiglet import Figlet

def banner():
    bb = Figlet(font='slant')
    print(bb.renderText('baekseoheon\nweb fuzzer'))