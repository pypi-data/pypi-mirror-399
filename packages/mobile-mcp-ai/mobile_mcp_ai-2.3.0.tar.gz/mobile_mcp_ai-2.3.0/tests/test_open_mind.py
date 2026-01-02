#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例: 打开Mind应用测试
生成时间: 2025-12-17 10:50:37
"""
import time
import uiautomator2 as u2

PACKAGE_NAME = "com.im30.mind"


def test_main():
    # 连接设备
    d = u2.connect()
    
    # 启动应用
    d.app_start(PACKAGE_NAME)
    time.sleep(3)
    
    # 步骤1: 点击文本 Mind
    d(text='Mind').click()
    time.sleep(1)
    
    # 步骤2: 点击坐标
    d.click(540, 1200)
    time.sleep(1)
    
    # 步骤3: 输入文本
    d(resourceId='com.im30.mind:id/search').set_text('测试')
    time.sleep(1)
    
    print('✅ 测试完成')


if __name__ == '__main__':
    test_main()