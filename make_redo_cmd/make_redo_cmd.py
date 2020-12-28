import configparser
import requests
import base64
import os
import shutil
import re
from time import gmtime, strftime


def get_miner_post():
    config = configparser.ConfigParser()
    config.read("token.ini", encoding="utf-8")
    api = config.get('POST', 'API_MINER')
    token = config.get('POST', 'TOKEN_MINER')
    url = "http://" + eval(api) + "/rpc/v0"
    return url, eval(token)


def get_sectors_status(miner_url, miner_token, number):
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + miner_token}
    params = {
        "jsonrpc": "2.0",
        "method": "Filecoin.SectorsStatus",
        "id": 1,
        "params": [
            number,
            True
        ]
    }
    r = requests.post(miner_url, headers=headers, json=params)
    if r.status_code == 200:
        if ("error" in r.json()):
            return False
        result = r.json()["result"]
        return result

def print():
    # file1=open("/home/fqw/20201226faultsectors_sorted", "r+")
    file2=open("/home/fqw/sectorCmd.txt", "w+")
    miner_url, miner_token = get_miner_post()
    i=1
    with open('/home/fqw/20201226faultsectors_sorted', 'r') as f:
        for line in f:
            number=int(line)
            sectorStatus=get_sectors_status(miner_url, miner_token, number)
            if not sectorStatus is None:
                sealProofType=sectorStatus["SealProof"]
                ticket=sectorStatus["Ticket"]["Value"]
                if number >=0:
                    if (i%2)==0:
                        cmd="lotus-scheduler add-redo-task --sealProofType "+str(sealProofType)+" --minerID "+"54267"+" --sectorNumber "+str(number)+" --ticketBase64 "+str(ticket)+" --minerSealedDir /mnt/data/data_nfs4/sealed --minerCacheDir /mnt/data/data_nfs4/cache"
                    else:
                        cmd="lotus-scheduler add-redo-task --sealProofType "+str(sealProofType)+" --minerID "+"54267"+" --sectorNumber "+str(number)+" --ticketBase64 "+str(ticket)+" --minerSealedDir /mnt/data/data_nfs5/sealed --minerCacheDir /mnt/data/data_nfs5/cache"
                    file2.writelines(cmd + '\n')
                    i+=1
    f.close()
    file2.close()

if __name__ == '__main__':
    print()