#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from web2 import app

if __name__ == '__main__':
    print("\n" + "="*60)
    print("日程记录应用启动中...")
    print("="*60)
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止应用")
    print("="*60 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
