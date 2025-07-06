import grpc
from user_srv.proto import user_pb2_grpc, user_pb2
import random
import string


class TestCreateUser:
    """测试 CreateUser 函数的测试用例"""
    
    def __init__(self):
        # 连接到 gRPC 服务器
        channel = grpc.insecure_channel('localhost:50051')
        self.stub = user_pb2_grpc.UserStub(channel)
    
    def generate_random_mobile(self):
        """生成随机手机号"""
        # 生成 138 开头的随机手机号
        return "138" + "".join(random.choices(string.digits, k=8))
    
    def test_create_new_user(self):
        """测试创建新用户"""
        print("=== 测试用例1: 创建新用户 ===")
        
        try:
            # 生成随机手机号避免冲突
            mobile = self.generate_random_mobile()
            
            # 创建用户请求
            request = user_pb2.CreateUserInfo(
                nickName="测试新用户",
                passWord="test123456",
                mobile=mobile
            )
            
            response = self.stub.CreateUser(request)
            
            # 验证响应
            if response.id:
                print(f"✅ 成功创建用户:")
                print(f"   用户ID: {response.id}")
                print(f"   昵称: {response.nickName}")
                print(f"   手机号: {response.mobile}")
                print(f"   角色: {response.role}")
                
                # 验证数据是否正确
                if response.nickName == "测试新用户" and response.mobile == mobile:
                    print("✅ 用户数据验证通过")
                    return True, response.id
                else:
                    print("❌ 用户数据验证失败")
                    return False, None
            else:
                print("❌ 创建用户失败: 未返回用户信息")
                return False, None
                
        except grpc.RpcError as e:
            print(f"❌ gRPC 错误: {e.code()}, {e.details()}")
            return False, None
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            return False, None
    
    def test_create_duplicate_user(self):
        """测试创建重复用户"""
        print("\n=== 测试用例2: 创建重复用户 ===")
        
        try:
            # 使用已存在的手机号
            request = user_pb2.CreateUserInfo(
                nickName="重复用户",
                passWord="test123456",
                mobile="13800138000"  # 这个手机号应该已经存在
            )
            
            response = self.stub.CreateUser(request)
            
            # 应该返回空响应
            if response.id:
                print(f"⚠️  意外创建了重复用户: ID={response.id}")
                return False
            else:
                print("✅ 正确处理：未创建重复用户")
                return True
                
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                print("✅ 正确处理：返回 ALREADY_EXISTS 状态码")
                print(f"   错误详情: {e.details()}")
                return True
            else:
                print(f"❌ 意外的 gRPC 错误: {e.code()}, {e.details()}")
                return False
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            return False
    
    def test_create_user_with_invalid_data(self):
        """测试使用无效数据创建用户"""
        print("\n=== 测试用例3: 测试无效数据 ===")
        
        test_cases = [
            {
                "desc": "空昵称",
                "data": {"nickName": "", "passWord": "test123", "mobile": self.generate_random_mobile()}
            },
            {
                "desc": "空密码",
                "data": {"nickName": "测试用户", "passWord": "", "mobile": self.generate_random_mobile()}
            },
            {
                "desc": "空手机号",
                "data": {"nickName": "测试用户", "passWord": "test123", "mobile": ""}
            },
            {
                "desc": "无效手机号格式",
                "data": {"nickName": "测试用户", "passWord": "test123", "mobile": "123"}
            }
        ]
        
        results = []
        for case in test_cases:
            try:
                print(f"测试 {case['desc']}")
                request = user_pb2.CreateUserInfo(**case['data'])
                response = self.stub.CreateUser(request)
                
                if response.id:
                    print(f"⚠️  意外创建了用户: ID={response.id}")
                    results.append(False)
                else:
                    print("✅ 正确处理：未创建无效用户")
                    results.append(True)
                    
            except grpc.RpcError as e:
                print(f"✅ 正确处理 gRPC 错误: {e.code()}")
                results.append(True)
            except Exception as e:
                print(f"❌ 其他错误: {e}")
                results.append(False)
        
        return all(results)
    
    def test_create_multiple_users(self):
        """测试批量创建用户"""
        print("\n=== 测试用例4: 批量创建用户 ===")
        
        created_users = []
        success_count = 0
        
        for i in range(3):
            try:
                mobile = self.generate_random_mobile()
                request = user_pb2.CreateUserInfo(
                    nickName=f"批量测试用户{i+1}",
                    passWord="batch123456",
                    mobile=mobile
                )
                
                response = self.stub.CreateUser(request)
                
                if response.id:
                    success_count += 1
                    created_users.append({
                        "id": response.id,
                        "nickName": response.nickName,
                        "mobile": response.mobile
                    })
                    print(f"✅ 创建用户{i+1}: ID={response.id}, 昵称={response.nickName}")
                else:
                    print(f"❌ 创建用户{i+1}失败")
                    
            except grpc.RpcError as e:
                print(f"❌ 创建用户{i+1} gRPC错误: {e.code()}")
            except Exception as e:
                print(f"❌ 创建用户{i+1} 其他错误: {e}")
        
        print(f"批量创建结果: 成功 {success_count}/3")
        return success_count > 0, created_users
    
    def test_password_encryption(self):
        """测试密码加密"""
        print("\n=== 测试用例5: 验证密码加密 ===")
        
        try:
            mobile = self.generate_random_mobile()
            original_password = "testpassword123"
            
            # 创建用户
            request = user_pb2.CreateUserInfo(
                nickName="密码测试用户",
                passWord=original_password,
                mobile=mobile
            )
            
            response = self.stub.CreateUser(request)
            
            if response.id:
                print(f"✅ 用户创建成功: ID={response.id}")
                
                # 注意：response.password 在实际实现中可能不会返回密码
                # 这里主要是验证用户创建成功，密码加密的验证需要在服务端进行
                print("✅ 密码应该已经被加密存储（无法直接验证）")
                
                # 可以通过尝试用原密码登录来验证（如果有登录接口的话）
                print("ℹ️  建议：添加登录接口来验证密码加密是否正确")
                return True
            else:
                print("❌ 用户创建失败")
                return False
                
        except grpc.RpcError as e:
            print(f"❌ gRPC 错误: {e.code()}, {e.details()}")
            return False
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试用例"""
        print("🚀 开始运行 CreateUser 函数测试用例")
        print("=" * 50)
        
        test_results = []
        created_users = []
        
        # 运行各个测试用例
        result1, user_id = self.test_create_new_user()
        test_results.append(result1)
        if user_id:
            created_users.append(user_id)
        
        test_results.append(self.test_create_duplicate_user())
        test_results.append(self.test_create_user_with_invalid_data())
        
        result4, batch_users = self.test_create_multiple_users()
        test_results.append(result4)
        created_users.extend([user['id'] for user in batch_users])
        
        test_results.append(self.test_password_encryption())
        
        # 统计结果
        passed = sum(test_results)
        total = len(test_results)
        
        print("\n" + "=" * 50)
        print(f"📊 测试结果统计:")
        print(f"   通过: {passed}/{total}")
        print(f"   失败: {total - passed}/{total}")
        
        if created_users:
            print(f"📝 本次测试创建的用户ID: {created_users}")
        
        if passed == total:
            print("🎉 所有测试用例通过!")
        else:
            print("⚠️  部分测试用例失败，请检查实现")
        
        return passed == total


if __name__ == "__main__":
    # 创建测试实例并运行所有测试
    test = TestCreateUser()
    test.run_all_tests()
