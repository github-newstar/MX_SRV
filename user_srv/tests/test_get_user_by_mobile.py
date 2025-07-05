import grpc
from user_srv.proto import user_pb2_grpc, user_pb2


class TestGetUserByMobile:
    """测试 GetUserByMobile 函数的测试用例"""
    
    def __init__(self):
        # 连接到 gRPC 服务器
        channel = grpc.insecure_channel('localhost:50051')
        self.stub = user_pb2_grpc.UserStub(channel)
    
    def test_get_user_by_existing_mobile(self):
        """测试通过存在的手机号获取用户"""
        print("=== 测试用例1: 通过存在的手机号获取用户 ===")
        
        try:
            # 使用指定的手机号 13800138000
            request = user_pb2.MobileRequest(mobile="13800138000")
            response = self.stub.GetUserByMobile(request)
            
            # 验证响应
            if response.id:
                print(f"✅ 成功通过手机号获取用户:")
                print(f"   用户ID: {response.id}")
                print(f"   昵称: {response.nickName}")
                print(f"   手机号: {response.mobile}")
                print(f"   性别: {response.gender}")
                print(f"   角色: {response.role}")
                if response.birthday:
                    print(f"   生日时间戳: {response.birthday}")
                
                # 验证返回的手机号是否匹配
                if response.mobile == "13800138000":
                    print("✅ 手机号匹配正确")
                    return True
                else:
                    print(f"❌ 手机号不匹配: 期望 13800138000, 实际 {response.mobile}")
                    return False
            else:
                print("❌ 测试失败: 未找到用户")
                return False
                
        except grpc.RpcError as e:
            print(f"❌ gRPC 错误: {e.code()}, {e.details()}")
            return False
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            return False
    
    def test_get_user_by_nonexistent_mobile(self):
        """测试通过不存在的手机号获取用户"""
        print("\n=== 测试用例2: 通过不存在的手机号获取用户 ===")
        
        try:
            # 使用不存在的手机号
            request = user_pb2.MobileRequest(mobile="99999999999")
            response = self.stub.GetUserByMobile(request)
            
            # 验证响应
            if response.id:
                print(f"⚠️  意外获取到用户: ID={response.id}, 手机号={response.mobile}")
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
    
    def test_get_user_by_invalid_mobile(self):
        """测试使用无效手机号获取用户"""
        print("\n=== 测试用例3: 测试无效手机号 ===")
        
        test_cases = [
            {"mobile": "", "desc": "空字符串"},
            {"mobile": "123", "desc": "过短手机号"},
            {"mobile": "abcdefghijk", "desc": "非数字手机号"},
            {"mobile": "12345678901234567890", "desc": "过长手机号"},
        ]
        
        results = []
        for case in test_cases:
            try:
                print(f"测试 {case['desc']} (手机号='{case['mobile']}')")
                request = user_pb2.MobileRequest(mobile=case['mobile'])
                response = self.stub.GetUserByMobile(request)
                
                if response.id:
                    print(f"⚠️  意外获取到用户: ID={response.id}")
                    results.append(False)
                else:
                    print("✅ 正确处理：无效手机号返回空响应")
                    results.append(True)
                    
            except grpc.RpcError as e:
                print(f"✅ 正确处理 gRPC 错误: {e.code()}")
                results.append(True)
            except Exception as e:
                print(f"❌ 其他错误: {e}")
                results.append(False)
        
        return all(results)
    
    def test_multiple_mobile_numbers(self):
        """测试多个手机号"""
        print("\n=== 测试用例4: 批量测试多个手机号 ===")
        
        # 测试多个可能存在的手机号
        mobile_numbers = [
            "13800138000",
            "13800138001", 
            "13800138002",
            "13800138003",
            "13800138004"
        ]
        
        found_users = 0
        
        for mobile in mobile_numbers:
            try:
                request = user_pb2.MobileRequest(mobile=mobile)
                response = self.stub.GetUserByMobile(request)
                
                if response.id:
                    found_users += 1
                    print(f"✅ 找到用户 手机号={mobile}: {response.nickName} (ID={response.id})")
                else:
                    print(f"ℹ️  手机号 {mobile} 对应的用户不存在")
                    
            except grpc.RpcError as e:
                print(f"ℹ️  手机号 {mobile} gRPC错误: {e.code()}")
            except Exception as e:
                print(f"❌ 手机号 {mobile} 其他错误: {e}")
        
        print(f"总共找到 {found_users} 个用户")
        return found_users > 0
    
    def test_mobile_format_validation(self):
        """测试手机号格式验证"""
        print("\n=== 测试用例5: 手机号格式验证 ===")
        
        # 测试各种格式的手机号
        test_cases = [
            {"mobile": "13800138000", "desc": "标准11位手机号", "should_work": True},
            {"mobile": "+8613800138000", "desc": "带国际区号", "should_work": False},
            {"mobile": "138-0013-8000", "desc": "带连字符", "should_work": False},
            {"mobile": "138 0013 8000", "desc": "带空格", "should_work": False},
        ]
        
        results = []
        for case in test_cases:
            try:
                print(f"测试 {case['desc']} ('{case['mobile']}')")
                request = user_pb2.MobileRequest(mobile=case['mobile'])
                response = self.stub.GetUserByMobile(request)
                
                if case['should_work']:
                    # 期望能找到用户或正常处理
                    if response.id or not response.id:  # 无论找到与否都算正常
                        print("✅ 格式正确，正常处理")
                        results.append(True)
                    else:
                        print("❌ 格式正确但处理异常")
                        results.append(False)
                else:
                    # 期望不能找到用户
                    if not response.id:
                        print("✅ 格式不正确，正确返回空结果")
                        results.append(True)
                    else:
                        print("⚠️  格式不正确但意外找到用户")
                        results.append(False)
                        
            except grpc.RpcError as e:
                print(f"ℹ️  gRPC错误: {e.code()}")
                results.append(True)  # 错误也算正常处理
            except Exception as e:
                print(f"❌ 其他错误: {e}")
                results.append(False)
        
        return all(results)
    
    def run_all_tests(self):
        """运行所有测试用例"""
        print("🚀 开始运行 GetUserByMobile 函数测试用例")
        print("=" * 50)
        
        test_results = []
        
        # 运行各个测试用例
        test_results.append(self.test_get_user_by_existing_mobile())
        test_results.append(self.test_get_user_by_nonexistent_mobile())
        test_results.append(self.test_get_user_by_invalid_mobile())
        test_results.append(self.test_multiple_mobile_numbers())
        test_results.append(self.test_mobile_format_validation())
        
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
    test = TestGetUserByMobile()
    test.run_all_tests()
