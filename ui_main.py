from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt


class PoemWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("每日诗词")
        self.resize(400, 300)

        # 主垂直布局
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 诗词标题、作者、内容标签
        self.title_label = QLabel("")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 20px;")

        self.author_label = QLabel("")
        self.author_label.setAlignment(Qt.AlignCenter)
        self.author_label.setStyleSheet("font-style: italic; font-size: 14px; color: gray;")

        self.content_label = QLabel("")
        self.content_label.setAlignment(Qt.AlignCenter)
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet("font-size: 16px;")

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.author_label)
        self.layout.addWidget(self.content_label)

        # 底部水平按钮布局
        btn_layout = QHBoxLayout()
        self.next_btn = QPushButton("下一首")
        self.close_btn = QPushButton("关闭")

        btn_layout.addStretch()
        btn_layout.addWidget(self.next_btn)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch()

        self.layout.addLayout(btn_layout)

        # 按钮信号（外部调用需绑定）
        self.next_btn.clicked.connect(self.on_next_clicked)
        self.close_btn.clicked.connect(self.close)

        # 用于外部绑定的回调
        self.next_callback = None

    def on_next_clicked(self):
        if self.next_callback:
            self.next_callback()

    def show_poem(self, poem):
        self.title_label.setText(poem.get("title", ""))
        self.author_label.setText(poem.get("author", ""))
        paragraphs = poem.get("paragraphs", [])
        content = "\n".join(paragraphs)
        self.content_label.setText(content)

        self.show()
        self.activateWindow()

    def closeEvent(self, event):
        # 拦截关闭事件，隐藏窗口，不退出程序
        event.ignore()  # 忽略默认关闭
        self.hide()  # 隐藏窗口
