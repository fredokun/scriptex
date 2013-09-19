
# the Tango frontend

import argparse

def tangoArgumentParser():
    parser = argparse.ArgumentParser(prog="tango", description="a programmable document processor")

    parser.add_argument("--banner", help="show nice banner", action="store_true")
    return parser
    

def tangoBanner():
    return \
r"""

                         .~""~.,--.       TANGO                       |
                          > :::i_, ~;                                 |
              mmn        <, ?::j~?`_{}          a Programmable        |
              (_)         l_  fl_ f {}                                |
               \ `.     ,__}--{_/_l___.      Document                 |
                \  `--~'           `m,_`.                             |
                 \                      )}           Processor        |
                  `~----f     i  :-----~'                             |
                        }     |  |-'/                                 |
________________________|     !  | f__________________________________!
                        l        j |                                   \
                        }==I===I={~(                                    \
                        f.       1( )                                    \
                        |      } }` `.                                    \
                        |     '  { ) )                                     \
                        }    f   |(  `\                                     \
                        |    |   |  )  )
                        |    |   |.  ( `.
                        |    |  ,l ) `. )
                       /{    |    \   ( `\
                      ('|    |\    \ ; `. )
                     (;!|    |`\    \  ',' )
                      YX|    |XX\    \XXXXXY
                        !____j_) \__,'> _)         (C) 2013 Frederic Peschanski
                     ,_.'`--('Y,_' ,^' /`!               
                     L___-__J  L_,'`--'     mab'95

"""


if __name__ == "__main__":


    arg_parser = tangoArgumentParser()
    args = arg_parser.parse_args()

    if args.banner:
        print(tangoBanner())


    print("... bye bye ... (for now)")

