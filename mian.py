# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 09:53:29 2023

@author: 86159
"""

import json
from login import DbackupLogin

# 用户登录 DbackupLogin(用户名, 密码)
user = DbackupLogin('python', '22222222')
[SESSION, COOKIE, TOKEN] = user.dbackupd_login()
resourceUUID = 'b9b25bb0382311ee800000505692225b'
minorResourceID = 'ca65ba1f8f400001d99916a013b02fb0'

# 找到某作业下的所有备份集
def restory_collection(resource_uuid, minor_resource_id):
    url3 = "http://192.168.3.118/d2/r/v2/sets/restore/sets"
    payload = {
        'resource_uuid': resource_uuid,
        'minor_resource_id': minor_resource_id,
        "X-CSRF-Token":TOKEN,
        "module": "file"
    }
    testStr = SESSION.get(url3, params=payload, cookies=COOKIE)
    restoryList = json.loads(testStr.text)['rows']
    print('共'+str(len(restoryList))+'个备份集')
    return restoryList


#正式操作
# =============================================================================
# entries: 要恢复的备份内容
#     全路径用{“dir”:"dirPath"} 单文件用{"file":"path/fileName.txt"}
#     对于没有的路径或文件会 不执行该文件的恢复，其余文件正常恢复不报错
# location: 恢复路径
# =============================================================================
restoryList = restory_collection(resourceUUID, minorResourceID)
#每一个备份集都创建恢复作业
for i in range(len(restoryList)):
    item = restoryList[i]
    data3 = {
        "type": "restore",
        "host_id": item['host_uuid'],
        "agent": item['agent'],
        "source": {
            "id": item['resource_uuid'],
            "name": "file",
            "pool_uuid": item['pool_uuid'],
            "backup_host_id": item['host_uuid'],
            "backup_minor_resource_id": item['minor_resource_id'],
            "seq": item['seq'],
            "entries": [
                {"file": "/backupTest/config.txt"},
                {"file": "/backupTest/4.29/boring.txt"},
                {"file": "/backupTest/4.29/nothing.txt"},
                {"dir": "/backupTest/all"},
                {"dir": "/nosuchDir/all"},
                {"file": "/nosuchDir/all/no.txt"}
            ],
            "time":item['backup_start_time'],
            "catalog_id": restoryList[1]['uuid']
        },
        "target": {
            "id": item['resource_uuid'],
            "name": 'file',
            "location": ""
        },
        "schedule": {
            "start": "2024-08-31 15:11:00",
            "type": "once"
        },
        "options": {
            "channels": 1,
            "location": "/restory/" + item['backup_start_time'].split(' ')[0],
            "existing": "overwrite",
            "path_converter": "",
            "numeric_owner": False
        },
        "subtype": "point_in_time",
        "max_seconds_retry": 600,
        "resumption_buffer_size": 10485760,
        "max_rate_limits": [],
        "precondition": "",
        "name": "auto_create测试作业"+str(i)+"_" +  item['backup_start_time'].split(' ')[0]
    }
    r = SESSION.post('http://192.168.3.118/d2/r/v2/jobs', json=data3, cookies=COOKIE, headers={"X-CSRF-Token":TOKEN})
    print(r.text)
