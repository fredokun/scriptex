'''
Default Pre-markup rules

Created on 27 déc. 2012

@author: F.Peschanski
'''

from .lexer import Token
from .preparser import PreTemplate
from .render import Render


def default_premarkup_rules(preparser):
    # _([^_\n]+)@{word}_ ==> \emph{${word}}
    emph = PreTemplate() \
            .when(Token.Char('_')) \
            .then(Token.Repeat(Token.CharNotIn('_', '\n'), minimum=1),
                  param="word") \
            .then(Token.Char('_')) \
            .render(Render.Text("\\emph{")) \
            .render(Render.Param('word'))  \
            .render(Render.Text("}"))  \

    preparser.template(emph)

    # *([^*\n])@{word}* ==> \strong{${word}}
    strong = PreTemplate() \
                .when(Token.Char('*')) \
                .then(Token.Repeat(Token.CharNotIn('*', '\n'), minimum=1),
                      param="word") \
                      .then(Token.Char('*')) \
                      .render(Render.Text("\\strong{")) \
                      .render(Render.Param('word'))  \
                      .render(Render.Text("}"))  \

    preparser.template(strong)
