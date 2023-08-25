# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 10:38:23 2023

@author: 86159
"""

import json
from login import DbackupLogin

# 用户登录 DbackupLogin(用户名, 密码)
user = DbackupLogin('python', '22222222')
[SESSION, COOKIE, TOKEN] = user.dbackupd_login()
JobUUID = 'af7c838a3a7311ee800000505692225b'

# 根据jobUUID找到该作业的所有备份集
def jobUUID_backupd_collection(JobUUID):
    # 找到该作业对应的resource_uuid (/d2/r/v2/sets/restore/sets中传参用到)
    url3 = "http://192.168.3.118/d2/r/v2/jobs"
    payload = {'uuid':JobUUID, "X-CSRF-Token":TOKEN}
    testStr = SESSION.get(url3, params=payload, cookies=COOKIE)
    resourceUUID = json.loads(testStr.text)['rows'][0]['source']['id']
    # 找到该资源的所有备份集(包含多个作业的备份集)
    url3 = "http://192.168.3.118/d2/r/v2/sets/restore/sets"
    payload = {'module': 'file', 'resource_uuid':resourceUUID, "X-CSRF-Token":TOKEN}
    testStr = SESSION.get(url3, params=payload, cookies=COOKIE)
    restoryList = json.loads(testStr.text)['rows']
    # 根据JobUUID找到某作业的所有备份集
    useList = []
    for item in restoryList:
        if(item['definition_uuid'] == JobUUID):
            useList.append(item)
    print('该作业共' + str(len(useList)) + '个备份集')
    return useList

#正式操作
# =============================================================================
# entries: 要恢复的备份内容
#     全路径用{“dir”:"dirPath"} 单文件用{"file":"path/fileName.txt"}
#     对于没有的路径或文件会 不执行该文件的恢复，其余文件正常恢复不报错
# location: 恢复路径
# =============================================================================
restoryList = jobUUID_backupd_collection(JobUUID)

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
        "name": "auto_create测试作业"+str(i+1)+"_" +  item['backup_start_time'].split(' ')[0]
    }
    r = SESSION.post('http://192.168.3.118/d2/r/v2/jobs', json=data3, cookies=COOKIE, headers={"X-CSRF-Token":TOKEN})
    print(r.text)

# =============================================================================
# "entries": [
#     {"file": "/backupTest/config.txt"},
#     {"file": "/backupTest/4.29/boring.txt"},
#     {"file": "/backupTest/nothisone.txt"}
# ],
# =============================================================================


