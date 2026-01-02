#!/usr/bin/env python3
"""
buct-pdf 核心功能测试
"""

import unittest
from unittest.mock import Mock, patch
import requests
from buct_pdf.core import GetsPdf, LoginError, NetworkError


class TestGetsPdf(unittest.TestCase):
    
    def setUp(self):
        self.downloader = GetsPdf()
    
    def test_init(self):
        """测试初始化"""
        self.assertFalse(self.downloader.logged_in)
        self.assertEqual(self.downloader.base_url, "https://course.buct.edu.cn")
        self.assertIsInstance(self.downloader.session, requests.Session)
    
    def test_is_logged_in(self):
        """测试登录状态检查"""
        self.assertFalse(self.downloader.is_logged_in())
        self.downloader.logged_in = True
        self.assertTrue(self.downloader.is_logged_in())
    
    def test_set_base_url(self):
        """测试设置基础URL"""
        new_url = "https://test.example.com"
        self.downloader.set_base_url(new_url)
        self.assertEqual(self.downloader.base_url, new_url)
        
        # 测试URL末尾斜杠处理
        new_url_with_slash = "https://test.example.com/"
        self.downloader.set_base_url(new_url_with_slash)
        self.assertEqual(self.downloader.base_url, "https://test.example.com")
    
    def test_get_session_not_logged_in(self):
        """测试未登录时获取session"""
        with self.assertRaises(LoginError):
            self.downloader.get_session()
    
    def test_download_ppt_not_logged_in(self):
        """测试未登录时下载PPT"""
        with self.assertRaises(LoginError):
            self.downloader.download_ppt_to_pdf("http://example.com")
    
    def test_download_pdf_not_logged_in(self):
        """测试未登录时下载PDF"""
        with self.assertRaises(LoginError):
            self.downloader.download_pdf("http://example.com")
    
    @patch('requests.Session.post')
    def test_login_success(self, mock_post):
        """测试登录成功"""
        # 模拟成功登录的响应
        mock_response = Mock()
        mock_response.url = "https://course.buct.edu.cn/dashboard"
        mock_post.return_value = mock_response
        
        result = self.downloader.login("test_user", "test_pass")
        
        self.assertTrue(result)
        self.assertTrue(self.downloader.logged_in)
        mock_post.assert_called_once()
    
    @patch('requests.Session.post')
    def test_login_failure(self, mock_post):
        """测试登录失败"""
        # 模拟登录失败的响应
        mock_response = Mock()
        mock_response.url = "https://course.buct.edu.cn/meol/loginCheck.do"
        mock_post.return_value = mock_response
        
        with self.assertRaises(LoginError):
            self.downloader.login("wrong_user", "wrong_pass")
        
        self.assertFalse(self.downloader.logged_in)
    
    @patch('requests.Session.post')
    def test_login_timeout(self, mock_post):
        """测试登录超时"""
        mock_post.side_effect = requests.exceptions.Timeout()
        
        with self.assertRaises(NetworkError):
            self.downloader.login("test_user", "test_pass")
    
    @patch('requests.Session.post')
    def test_login_connection_error(self, mock_post):
        """测试连接错误"""
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        with self.assertRaises(NetworkError):
            self.downloader.login("test_user", "test_pass")
    
    @patch('requests.Session.get')
    def test_logout(self, mock_get):
        """测试注销"""
        # 设置为已登录状态
        self.downloader.logged_in = True
        
        # 测试正常注销
        self.downloader.logout()
        
        self.assertFalse(self.downloader.logged_in)
        self.assertIsInstance(self.downloader.session, requests.Session)
    
    def test_logout_with_exception(self):
        """测试注销时出现异常"""
        # 设置为已登录状态
        self.downloader.logged_in = True
        
        # 模拟session.get抛出异常
        with patch.object(self.downloader.session, 'get', side_effect=Exception("Network error")):
            self.downloader.logout()
        
        # 即使出现异常，也应该清理本地状态
        self.assertFalse(self.downloader.logged_in)


if __name__ == '__main__':
    unittest.main()