import string
def binarysearch(l, r, word):#二分搜敏感字詞
    if(l <= r):
        mid = (l+r)//2
        if (sen_words[mid] == word):
            return True
        elif (sen_words[mid] > word):
            return binarysearch(l, mid-1, word)
        elif (sen_words[mid] < word):
            return binarysearch(mid+1, r, word)
    else:
        return False
def rmv_pun(word):
    length = len(word)
    punct = string.punctuation
    for c in punct:
        word = word.replace(c, '')
    return word
    
f_sen = open("name.txt", 'r')

sen_words = f_sen.read().split('\n')
sen_words.pop()#移除最後一個空白元素
sen_words.sort()#方便二分搜
Num = len(sen_words)#要屏蔽的文字

while(1):
    messenge_in = input("Enter the messenge: ")
    words_in = messenge_in.split()
    length = len(messenge_in)
    word_head_lst = []
    if(messenge_in[0].isalnum()):
        word_head_lst.append(0)
    for i in range(length):#將輸入切成多個單字
        if (messenge_in[i] == ' '):
            while((not messenge_in[i].isalnum()) and i != length - 1):
                i += 1
            word_head_lst.append(i)
    words_num = len(words_in)
    messenge_split = list(messenge_in)
    for i in range(words_num):#移除標點符號
        words_in[i] = rmv_pun(words_in[i])
    for i in range(words_num):
        judge = binarysearch(0, Num - 1, words_in[i].lower())
        if(judge):
            if(i != words_num - 1):
                for j in range(word_head_lst[i], word_head_lst[i+1] - 1):
                    if(not messenge_split[j].isalnum()):
                        break
                    messenge_split[j] = '*'
            else:
                for j in range(word_head_lst[i], length):
                    if(not messenge_split[j].isalnum()):
                        break
                    messenge_split[j] = '*'
    messenge_out = ''.join(messenge_split)
    print(messenge_out)
                    
            
    
            
    
        
