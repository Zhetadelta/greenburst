#!/usr/bin/env python3

#from slackclient import SlackClient
from slack import WebClient as SlackClient

import yaml
import logging

def send_msg_2_slack(msg):
    with open("config/conf.yaml", 'r') as stream:
        data_loaded = yaml.load(stream)
    TOKEN = data_loaded['slack']['bot_oauth']
    
    client = SlackClient(TOKEN)
    response = client.chat_postMessage(
      channel="CPAK5A4G2",
      text=msg
    )
    return response

def send_img_2_slack(img):
    with open("config/conf.yaml", 'r') as stream:
        data_loaded = yaml.load(stream)
    TOKEN = data_loaded['slack']['bot_oauth']
    
    client = SlackClient(TOKEN)
    attachments = [{"title": "", "image_url": img}]
    response = client.chat_postMessage(channel='CPAK5A4G2', text='',
                attachments=attachments)
    response2 = client.chat_postMessage(channel='C013W4P08MB', text='',
                attachments=attachments)
    return f"{response}\n{response2}"


if __name__ == "__main__":
    logger = logging.getLogger()
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=format)
    #respose = send_msg_2_slack("Hello from Python! :tada:")
    #logging.info(f'{respose}')
    response = send_img_2_slack('https://www.dropbox.com/scl/fi/rx5c6kn2jbaxdz2mopfqe/cand_tstart_60586.508384786939_tcand_426.2090000_dm_5454.92000_snr_10.30260.png?rlkey=3bvcyn05xwk5p52o4rhobi8uk&dl=1')
    logging.info(f"{response}")
