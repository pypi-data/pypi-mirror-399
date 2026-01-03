"""
客户端模块测试 (使用 Mock)
"""
from yz_dubbo import invoke


def test_client_invoke():
    resp = invoke("com.youzan.material.materialcenter.api.service.storage.file.StorageQiniuFileWriteService", "getPublicFileUploadToken", [{
        "channel": "ai_sales",
        "maxSize": 1073741824,
        "fromApp": "ai-sales",
        "operatorType": 1,
        "operatorId": 16595,
        "operatorName": "张三",
        "operatorKdtId": 55,
        "operatorPhone": "13800138000"
    }])
    print(resp)

if __name__ == "__main__":
    test_client_invoke()