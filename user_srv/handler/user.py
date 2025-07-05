from user_srv.model.models import User
from peewee import DoesNotExist
import grpc
from user_srv.proto import user_pb2_grpc, user_pb2
from loguru import logger
import time

class UserServicer(user_pb2_grpc.UserServicer):
    def convUserToRsp(self, user):
        rsp = user_pb2.UserInfoResponse()
        
        user_info_rsp = user_pb2.UserInfoResponse()
        
        user_info_rsp.id = user.id
        user_info_rsp.mobile = user.mobile
        user_info_rsp.role = user.role
        if user.nick_name:
            user_info_rsp.nickName =user.nick_name
        if user.gender:
            user_info_rsp.gender = user.gender
        if user.birthday:
            user_info_rsp.birthday = int(time.mktime(user.birthday.timetuple()))
        
        return user_info_rsp
    @logger.catch
    def GetUserList(self, request , context):
        rsp = user_pb2.UserListResponse()
        
        users = User.select()
        rsp.total = users.count()
        
        start = 0
        per_page_numbers = 10
        if request.pSize:
            per_page_numbers = request.pSize
        if request.pn:
            start = per_page_numbers * (request.pn - 1)
        users = users.offset(start).limit(per_page_numbers)
        for user in users:
            user_info_rsp = self.convUserToRsp(user)
            rsp.data.append(user_info_rsp)
        
        return rsp
    @logger.catch
    def GetUserById(self, request, context):
        try:
            user = User.get(User.id == request.id)
            return self.convUserToRsp(user)
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User not found')
            return user_pb2.UserInfoResponse()

    @logger.catch
    def GetUserByMobile(self, request, context):
        try:
            user = User.get(User.mobile == request.mobile)
            return self.convUserToRsp(user)
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User not found')
            return user_pb2.UserInfoResponse()


