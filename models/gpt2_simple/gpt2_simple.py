import sys
import yaml
import logging
import argparse
import gpt_2_simple as gpt2  # Memo: tf 1.x needed
from os import makedirs
from os.path import basename, normpath, join
from datetime import datetime

sys.path.append("./")  # needed 4 utils imports - created according to launcher
from pistoBot.utils.general_utils import my_init, load_yaml

MODEL_DIR = './models/trained/'
MODEL_NAME = '124M'
DATASET = ''
LEARNING_RATE = 0.0001
STEPS = 1500
PRINT_EVERY = 1
SAMPLE_EVERY = 300
SAVE_EVERY = 300
RESTORE_FROM = 'latest'


def train():
    # Initialization
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    run_name = f'GPT2-Simple-124M-{timestamp}'

    gpt2.download_gpt2(model_dir=MODEL_DIR, model_name=MODEL_NAME)

    sess = gpt2.start_tf_sess()

    gpt2.finetune(sess,
                  model_dir=MODEL_DIR,
                  model_name=MODEL_NAME,
                  run_name=run_name,
                  dataset=DATASET,
                  learning_rate=LEARNING_RATE,
                  restore_from=RESTORE_FROM,
                  print_every=PRINT_EVERY,
                  sample_every=SAMPLE_EVERY,
                  save_every=SAVE_EVERY)


def generate(prompt: str, temperature: float):
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess)
    text = gpt2.generate(sess,
                         model_dir=MODEL_DIR,
                         model_name=MODEL_NAME,
                         return_as_list=True)[0]
