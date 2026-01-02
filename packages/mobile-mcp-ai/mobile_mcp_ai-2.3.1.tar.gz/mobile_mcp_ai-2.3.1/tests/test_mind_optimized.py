#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例: Mind云文档我的空间_优化版
生成时间: 2025-12-17 11:04:53
"""
import time
import uiautomator2 as u2

PACKAGE_NAME = "com.im30.mind"

# 广告关闭按钮关键词（可自定义）
AD_CLOSE_KEYWORDS = ['关闭', '跳过', 'Skip', 'Close', '×', 'X', '我知道了', '稍后再说']


def smart_wait(d, seconds=1):
    """等待页面稳定"""
    time.sleep(seconds)


def close_ad_if_exists(d, quick=False):
    """尝试关闭广告弹窗（quick=True 时只检查常见的）"""
    keywords = AD_CLOSE_KEYWORDS[:3] if quick else AD_CLOSE_KEYWORDS
    for keyword in keywords:
        elem = d(textContains=keyword)
        if elem.exists(timeout=0.3):  # 缩短超时
            try:
                elem.click()
                print(f'  📢 关闭广告: {keyword}')
                time.sleep(0.3)
                return True
            except:
                pass
    return False


def safe_click(d, selector, timeout=3):
    """安全点击（带等待）"""
    try:
        if selector.exists(timeout=timeout):
            selector.click()
            return True
        return False
    except Exception as e:
        print(f'  ⚠️ 点击失败: {e}')
        return False


def test_main():
    # 连接设备
    d = u2.connect()
    d.implicitly_wait(10)  # 设置全局等待
    
    # 启动应用
    d.app_start(PACKAGE_NAME)
    smart_wait(d)
    
    # 尝试关闭启动广告
    close_ad_if_exists(d)
    
    # 步骤1: 点击文本 'Mind'
    safe_click(d, d(text='Mind'))
    time.sleep(0.5)  # 等待响应
    
    # 步骤2: 点击坐标 (756, 2277)
    d.click(756, 2277)
    time.sleep(0.5)  # 等待响应
    
    # 步骤3: 点击坐标 (815, 285)
    d.click(815, 285)
    time.sleep(0.5)  # 等待响应
    
    print('✅ 测试完成')


if __name__ == '__main__':
    test_main()