'''module optparse

Parsing command and environment options.
'''

def parse_options(input, keysep='=', itemsep=','):
    opts = dict()
    i = 0
    parse_key = True
    current_key = ""
    current_value = ""
    while i < len(input):
        ch = input[i]
        if parse_key:
            # if parsing key
            if ch == keysep:
                # if next character is key separator
                if i+1 < len(input):
                    ch2 = input[i+1]                
                    if ch2 == keysep:
                        # if also following character is key separator
                        # put into the key name (protected character)
                        current_key += keysep
                        i += 2
                        continue # jump directly

                # parsing the key is over
                parse_key = False
                i += 1

            elif ch == itemsep or i+1 == len(input):
                # if next character is item separator
                if i+1 < len(input):
                    ch2 = input[i+1]
                    if ch2 == itemsep:
                        # protected item separator, put into key name
                        current_key += itemsep
                        i += 2
                        continue # jump directly
                    
                # this is a key-only entry
                if ch != itemsep:
                    current_key += ch
                opts[current_key] = current_key
                current_key = ""
                i += 1

            else:
                # any other character
                current_key += ch
                i += 1

        else:
            # in parse-value mode
            if ch == itemsep or i+1 == len(input):
                # if next character is item separator
                if i+1 < len(input):
                    ch2 = input[i+1]
                    if ch2 == itemsep:
                        # protected item separator, put into key name
                        current_value += itemsep
                        i += 2
                        continue # jump directly
                    
                # the entry is parsed
                if ch != itemsep:
                    current_value += ch
                opts[current_key] = current_value
                current_key = ""
                current_value = ""
                i += 1

            else:
                # any other character
                current_value += ch
                i += 1

    # end of while
    return opts
    
