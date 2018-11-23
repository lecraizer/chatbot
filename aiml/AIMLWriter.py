def DumpParser(file, p, flag, current, pattern, topicpattern):
    if isinstance(p, dict):
        for (key, info) in p.items():
            if isinstance(key, str):
                if pattern == '': pat = key
                else: pat = pattern + " " + key
                DumpParser(file, info, flag, current, pat, topicpattern)
            elif isinstance(key, int):
                if key == 0:
                    if pattern == '': pat = "_"
                    else: pat = pattern + " _"
                    DumpParser(file, info, flag, current, pat, topicpattern)
                if key == 1 and flag == 0:
                    if pattern == '': pat = "*"
                    else: pat = pattern + " *"
                    DumpParser(file, info, flag, current, pat, topicpattern)
                elif key == 1:
                    DumpParser(file, info, flag, current, pattern, topicpattern)
                elif key == 2:
                    cur = current + "\t<template>\n\t\t"
                    DumpParser(file, info, flag, cur, '', pattern)
                elif key == 3:
                    cur = "<category>\n\t<pattern>" + pattern + "</pattern>\n"
                    DumpParser(file, info, 1, cur, '', topicpattern)
                elif key == 4:
                    cur = current
                    if pattern != '':
                        cur = current + "\t<that>" + pattern + "</that>\n"
                    DumpParser(file, info, flag, cur, '', topicpattern)
    elif isinstance(p, (frozenset, list, set, tuple)):
        template = ''
        for tup in p:
            if isinstance(tup, (frozenset, list, set, tuple)):
                if tup[0] == 'text': template += tup[2]
                elif tup[0] == 'srai':
                    template += "<srai>"
                    for t in tup:
                        if isinstance(t, (frozenset, list, set, tuple)):
                            if t[0] == 'text': template += t[2]
                            elif t[0] == 'star':
                                if t[1] == {}: template += "<star/>"
                                else: template += "<star index ='" + t[1]['index'] + "'/>"
                    template += "</srai>\n"
                elif tup[0] == 'star':
                    if tup[1] == {}: template += '<star/>'
                    else: template += "<star index ='" + tup[1]['index'] + "'/>"
                elif tup[0] == 'think':
                    template += "<think>"
                    for t in tup:
                        if isinstance (t, (frozenset, list, set, tuple)):
                            if t[0] == 'text': template += t[2]
                            elif t[0] == 'star':
                                if t[1] == {}: template += '<star/>'
                                else: template += "<star index ='" + t[1]['index'] + "'/>"
                            elif t[0] == 'set':
                                template += "<set name ='" + t[1]['name'] + "'>"
                                for t2 in t:
                                    if isinstance (t2, (frozenset, list, set, tuple)):
                                        if t2[0] == 'text': template += t2[2]
                                        elif t2[0] == 'star':
                                            if t2[1] == {}: template += '<star/>'
                                            else: template += "<star index ='" + t2[1]['index'] + "'/>"
                                        elif t2[0] == 'get':
                                            template += "<get name ='" + t[1]['name'] + "'/>"
                                template += "</set>"                       
                            elif t[0] == 'get':
                                template += "<get name ='" + t[1]['name'] + "'/>"
                    template += '</think>'
                elif tup[0] == 'set':
                    template += "<set name ='" + t[1]['name'] + "'>"
                    for t in tup:
                        if isinstance (t, (frozenset, list, set, tuple)):
                            if t[0] == 'text': template += t[2]
                            elif t[0] == 'star':
                                if t[1] == {}: template += '<star/>'
                                else: template += "<star index ='" + t[1]['index'] + "'/>"
                            elif t[0] == 'get':
                                template += "<get name ='" + t[1]['name'] + "'/>"
                    template += "</set>"   
                elif tup[0] == 'get':
                    template += "<get name ='" + tup[1]['name'] + "'/>"
                elif tup[0] == 'learn':
                    template += "<learn>" + tup[2][2] + "</learn>"
                elif tup[0] == 'random':
                    template += "<random>\n"
                    for t in tup:
                        if isinstance(t, (frozenset, list, set, tuple)):
                            if t[0] == 'li':
                                template += '\t\t\t<li>'
                                for t2 in t:
                                    if isinstance (t2, (frozenset, list, set, tuple)):
                                        if t2[0] == 'text': template += t2[2]
                                        elif t2[0] == 'star':
                                            if t2[1] == {}: template += '<star/>'
                                            else: template += "<star index ='" + t2[1]['index'] + "'/>"
                                        elif t2[0] == "set":
                                            template += "<set name ='" + t[1]['name'] + "'>"
                                            for t3 in t2:
                                                if isinstance (t3, (frozenset, list, set, tuple)):
                                                    if t3[0] == 'text': template += t3[2]
                                                    elif t3[0] == 'star':
                                                        if t3[1] == {}: template += '<star/>'
                                                        else: template += "<star index ='" + t3[1]['index'] + "'/>"
                                                    elif t3[0] == 'get':
                                                        template += "<get name ='" + t3[1]['name'] + "'/>"
                                            template += "</set>"
                                        elif t2[0] == 'get':
                                            template += "<get name ='" + t[1]['name'] + "'/>"
                                template += "</li>\n"    
                    template += "\t\t</random>"
        
        cur = current + template + "\n\t</template>\n</category>\n\n"
        if topicpattern != '':
            cur = "<topic name ='" + topicpattern + "'>\n\n" + cur + "</topic>\n\n"
        file.write(cur)

def WriteAIML(root):
    with open("saida.txt", "a+") as f:
        f.write('<?xml version="1.0" encoding="Latin-1"?>\n<aiml version="1.0.1">\n\n')
        DumpParser(f, root, 0, '', '', '')
        f.write('\n</aiml>')
        