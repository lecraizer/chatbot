def beforeTag(tag, frase):
    if hasTag(tag,frase):
        tagIni = frase.find(tag)
        frase = frase[0:tagIni]
    return frase  
            

def hasTag(tag, frase):
    if tag in frase :
        return True
    return False
   

def removeTag(tag, frase):
    if hasTag(tag,frase):
        tagIni = frase.find(tag)
        content = frase[tagIni + len(tag):len(frase)]
        return content
    return frase

        
def getTagContent(tag, frase, optToken = "♫"):
    if hasTag(tag,frase):
        content = removeTag(tag, frase)
        content = content.split(optToken)
        return content
    return frase