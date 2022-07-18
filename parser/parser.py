import argparse
import logging
import sys
from datetime import datetime
from os.path import join, basename, normpath
from pathlib import Path
from typing import List, Tuple, Optional

import parse
from utils.utils import get_dir_files

sys.path.append("./")

USER_TAG = "[Bot]"
OTHERS_TAG = "[Human]"
INVALID_SEQUENCES = ("https", "www", "<Media omitted>")


def parse_line(line: str, datetime_format: str) -> Tuple[Optional[datetime], str, str]:
    timestamp, user, message = None, '', ''

    line = parse.parse("{date}, {time} - {user}: {message}", line)
    if line:
        message_datetime = f"{ line['date'] }, { line['time'] }"
        timestamp = datetime.strptime(message_datetime, datetime_format)
        user = line['user']
        message = line['message']
    return timestamp, user, message


def run(user_name: str,
        chats_path: str,
        output_path: str,
        time_format: str,
        delta_h_threshold: int,
        session_token: str = None):
    Path("./tmp").mkdir(parents=True, exist_ok=True)
    txt_files_name, txt_files_paths = get_dir_files(dir_path=chats_path, extension_filter=".txt")
    logging.info(f"Found {len(txt_files_paths)} txt files in `{chats_path}` folder: {txt_files_paths}")

    data = []
    for file_name, file_path in zip(txt_files_name, txt_files_paths):
        file_text_parsed = parse_chat(file_path, user_name, time_format, delta_h_threshold, session_token)
        data.extend(file_text_parsed)

    dataset_path = join(output_path, 'dataset.txt')
    save_text(data, dataset_path)


def has_invalid_sequence(text):
    for word in INVALID_SEQUENCES:
        if word in text:
            return True
    return False


def save_text(text_list: List[str], output_path: str):
    logging.info(f'Saving {output_path}')
    with open(output_path, "w", encoding='utf8') as f:
        f.writelines("\n".join(text_list))


def split_in_sessions(t_current, t_last, chat_text, delta_h_threshold, session_token):
    if session_token and t_current and t_last:
        delta_h = divmod((t_current - t_last).total_seconds(), 3600)[0]
        if delta_h >= delta_h_threshold:
            chat_text.append(session_token)


def parse_chat(file_path: str,
               user_name: str,
               datetime_format: str,
               delta_h_threshold: int,
               session_token: str = None) -> List[str]:
    chat_text = [session_token] if session_token else []

    with open(file_path, encoding='utf8') as f:
        lines = f.readlines()

        t_last = None
        for line in lines:

            t_current, user, text = parse_line(line, datetime_format)

            if user == '' or has_invalid_sequence(text):
                continue

            split_in_sessions(t_current, t_last, chat_text, delta_h_threshold, session_token)
            t_last = t_current

            user = USER_TAG if user == user_name else OTHERS_TAG
            chat_text.append(f"{user} {text}")
    return chat_text


def main(argv):
    parser = argparse.ArgumentParser(prog=argv[0])
    parser.add_argument('--user_name', type=str, required=True,
                        help="The whatsapp user name of User. It could be read on the WhatsApp raws data.")
    parser.add_argument('--chats_path', type=str, default="../data/raw/")
    parser.add_argument('--output_path', type=str, default="../data/parsed/")
    parser.add_argument('--session_token', type=str,
                        help="Add a 'session_token' after 'delta_h_threshold' hours"
                             "are elapsed between two messages. This allows splitting in sessions"
                             "one chat based on messages timing.")
    parser.add_argument("--delta_h_threshold", type=int, default=4,
                        help="Hours between two messages to before add 'session_token'")
    parser.add_argument("--time_format", type=str, default="%m/%d/%y, %H:%M",
                        help="The WhatsApp datetime format. The default is the Singapore format.")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args(argv[1:])
    loglevel = logging.DEBUG if args.verbose else logging.INFO
    process_name = basename(normpath(argv[0]))
    logging.basicConfig(format=f"[{process_name}][%(levelname)s]: %(message)s", level=loglevel, stream=sys.stdout)
    delattr(args, "verbose")
    run(**vars(args))


if __name__ == '__main__':
    main(sys.argv)
