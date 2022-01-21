def usage():
    import sys
    
    print('%s' % sys.argv[0].center(40))
    print("Usage: %s -u [target_ip] -f [word_list]" % sys.argv[0])
    print("ex) %s -u www.victim.com -f wordlist.txt" % sys.argv[0])
    