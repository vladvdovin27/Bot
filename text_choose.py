from random import choice


def preprocess_symbols(text):
    lines = text.split('\n')
    new_text = ''
    for line in lines:
        lst = line.split()
        symbols = '!.,:;?'
        for elm in lst:
            if elm[0] in symbols:
                new_text += elm
            else:
                new_text += ' ' + elm
        new_text += '\n'

    return new_text


def preprocess_text(text):
    if '{' in text:
        new_text = []
        check_choose = False
        word = ''
        new_sentence = []
        choose_text = ''
        for symbol in text:
            if check_choose:
                choose_text += symbol
                if symbol == '}':
                    check_choose = False
                    variant = choose(choose_text)
                    choose_text = ''
                    new_sentence.append(variant)
            else:
                if symbol == '{':
                    check_choose = True
                    choose_text += symbol
                elif symbol == ' ':
                    new_sentence.append(word)
                    word = ''
                elif symbol == '.':
                    new_sentence.append(word)
                    new_text.append(' '.join(new_sentence))
                    new_sentence.clear()
                else:
                    word += symbol

        return preprocess_symbols('.'.join(new_text))

    else:
        return text


def count(text, symbol):
    res = []
    for i in range(len(text)):
        if text[i] == symbol:
            res.append(i)

    return res


def choose(choose):
    start, end = count(choose, '{'), count(choose, '}')
    res = ''
    for i in range(len(start)):
        curr_choose = choose[start[i] + 1:end[i]]
        res += choice(curr_choose.split('|'))

    return res if end[-1] + 1 != len(choose) else res + choose[end[-1] + 1:]
