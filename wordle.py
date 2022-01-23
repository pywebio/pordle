from pywebio.output import *
from pywebio.session import run_js
from pywebio import session, start_server, config
import time

WORD_LEN = 5
MAX_TRY = 6

TODAY_WORD = 'HAPPY'  # need be upper

assert len(TODAY_WORD) == WORD_LEN

CSS = """
.pywebio {padding-top: 0} .markdown-body table {display:table; width:250px; margin:10px auto;}
.markdown-body table th, .markdown-body table td {font-weight:bold; padding:0; line-height:50px;}
th>div,td>div {width:50px; height:50px}.btn-light {background-color:#d3d6da;}
@media (max-width: 435px) {.btn{padding:0.375rem 0.5rem;}}
@media (max-width: 355px) {.btn{padding:0.375rem 0.4rem;}}
"""


def is_word(s):  # todo: implement this function
    return 'X' not in s


def on_key_press(char):
    if session.local.curr_row >= MAX_TRY or session.local.game_pass:
        return

    # show the char in grid
    with use_scope(f's-{session.local.curr_row}-{len(session.local.curr_word)}', clear=True):
        put_text(char)

    session.local.curr_word += char
    if len(session.local.curr_word) == WORD_LEN:  # submit a word guess
        if not is_word(session.local.curr_word):
            toast('Not in word list!', color='error')
            session.local.curr_word = ''
            for i in range(WORD_LEN):
                with use_scope(f's-{session.local.curr_row}-{i}', clear=True): put_text(' ', inline=True)
        else:
            for idx, c in enumerate(session.local.curr_word):
                time.sleep(0.2)
                if TODAY_WORD[idx] == c:
                    session.local.green_chars.add(c)
                    run_js('$("button:contains(%s)").css({"background-color":"#6aaa64", "color":"white"})' % c)
                    text_bg = '#6aaa64'
                    session.local.game_result += '🟩'
                elif c in TODAY_WORD:
                    text_bg = '#c9b458'
                    session.local.game_result += '🟨'
                    if c not in session.local.green_chars:
                        run_js('$("button:contains(%s)").css({"background-color":"#c9b458", "color":"white"})' % c)
                else:
                    text_bg = '#787c7e'
                    session.local.game_result += '⬜'
                    run_js('$("button:contains(%s)").css({"background-color":"#787c7e", "color":"white"})' % c)

                with use_scope(f's-{session.local.curr_row}-{idx}', clear=True):
                    put_text(c).style(f'color:white;background:{text_bg}')

            session.local.game_result += '\n'
            if session.local.curr_word == TODAY_WORD:
                toast('Genius', color='success')
                session.local.game_pass = True

            session.local.curr_row += 1
            session.local.curr_word = ''

        if session.local.game_pass:
            message = f'Wordle {session.local.curr_row}/{MAX_TRY}\n\n' + session.local.game_result
            popup("Game Result", put_text(message).style('text-align: center'), size='small')


@config(title="Wordle - A daily word game", description="A PyWebIO implementation", css_style=CSS)
def main():
    put_markdown('# WORDLE').style('text-align:center')

    grid = [
        [put_scope(f's-{x}-{y}', content=put_text(' ')) for y in range(WORD_LEN)]
        for x in range(MAX_TRY)
    ]
    put_table(grid).style('text-align: center')

    keyboard = [
        put_buttons([dict(label=c, value=c, color='light') for c in keys], on_key_press, serial_mode=True)
        for keys in ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM']
    ]
    put_column(keyboard).style('text-align: center')

    session.local.curr_row = 0
    session.local.curr_word = ''
    session.local.green_chars = set()
    session.local.game_pass = False
    session.local.game_result = ''


if __name__ == '__main__':
    start_server(main, port=8080, debug=True, remote_access=True)
