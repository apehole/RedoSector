import os
import requests
import copy

BASE_CACHE_PATH1 = "/mnt/nvme1/cache"
BASE_CACHE_PATH2 = "/mnt/nvmeraid/cache"
BASE_SEALED_PATH1 = "/mnt/nvme1/sealed"
BASE_SEALED_PATH2 = "/mnt/nvmeraid/sealed"
API_URL = ""
BASE_WORKER_URL1 = ""
BASE_WORKER_URL2 = ""
MINER_NUMBER = 54267
TODO_LIST1 = [4808, 4979, 4816, 4805]
TODO_LIST2 = [4820, 4818]

P1_Model = {
    "jsonrpc": "2.0",
    "params": [
        {
            "SectorID": {
                "Miner": 54267,
                "Number": 2354
            },
            "TaskType": "seal/v0/precommit/1",
            "SealProofType": 8,
            "CacheDirPath": "",
            "StagedSectorPath": "/mnt/data/lotuscache/empty_sector_34359738368",
            "SealedSectorPath": "",
            "Ticket": "",
            "Seed": None,
            "Pieces": [
                {
                    "Size": 34359738368,
                    "PieceCID": {
                        "/": "baga6ea4seaqao7s73y24kcutaosvacpdjgfe5pw76ooefnyqw4ynr3d2y6x2mpq"
                    }
                }
            ],
            "PreCommit1Out": "",
            "PreCommit2Out": {
                "Unsealed": None,
                "Sealed": None
            },
            "Commit1Out": None,
            "Commit2Out": None,
            "Finalized": False,
            "ErrMsg": ""
        }
    ],
    "method": "WorkerJsonRpc.DoTask",
    "id": 1
}


def make_ticket_params(sector_id):
    return {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "Filecoin.SectorsStatus",
        "params": [sector_id, False]
    }


def make_p2_params(sector_id):
    return {
        "jsonrpc": "2.0",
        "params": [{"Miner": MINER_NUMBER, "Number": sector_id}],
        "method": "WorkerJsonRpc.GetTaskInfo",
        "id": 1
    }


def do_p1(base_url, sector_id, worker_port, base_cache_path, base_sealed_path):
    cache_path = os.path.join(base_cache_path, f"s-t0{MINER_NUMBER}-{sector_id}")
    sealed_path = os.path.join(base_sealed_path, f"s-t0{MINER_NUMBER}-{sector_id}")

    back = requests.post(API_URL, json=make_ticket_params(sector_id))
    ticket = back.json()["result"]["Ticket"]["Value"]
    p1_task_info = copy.deepcopy(P1_Model)
    p1_task_info["params"][0]["CacheDirPath"] = cache_path
    p1_task_info["params"][0]["SealedSectorPath"] = sealed_path
    p1_task_info["params"][0]["Ticket"] = ticket
    p1_task_info["params"][0]["SectorID"]["Miner"] = MINER_NUMBER
    p1_task_info["params"][0]["SectorID"]["Number"] = sector_id

    worker_url = f"{base_url}:{worker_port}"

    post = requests.post(worker_url, json=p1_task_info)
    if post.status_code == 200 and post.json()["result"] == "ok":
        print(f"{sector_id} ok")
    else:
        print(f"{sector_id} failed")


def do_p2(base_url, worker_port, sector_id, base_cache_path, base_sealed_path):
    cache_path = os.path.join(base_cache_path, f"s-t0{MINER_NUMBER}-{sector_id}")
    sealed_path = os.path.join(base_sealed_path, f"s-t0{MINER_NUMBER}-{sector_id}")

    worker_url = f"{base_url}:{worker_port}"
    back = requests.post(worker_url, json=make_p2_params(sector_id))
    p1_out = back.json()["result"]["Task"]["PreCommit1Out"]
    if p1_out == "":
        return f"{sector_id} get PreCommit1Out failed"
    else:
        back = requests.post(API_URL, json=make_ticket_params(sector_id))
        ticket = back.json()["result"]["Ticket"]["Value"]
        p2_task_info = copy.deepcopy(P1_Model)
        p2_task_info["params"][0]["TaskType"] = "seal/v0/precommit/2"
        p2_task_info["params"][0]["CacheDirPath"] = cache_path
        p2_task_info["params"][0]["SealedSectorPath"] = sealed_path
        p2_task_info["params"][0]["Ticket"] = ticket
        p2_task_info["params"][0]["SectorID"]["Miner"] = MINER_NUMBER
        p2_task_info["params"][0]["SectorID"]["Number"] = sector_id
        p2_task_info["params"][0]["PreCommit1Out"] = p1_out
        post = requests.post(worker_url, json=p2_task_info)
        if post.status_code == 200 and post.json()["result"] == "ok":
           return ""
        else:
            return f"{sector_id} p2 failed"


if __name__ == '__main__':
# for idx, sectorId in enumerate(TODO_LIST1):
#     port = str(18101 + idx)
#     do_p1(BASE_WORKER_URL1, sectorId, port, BASE_CACHE_PATH1, BASE_SEALED_PATH1)
# for idx, sectorId in enumerate(TODO_LIST2):
#     port = str(18101 + idx)
#     do_p1(BASE_WORKER_URL2, sectorId, port, BASE_CACHE_PATH2, BASE_SEALED_PATH2)
    part_1_ok = True
    for idx, sectorId in enumerate(TODO_LIST1):
        port = str(18105 + idx)
        info = do_p2(BASE_WORKER_URL1, port, sectorId, BASE_CACHE_PATH1, BASE_SEALED_PATH1)
        if info != "":
            print(info)
            part_1_ok = False
            break
        else:
            print(f"{sectorId} ok")
    # if part_1_ok:
    #     for idx, sectorId in enumerate(TODO_LIST2):
    #         port = str(18101 + idx)
    #         info = do_p2(BASE_WORKER_URL2, port, sectorId, BASE_CACHE_PATH2, BASE_SEALED_PATH2)
    #         if info != "":
    #             print(info)
    #             break
    #         else:
    #             print(f"{sectorId} ok")
    # else:
    #     print("error")
