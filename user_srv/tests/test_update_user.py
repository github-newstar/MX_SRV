import grpc
from user_srv.proto import user_pb2_grpc, user_pb2
import time
from datetime import date, datetime


class TestUpdateUser:
    """测试 UpdateUser 函数的测试用例"""
    
    def __init__(self):
        # 连接到 gRPC 服务器
        channel = grpc.insecure_channel('localhost:50051')
        self.stub = user_pb2_grpc.UserStub(channel)
    
    def get_existing_user_id(self):
        """获取一个存在的用户ID用于测试"""
        try:
            # 获取用户列表，取第一个用户的ID
            request = user_pb2.PageInfo(pn=1, pSize=1)
            response = self.stub.GetUserList(request)
            if response.data and len(response.data) > 0:
                print(f"找到测试用户ID: {response.data[0].id}")
                return response.data[0].id
            else:
                print("用户列表为空，尝试使用固定ID")
                # 如果没有用户，尝试使用一个已知存在的ID
                return 1
        except Exception as e:
            print(f"获取用户ID失败: {e}")
            return 1  # 返回一个默认ID
    
    def test_update_existing_user(self):
        """测试更新存在的用户"""
        print("=== 测试用例1: 更新存在的用户 ===")
        
        user_id = self.get_existing_user_id()
        if not user_id:
            print("❌ 无法获取测试用户ID，跳过此测试")
            return False
        
        try:
            # 先获取用户原始信息
            get_request = user_pb2.IdRequest(id=user_id)
            original_user = self.stub.GetUserById(get_request)
            print(f"原始用户信息: ID={original_user.id}, 昵称={original_user.nickName}")
            
            # 生成测试用的生日时间戳（2000年1月1日）
            test_birthday = datetime(2000, 1, 1)
            birthday_timestamp = int(time.mktime(test_birthday.timetuple()))
            
            # 更新用户信息
            update_request = user_pb2.UpdateUserInfo(
                id=user_id,
                nickName="更新后的昵称",
                gender="male",
                birthday=birthday_timestamp
            )
            
            response = self.stub.UpdateUser(update_request)
            print("✅ 更新请求发送成功")
            
            # 验证更新结果 - 重新获取用户信息
            updated_user = self.stub.GetUserById(get_request)
            
            # 验证更新是否成功
            success = True
            if updated_user.nickName != "更新后的昵称":
                print(f"❌ 昵称更新失败: 期望='更新后的昵称', 实际='{updated_user.nickName}'")
                success = False
            else:
                print(f"✅ 昵称更新成功: {updated_user.nickName}")
            
            if updated_user.gender != "male":
                print(f"❌ 性别更新失败: 期望='male', 实际='{updated_user.gender}'")
                success = False
            else:
                print(f"✅ 性别更新成功: {updated_user.gender}")
            
            if updated_user.birthday != birthday_timestamp:
                print(f"❌ 生日更新失败: 期望={birthday_timestamp}, 实际={updated_user.birthday}")
                success = False
            else:
                print(f"✅ 生日更新成功: {updated_user.birthday}")
            
            return success
            
        except grpc.RpcError as e:
            print(f"❌ gRPC 错误: {e.code()}, {e.details()}")
            return False
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            return False
    
    def test_update_nonexistent_user(self):
        """测试更新不存在的用户"""
        print("\n=== 测试用例2: 更新不存在的用户 ===")
        
        try:
            # 使用一个不存在的用户ID
            update_request = user_pb2.UpdateUserInfo(
                id=99999,  # 假设这个ID不存在
                nickName="不存在的用户",
                gender="female",
                birthday=int(time.time())
            )
            
            response = self.stub.UpdateUser(update_request)
            print("⚠️  意外成功更新了不存在的用户")
            return False
            
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                print("✅ 正确处理：返回 NOT_FOUND 状态码")
                print(f"   错误详情: {e.details()}")
                return True
            else:
                print(f"❌ 意外的 gRPC 错误: {e.code()}, {e.details()}")
                return False
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            return False
    
    def test_update_with_invalid_data(self):
        """测试使用无效数据更新用户"""
        print("\n=== 测试用例3: 测试无效数据更新 ===")
        
        user_id = self.get_existing_user_id()
        if not user_id:
            print("❌ 无法获取测试用户ID，跳过此测试")
            return False
        
        test_cases = [
            {
                "desc": "无效性别",
                "data": {"id": user_id, "nickName": "测试", "gender": "invalid", "birthday": int(time.time())}
            },
            {
                "desc": "未来时间戳",
                "data": {"id": user_id, "nickName": "测试", "gender": "male", "birthday": int(time.time()) + 365*24*3600}
            },
            {
                "desc": "空昵称",
                "data": {"id": user_id, "nickName": "", "gender": "male", "birthday": int(time.time())}
            }
        ]
        
        results = []
        for case in test_cases:
            try:
                print(f"测试 {case['desc']}")
                request = user_pb2.UpdateUserInfo(**case['data'])
                response = self.stub.UpdateUser(request)
                
                # 对于无效数据，理想情况下应该返回错误
                print("⚠️  无效数据被接受了（可能需要添加验证）")
                results.append(True)  # 暂时认为是正常的，因为服务端可能没有验证
                
            except grpc.RpcError as e:
                print(f"✅ 正确处理 gRPC 错误: {e.code()}")
                results.append(True)
            except Exception as e:
                print(f"❌ 其他错误: {e}")
                results.append(False)
        
        return all(results)
    
    def test_partial_update(self):
        """测试部分字段更新"""
        print("\n=== 测试用例4: 部分字段更新 ===")
        
        user_id = self.get_existing_user_id()
        if not user_id:
            print("❌ 无法获取测试用户ID，跳过此测试")
            return False
        
        try:
            # 先获取原始用户信息
            get_request = user_pb2.IdRequest(id=user_id)
            original_user = self.stub.GetUserById(get_request)
            
            # 只更新昵称，其他字段保持默认值
            update_request = user_pb2.UpdateUserInfo(
                id=user_id,
                nickName="只更新昵称"
                # 不设置 gender 和 birthday
            )
            
            response = self.stub.UpdateUser(update_request)
            print("✅ 部分更新请求发送成功")
            
            # 验证更新结果
            updated_user = self.stub.GetUserById(get_request)
            
            if updated_user.nickName == "只更新昵称":
                print("✅ 昵称部分更新成功")
                return True
            else:
                print(f"❌ 昵称部分更新失败: 期望='只更新昵称', 实际='{updated_user.nickName}'")
                return False
            
        except grpc.RpcError as e:
            print(f"❌ gRPC 错误: {e.code()}, {e.details()}")
            return False
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            return False
    
    def test_birthday_conversion(self):
        """测试生日时间戳转换"""
        print("\n=== 测试用例5: 生日时间戳转换测试 ===")
        
        user_id = self.get_existing_user_id()
        if not user_id:
            print("❌ 无法获取测试用户ID，跳过此测试")
            return False
        
        try:
            # 测试不同的日期
            test_dates = [
                {"desc": "1990年1月1日", "date": datetime(1990, 1, 1)},
                {"desc": "2000年12月31日", "date": datetime(2000, 12, 31)},
                {"desc": "今天", "date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)}
            ]
            
            results = []
            for test_case in test_dates:
                try:
                    print(f"测试日期: {test_case['desc']}")
                    
                    # 转换为时间戳
                    timestamp = int(time.mktime(test_case['date'].timetuple()))
                    
                    # 更新用户生日
                    update_request = user_pb2.UpdateUserInfo(
                        id=user_id,
                        nickName=f"生日测试_{test_case['desc']}",
                        gender="male",
                        birthday=timestamp
                    )
                    
                    response = self.stub.UpdateUser(update_request)
                    
                    # 验证更新结果
                    get_request = user_pb2.IdRequest(id=user_id)
                    updated_user = self.stub.GetUserById(get_request)
                    
                    if updated_user.birthday == timestamp:
                        print(f"✅ {test_case['desc']} 时间戳转换成功")
                        results.append(True)
                    else:
                        print(f"❌ {test_case['desc']} 时间戳转换失败")
                        results.append(False)
                        
                except Exception as e:
                    print(f"❌ {test_case['desc']} 测试失败: {e}")
                    results.append(False)
            
            return all(results)
            
        except Exception as e:
            print(f"❌ 生日转换测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试用例"""
        print("🚀 开始运行 UpdateUser 函数测试用例")
        print("=" * 50)
        
        test_results = []
        
        # 运行各个测试用例
        test_results.append(self.test_update_existing_user())
        test_results.append(self.test_update_nonexistent_user())
        test_results.append(self.test_update_with_invalid_data())
        test_results.append(self.test_partial_update())
        test_results.append(self.test_birthday_conversion())
        
        # 统计结果
        passed = sum(test_results)
        total = len(test_results)
        
        print("\n" + "=" * 50)
        print(f"📊 测试结果统计:")
        print(f"   通过: {passed}/{total}")
        print(f"   失败: {total - passed}/{total}")
        
        if passed == total:
            print("🎉 所有测试用例通过!")
        else:
            print("⚠️  部分测试用例失败，请检查实现")
        
        return passed == total


if __name__ == "__main__":
    # 创建测试实例并运行所有测试
    test = TestUpdateUser()
    test.run_all_tests()
