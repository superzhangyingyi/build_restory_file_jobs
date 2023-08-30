# 分支Master：
1. v1.1 和web一样，靠resource_uuid和minor_resource_id来查找所有备份集
3. v1.2(稳定版) 将用户账号密码登录改为apikey登录，不再需要login.py登录

# 分支Feature：
1. v1.3(测试版) 使用minor_resource_id来查找对应的resource_uuid，缩减需要填写的参数，规范了部分写法

# 分支bug： ~**已废除**~
  - 根据jobUUID查找，当作业任务删除后就找不到了
  - 通过控制台确定，软件是通过resource_uuid + minor_resource_id来确定的
