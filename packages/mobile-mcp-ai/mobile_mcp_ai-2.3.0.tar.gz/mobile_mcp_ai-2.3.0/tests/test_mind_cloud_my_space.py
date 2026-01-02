#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例: Mind云文档我的空间
生成时间: 2025-12-17 11:00:00
"""
import time
import uiautomator2 as u2

PACKAGE_NAME = "com.im30.mind"

# 广告关闭按钮关键词（可自定义）
AD_CLOSE_KEYWORDS = ['关闭', '跳过', 'Skip', 'Close', '×', 'X', '我知道了', '稍后再说']


def smart_wait(d, timeout=10):
    """智能等待页面稳定"""
    d.implicitly_wait(timeout)
    time.sleep(0.5)  # 额外等待动画


def close_ad_if_exists(d):
    """尝试关闭广告弹窗"""
    for keyword in AD_CLOSE_KEYWORDS:
        elem = d(textContains=keyword)
        if elem.exists(timeout=0.5):
            try:
                elem.click()
                print(f'  📢 关闭广告: {keyword}')
                time.sleep(0.5)
                return True
            except:
                pass
    return False


def safe_click(d, selector, timeout=5):
    """安全点击（带等待和重试）"""
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
    smart_wait(d)
    close_ad_if_exists(d)  # 检查广告
    
    # 步骤2: 点击坐标 (756, 2277)
    d.click(756, 2277)
    smart_wait(d)
    close_ad_if_exists(d)  # 检查广告
    
    # 步骤3: 点击坐标 (815, 285)
    d.click(815, 285)
    smart_wait(d)
    close_ad_if_exists(d)  # 检查广告
    
    print('✅ 测试完成')


if __name__ == '__main__':
    test_main()