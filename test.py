from win10toast import ToastNotifier
# 创建一个 ToastNotifier 对象
toaster = ToastNotifier()

# 显示通知
toaster.show_toast(
    title="公文通更新", 
    msg="这是一条通知消息",
    duration=3
    )

