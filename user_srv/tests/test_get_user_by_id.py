import grpc
from user_srv.proto import user_pb2_grpc, user_pb2


class TestGetUserById:
    """测试 GetUserById 函数的测试用例"""
    
    def __init__(self):
        # 连接到 gRPC 服务器
        channel = grpc.insecure_channel('localhost:50051')
        self.stub = user_pb2_grpc.UserStub(channel)
    
    def test_get_existing_user(self):
        """测试获取存在的用户"""
        print("=== 测试用例1: 获取存在的用户 ===")
        
        try:
            # 创建请求，获取ID为1的用户
            request = user_pb2.IdRequest(id=1)
            response = self.stub.GetUserById(request)
            
            # 验证响应
            if response.id:
                print(f"✅ 成功获取用户:")
                print(f"   用户ID: {response.id}")
                print(f"   昵称: {response.nickName}")
                print(f"   手机号: {response.mobile}")
                print(f"   性别: {response.gender}")
                print(f"   角色: {response.role}")
                if response.birthday:
                    print(f"   生日时间戳: {response.birthday}")
                return True
            else:
                print("❌ 测试失败: 未找到用户")
                return False
                
        except grpc.RpcError as e:
            print(f"❌ gRPC 错误: {e.code()}, {e.details()}")
            return False
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            return False
    
    def test_get_nonexistent_user(self):
        """测试获取不存在的用户"""
        print("\n=== 测试用例2: 获取不存在的用户 ===")
        
        try:
            # 创建请求，获取ID为999的用户（假设不存在）
            request = user_pb2.IdRequest(id=999)
            response = self.stub.GetUserById(request)
            
            # 验证响应
            if response.id:
                print(f"⚠️  意外获取到用户: ID={response.id}")
                return False
            else:
                print("✅ 正确处理：未找到用户，返回空响应")
                return True
                
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                print("✅ 正确处理：返回 NOT_FOUND 状态码")
                return True
            else:
                print(f"❌ 意外的 gRPC 错误: {e.code()}, {e.details()}")
                return False
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            return False
    
    def test_get_user_with_invalid_id(self):
        """测试使用无效ID获取用户"""
        print("\n=== 测试用例3: 测试无效ID ===")
        
        test_cases = [
            {"id": -1, "desc": "负数ID"},
            {"id": 0, "desc": "零ID"},
        ]
        
        results = []
        for case in test_cases:
            try:
                print(f"测试 {case['desc']} (ID={case['id']})")
                request = user_pb2.IdRequest(id=case['id'])
                response = self.stub.GetUserById(request)
                
                if response.id:
                    print(f"⚠️  意外获取到用户: ID={response.id}")
                    results.append(False)
                else:
                    print("✅ 正确处理：无效ID返回空响应")
                    results.append(True)
                    
            except grpc.RpcError as e:
                print(f"✅ 正确处理 gRPC 错误: {e.code()}")
                results.append(True)
            except Exception as e:
                print(f"❌ 其他错误: {e}")
                results.append(False)
        
        return all(results)
    
    def test_multiple_users(self):
        """测试获取多个用户"""
        print("\n=== 测试用例4: 批量测试多个用户ID ===")
        
        # 测试ID 1-5
        user_ids = [1, 2, 3, 4, 5]
        found_users = 0
        
        for user_id in user_ids:
            try:
                request = user_pb2.IdRequest(id=user_id)
                response = self.stub.GetUserById(request)
                
                if response.id:
                    found_users += 1
                    print(f"✅ 找到用户 ID={user_id}: {response.nickName} ({response.mobile})")
                else:
                    print(f"ℹ️  用户 ID={user_id} 不存在")
                    
            except grpc.RpcError as e:
                print(f"ℹ️  用户 ID={user_id} gRPC错误: {e.code()}")
            except Exception as e:
                print(f"❌ 用户 ID={user_id} 其他错误: {e}")
        
        print(f"总共找到 {found_users} 个用户")
        return found_users > 0
    
    def run_all_tests(self):
        """运行所有测试用例"""
        print("🚀 开始运行 GetUserById 函数测试用例")
        print("=" * 50)
        
        test_results = []
        
        # 运行各个测试用例
        test_results.append(self.test_get_existing_user())
        test_results.append(self.test_get_nonexistent_user())
        test_results.append(self.test_get_user_with_invalid_id())
        test_results.append(self.test_multiple_users())
        
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
    test = TestGetUserById()
    test.run_all_tests()
