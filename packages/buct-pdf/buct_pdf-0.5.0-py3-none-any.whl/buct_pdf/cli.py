"""命令行接口模块"""

import argparse
import sys
from .core import GetsPdf, LoginError, NetworkError


def main():
    """命令行主程序"""
    parser = argparse.ArgumentParser(description="北化在线PDF下载工具")
    parser.add_argument("--username", help="学号")
    parser.add_argument("--password", help="密码")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式模式")
    parser.add_argument("--gui", "-g", action="store_true", help="图形界面模式")

    args = parser.parse_args()
    
    # 如果请求 GUI 模式，直接启动图形界面
    if args.gui:
        GUI_client()
        return

    # 如果没有提供任何参数，进入交互式模式
    if not args.username or not args.password or args.interactive:
        client()
        return
    
    # 非交互式模式 - 仅登录并保持session
    client = GetsPdf()
    try:
        client.login(args.username, args.password)
        print("登录成功！")
        print("使用 Ctrl+C 退出")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n正在退出...")
    except (LoginError, NetworkError) as e:
        print(f"错误: {str(e)}")
        sys.exit(1)
    finally:
        client.logout()


def client():
    """交互式客户端"""
    client = GetsPdf()
    print("=== 北化在线PDF下载工具 ===")
    
    try:
        username = input("请输入学号: ")
        password = input("请输入密码: ")
        
        client.login(username, password)
        print("登录成功！")

        while True:
            print("\n请选择操作:")
            print("1. 下载PPT(转PDF)")
            print("2. 下载PDF")
            print("3. 退出")

            choice = input("请输入选项 (1/2/3): ")

            if choice == "1":
                url = input("请输入页面uri：")
                output_dir = input("请输入输出目录（回车使用当前目录）：") or "."
                try:
                    pdf_path = client.download_ppt_to_pdf(url, output_dir)
                    print(f"下载完成：{pdf_path}")
                except Exception as e:
                    print(f"下载失败: {str(e)}")
            elif choice == "2":
                url = input("请输入页面uri：")
                output_dir = input("请输入输出目录（回车使用当前目录）：") or "."
                try:
                    pdf_path = client.download_pdf(url, output_dir)
                    print(f"下载完成：{pdf_path}")
                except Exception as e:
                    print(f"下载失败: {str(e)}")
            elif choice == "3":
                print("正在退出...")
                break
            else:
                print("输入错误，请重新选择")

    except (LoginError, NetworkError) as e:
        print(f"错误: {str(e)}")
    except KeyboardInterrupt:
        print("\n用户中断操作")
    finally:
        client.logout()


def GUI_client():
    """图形交互客户端（Tkinter）。

    顶部为账号密码，左侧为PDF链接，右侧为PPT链接，支持多行（\n分隔）。
    用法与 `client()` 相同，但通过图形界面操作。
    """
    import threading
    try:
        import tkinter as tk
        from tkinter import messagebox, filedialog, scrolledtext
    except Exception as e:
        print("无法导入 tkinter：", e)
        return

    client = GetsPdf()

    root = tk.Tk()
    root.title("北化在线PDF下载工具 - GUI")
    root.geometry("1000x700")

    # ----------------- 顶部：账号密码 -----------------
    top_frame = tk.Frame(root)
    top_frame.pack(fill="x", padx=10, pady=8)

    tk.Label(top_frame, text="学号:").pack(side="left")
    username_var = tk.StringVar()
    username_entry = tk.Entry(top_frame, textvariable=username_var, width=20)
    username_entry.pack(side="left", padx=(6, 14))

    tk.Label(top_frame, text="密码:").pack(side="left")
    password_var = tk.StringVar()
    password_entry = tk.Entry(top_frame, textvariable=password_var, show="*", width=20)
    password_entry.pack(side="left", padx=(6, 14))

    login_btn = tk.Button(top_frame, text="登录", width=10)
    login_btn.pack(side="left", padx=6)
    logout_btn = tk.Button(top_frame, text="登出", width=10, state="disabled")
    logout_btn.pack(side="left", padx=6)

    # ----------------- 中间：左右两个文本框（使用 PanedWindow 提供更合理空间分配） -----------------
    middle_pane = tk.PanedWindow(root, orient="horizontal", sashrelief="raised")
    middle_pane.pack(fill="both", expand=True, padx=10, pady=6)

    left_frame = tk.Frame(middle_pane)
    tk.Label(left_frame, text="PDF 链接（每行一个）").pack(anchor="w")
    pdf_text = scrolledtext.ScrolledText(left_frame, wrap="none")
    pdf_text.pack(fill="both", expand=True)

    right_frame = tk.Frame(middle_pane)
    tk.Label(right_frame, text="PPT 链接（每行一个）").pack(anchor="w")
    ppt_text = scrolledtext.ScrolledText(right_frame, wrap="none")
    ppt_text.pack(fill="both", expand=True)

    # 将左右面板加入 PanedWindow，左侧初始较宽
    middle_pane.add(left_frame, minsize=300)
    middle_pane.add(right_frame, minsize=200)

    # ----------------- 底部：一键下载 按钮和日志 -----------------
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(fill="x", padx=10, pady=6)

    def choose_output_dir():
        d = filedialog.askdirectory()
        return d or "."

    download_all_btn = tk.Button(bottom_frame, text="一键下载", width=18, state="disabled")
    download_all_btn.pack(side="left", padx=6)
    choose_dir_btn = tk.Button(bottom_frame, text="选择输出目录", width=14)
    choose_dir_btn.pack(side="left", padx=6)

    status_frame = tk.Frame(root)
    status_frame.pack(fill="both", expand=False, padx=10, pady=(4,10))
    tk.Label(status_frame, text="运行日志:").pack(anchor="w")
    status_text = scrolledtext.ScrolledText(status_frame, height=8, state="disabled")
    status_text.pack(fill="both", expand=True)

    def log(msg: str):
        def _append():
            status_text.config(state="normal")
            status_text.insert("end", msg + "\n")
            status_text.see("end")
            status_text.config(state="disabled")
        root.after(0, _append)

    logged_in = {"val": False}

    def set_controls_after_login(ok: bool):
        if ok:
            login_btn.config(state="disabled")
            logout_btn.config(state="normal")
            download_all_btn.config(state="normal")
            username_entry.config(state="disabled")
            password_entry.config(state="disabled")
            logged_in["val"] = True
        else:
            login_btn.config(state="normal")
            logout_btn.config(state="disabled")
            download_all_btn.config(state="disabled")
            username_entry.config(state="normal")
            password_entry.config(state="normal")
            logged_in["val"] = False

    # ----------------- 操作函数（使用线程） -----------------
    def do_login():
        def task():
            try:
                uname = username_var.get().strip()
                pwd = password_var.get().strip()
                if not uname or not pwd:
                    messagebox.showwarning("提示", "请先输入学号和密码")
                    return
                log("正在登录...")
                client.login(uname, pwd)
                log("登录成功")
                set_controls_after_login(True)
            except (LoginError, NetworkError) as e:
                log(f"登录失败: {e}")
                messagebox.showerror("登录失败", str(e))
        threading.Thread(target=task, daemon=True).start()

    def do_logout():
        def task():
            try:
                client.logout()
            except Exception:
                pass
            set_controls_after_login(False)
            log("已登出")
        threading.Thread(target=task, daemon=True).start()

    def _download_lines(lines, downloader, outdir):
        for raw in lines:
            url = raw.strip()
            if not url:
                continue
            log(f"开始下载: {url}")
            try:
                path = downloader(url, outdir)
                log(f"下载完成: {path}")
            except Exception as e:
                log(f"下载失败 {url}: {e}")

    # 一键下载：优先下载 PDF 列表，然后下载 PPT 列表并转换
    selected_outdir = {"dir": None}

    def choose_dir_clicked():
        d = choose_output_dir()
        if d:
            selected_outdir["dir"] = d
            log(f"已选择输出目录: {d}")

    choose_dir_btn.config(command=choose_dir_clicked)

    def download_all():
        if not logged_in["val"]:
            messagebox.showwarning("未登录", "请先登录后再下载")
            return

        pdf_lines = [l for l in pdf_text.get("1.0", "end").splitlines() if l.strip()]
        ppt_lines = [l for l in ppt_text.get("1.0", "end").splitlines() if l.strip()]

        if not pdf_lines and not ppt_lines:
            messagebox.showinfo("提示", "没有可下载的链接")
            return

        outdir = selected_outdir["dir"] or choose_output_dir()

        download_all_btn.config(state="disabled")

        def task():
            try:
                if pdf_lines:
                    log("开始批量下载 PDF 列表...")
                    _download_lines(pdf_lines, client.download_pdf, outdir)
                if ppt_lines:
                    log("开始批量下载 PPT 列表（将转换为 PDF）...")
                    _download_lines(ppt_lines, client.download_ppt_to_pdf, outdir)
                log("全部任务完成")
            finally:
                root.after(0, lambda: download_all_btn.config(state="normal"))

        threading.Thread(target=task, daemon=True).start()

    # ----------------- 绑定按钮 -----------------
    login_btn.config(command=do_login)
    logout_btn.config(command=do_logout)
    download_all_btn.config(command=download_all)

    # 关闭窗口时确保登出
    def on_close():
        try:
            # 尝试登出（阻塞），确保会话被清理
            client.logout()
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()

