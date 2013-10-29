単語 (Tango)
============

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


A programmable document processor.

The input documents are written in a mix of latex and markdown-inspired short cuts.

The main phases of the processor are:
 
 1. parsing: detect the overall structure of the document and eliminate common structural errors.
    This phase results in a structured but unprocessed document
 2. processing: generate a portable structured document from the predocument by interpreting the
    commands and environments, except for those that are handled specifically in backend generators.
 3. generating: produce an output document using a generator backend.

The two main generator backends are:

 1. a latex/PDF backend for printing and on-screen reading
 2. a HTML/CSS/Javascript backend for interactive web documents.

Tango is mostly developed to develop computer science courses
 as well as testable scientific papers ... but it might prove useful in other areas too.
 It might one day be useful for static site generation (Jekyll, DocPad, etc.).

