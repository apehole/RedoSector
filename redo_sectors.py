"""
_*_ coding:utf-8 _*_
_*_ author:iron_huang _*_
_*_ blog:https://www.dvpos.com/ _*_
"""

import json
import socket
import itertools
import codecs

SECTOR_TICKET = " "  # lotus-miner sectors status [sectorID] 查看ticket
WORKER_DO_ADDR = "192.168.32.211"  # 执行任务worker的ip
WORKER_DO_PORT = 18101  # worker端口
GET_BASE_INFO_FROM_ADDR = "127.0.0.1"   # 本地启动一个测试集群，用于获取数据模板
GET_BASE_INFO_FROM_PORT = 18095  # 本地测试的端口
MODEL_MINER = 1000  # 本地测试miner号
MODEL_NUMBER = 4  # 本地测试sectorId
TODO_MINER = 1111  # 需要重做的miner
TODO_SECTOR_ID = 88888  # 需要重做的sectorID


class RPCClient(object):
    def __init__(self, addr, codec=json):
        self._socket = socket.create_connection(addr)
        self._id_iter = itertools.count()
        self._codec = codec

    def _message(self, name, *params):
        return dict(id=1,
                    params=list(params),
                    method=name)

    def call(self, name, *params):
        req = self._message(name, *params)
        id = req.get('id')

        """
        Golang Rpc 返回的Json格式
        type serverResponse struct {
        Id     *json.RawMessage `json:"id"`
        Result interface{}      `json:"result"`
        Error  interface{}      `json:"error"`
        }
        """

        mesg = self._codec.dumps(req).encode()
        # print(mesg)
        self._socket.sendall(mesg)

        # This will actually have to loop if resp is bigger
        resp = self._socket.recv(4096)
        resp = self._codec.loads(resp)

        if resp.get('id') != id:
            raise Exception("expected id=%s, received id=%s: %s"
                            % (id, resp.get('id'), resp.get('error')))

        if resp.get('error') is not None:
            raise Exception(resp.get('error'))

        return resp.get('result')


def close(self):
    self._socket.close()


def do_p1():
    rpc = RPCClient((GET_BASE_INFO_FROM_ADDR,GET_BASE_INFO_FROM_PORT))
    args = {'Miner': MODEL_MINER, 'Number': MODEL_NUMBER}
    back = rpc.call("MinerRpc.GetTaskInfo", args)
    back["SectorID"]["Miner"] = TODO_MINER
    back["SectorID"]["Number"] = TODO_SECTOR_ID
    back["SealProofType"] = 3
    back["CacheDirPath"] = "/mnt/nvmeraid/cache/s-t01289-82786"
    back["StagedSectorPath"] = "/mnt/data/lotuscache/empty_sector_34359738368"
    back["SealedSectorPath"] = "/mnt/nvmeraid/sealed/s-t01289-82786"
    back["Pieces"] = [{"Size": 34359738368,
                       "PieceCID": {
                           "/": "baga6ea4seaqao7s73y24kcutaosvacpdjgfe5pw76ooefnyqw4ynr3d2y6x2mpq"
                       }
                       }]
    # close(rpc)
    back["Ticket"] =codecs.decode(SECTOR_TICKET, 'hex')
    rpc2 = RPCClient((WORKER_DO_ADDR, WORKER_DO_PORT))
    rpc2.call("WorkerRpc.DoTask", back)

def do_p2():
    args = {'Miner': TODO_MINER, 'Number': TODO_SECTOR_ID}
    rpc2 = RPCClient((WORKER_DO_ADDR, WORKER_DO_PORT))
    aaa = rpc2.call("WorkerRpc.GetTaskInfo", args, {})
    aaa["TaskType"] = 'seal/v0/precommit/2'
    rpc2.call("WorkerRpc.DoTask", aaa)

if __name__ == '__main__':
    #  先执行完P1
    do_p1()
    # 等P1完成后再注销p1执行p2
    # do_p2()
