# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2024-10-15 18:30:21
@LastEditTime: 2024-11-14 15:22:28
@LastEditors: HuangJianYi
@Description: 
"""
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *
from seven_cloudapp_frame.models.cache_model import *

class MemberSyncJdModel(CacheModel):
    def __init__(self, db_connect_key='db_cloudapp', db_config_dict=None, sub_table=None, db_transaction=None, context=None, is_auto=False):
        super(MemberSyncJdModel, self).__init__(MemberSyncJd, sub_table)
        if not db_config_dict:
            db_config_dict = config.get_value(db_connect_key)
        self.db = MySQLHelper(self.convert_db_config(db_config_dict, is_auto))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    # 方法扩展请继承此类


class MemberSyncJd:
    def __init__(self):
        super(MemberSyncJd, self).__init__()
        self.id = 0
        self.business_id = 0  # 商家标识
        self.scheme_id = 0 # 体系标识
        self.member_telephone = ''  # 会员手机号
        self.user_id = ''  # 客户ID
        self.source_type = 0  # 来源类型(1-其他平台 2-京东)
        self.sync_status = 0  # 同步状态(0-未同步 1-同步中 2-已同步 3-不予同步)
        self.sync_first_date = '1970-01-01 00:00:00.000'  # 首次同步时间
        self.sync_last_date = '1970-01-01 00:00:00.000'  # 最后同步时间

    @classmethod
    def get_field_list(self):
        return ['id', 'business_id', 'scheme_id', 'member_telephone', 'user_id', 'source_type', 'sync_status', 'sync_first_date', 'sync_last_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "member_sync_jd_tb"
