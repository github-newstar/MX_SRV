import grpc
from user_srv.proto import user_pb2_grpc, user_pb2


class UserTest:
    def __init__(self):
        channel = grpc.insecure_channel('localhost:1001')
        self.stub = user_pb2_grpc.UserStub(channel)
    def uesr_list(self):
        rsp = self.stub.GetUserList(user_pb2.PageInfo(pn=1, pSize=11))
        print(rsp.total)
        for user in rsp.data:
            print(user.mobile, user.birthday)
    

UserTest().uesr_list()