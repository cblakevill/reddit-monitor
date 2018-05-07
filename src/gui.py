import time
import winsound
from PyQt5.QtMultimedia import QSound
from config_manager import ConfigManager
from updater import (
    Updater,
    UpdaterException
)
from PyQt5.QtCore import (
    QSize,
    QRect,
    Qt
)
from PyQt5.QtWidgets import (
    QWidget,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QSizePolicy,
    QLabel,
    QAbstractItemView,
    QCheckBox,
    QMessageBox,
    QStatusBar,
    QMainWindow
)
from PyQt5.QtGui import QColor, QIcon


class GUI(QMainWindow):
    FRAME_WIDTH = 700
    FRAME_HEIGHT = 600
    FRAME_BORDER = 20

    def __init__(self, config_man: ConfigManager, updater: Updater):
        super(GUI, self).__init__()

        self._config_man = config_man
        self._updater = updater

        self._subreddit_list = QListWidget()
        self._subreddit_text_field = QLineEdit()
        self._subreddit_add_btn = QPushButton()
        self._subreddit_del_btn = QPushButton()
        self._filter_text_field = QLineEdit()
        self._filter_add_btn = QPushButton()
        self._filter_del_btn = QPushButton()
        self._filt_rb_include = QRadioButton("Include")
        self._filt_rb_exclude = QRadioButton("Exclude")
        self._filter_phrase_list = QListWidget()
        self._sound_checkbox = CheckBox("Sound", self._sound_notify)
        self._popup_checkbox = CheckBox("Popup", self._popup_notify)
        self._notification_checkboxes = [self._sound_checkbox, self._popup_checkbox]
        self._update_button = QPushButton("Update")
        self._notification_sound = QSound(self._config_man.properties['notification_sound_path'])
        self._thread_list = QListWidget()
        self._status_bar = QStatusBar()
        self._last_updated_label = QLabel()
        self._refresh_rate_select = QComboBox()
        self._popup = None

        self._init_properties()
        self._init_layout()
        self._init_bindings()

    def _init_layout(self):
        self.setBaseSize(self.FRAME_WIDTH, self.FRAME_HEIGHT)
        self.setGeometry(QRect(100, 100, self.FRAME_WIDTH, self.FRAME_HEIGHT))

        self._subreddit_list.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self._subreddit_text_field.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self._subreddit_add_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._subreddit_del_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._filter_text_field.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self._filter_add_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._filter_del_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._filt_rb_include.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._filt_rb_exclude.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._filter_phrase_list.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        for checkbox in self._notification_checkboxes:
            checkbox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self._refresh_rate_select.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self._update_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        subreddit_box = QHBoxLayout()
        subreddit_box.addWidget(self._subreddit_text_field)
        subreddit_box.addWidget(self._subreddit_add_btn)
        subreddit_box.addWidget(self._subreddit_del_btn)

        filter_box = QHBoxLayout()
        filter_box.addWidget(self._filter_text_field)
        filter_box.addWidget(self._filter_add_btn)
        filter_box.addWidget(self._filter_del_btn)

        refresh_rate_box = QHBoxLayout()
        label = QLabel("Refresh rate")
        label.setFixedSize(70, 20)
        refresh_rate_box.addWidget(label)
        refresh_rate_box.addWidget(self._refresh_rate_select)
        refresh_rate_box.addSpacing(5)
        label = QLabel("mins")
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        refresh_rate_box.addWidget(label)

        option_box = QVBoxLayout()
        label = QLabel("Subreddits")
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        option_box.addWidget(label)
        option_box.addWidget(self._subreddit_list)
        option_box.addItem(subreddit_box)
        option_box.addSpacing(self.FRAME_BORDER)
        label = QLabel("Filter phrases")
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        option_box.addWidget(label)
        option_box.addWidget(self._filter_phrase_list)
        option_box.addItem(filter_box)
        option_box.addWidget(self._filt_rb_include)
        option_box.addWidget(self._filt_rb_exclude)
        option_box.addSpacing(self.FRAME_BORDER)
        for checkbox in self._notification_checkboxes:
            option_box.addWidget(checkbox)
        option_box.addSpacing(self.FRAME_BORDER)
        option_box.addItem(refresh_rate_box)
        option_box.addSpacing(self.FRAME_BORDER)
        option_box.addWidget(self._update_button)

        self._thread_list.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self._thread_list.setIconSize(QSize(200, 200))
        self._thread_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        self._subreddit_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._filter_phrase_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._thread_list.setSelectionMode(QAbstractItemView.NoSelection)

        hbox = QHBoxLayout()
        hbox.addItem(option_box)
        hbox.addWidget(self._thread_list)

        main = QWidget()
        main.setLayout(hbox)
        self.setCentralWidget(main)

        self.setStatusBar(self._status_bar)
        self._status_bar.addWidget(self._last_updated_label)

    def _init_bindings(self):
        self._updater.updater_task.update.connect(self.update_reddit_posts)

        self._update_button.clicked.connect(self.update_reddit_posts)
        self._subreddit_text_field.returnPressed.connect(self._add_subreddit)
        self._filter_add_btn.pressed.connect(self._add_filter_phrase)
        self._filter_text_field.returnPressed.connect(self._add_filter_phrase)
        self._filter_del_btn.pressed.connect(self._del_filter_phrase)
        self._subreddit_add_btn.clicked.connect(self._add_subreddit)
        self._subreddit_del_btn.clicked.connect(self._del_subreddit)
        self._sound_checkbox.stateChanged.connect(lambda state: self._config_man.set('sound_notify', state))
        self._popup_checkbox.stateChanged.connect(lambda state: self._config_man.set('popup_notify', state))
        self._filt_rb_include.toggled.connect(self._change_filter_mode)
        self._filt_rb_exclude.toggled.connect(self._change_filter_mode)
        self._refresh_rate_select.currentIndexChanged.connect(lambda rate: self._updater.set_refresh_rate((rate+1)*60))

    def _init_properties(self):
        for sub in self._config_man.properties['subreddits']:
            self._subreddit_list.addItem(QListWidgetItem(sub.lower()))

        for phrase in self._config_man.properties['filter_phrases']:
            self._filter_phrase_list.addItem(QListWidgetItem(phrase))

        if self._config_man.properties['filter_mode'] == 'exclude':
            self._filt_rb_exclude.setChecked(True)
        else:
            self._filt_rb_include.setChecked(True)

        checked = True if self._config_man.properties['sound_notify'] == 2 else False
        self._sound_checkbox.setChecked(checked)
        checked = True if self._config_man.properties['popup_notify'] == 2 else False
        self._popup_checkbox.setChecked(checked)

        self._last_updated_label.setText("last updated: " +
                                         time.strftime("%d/%m/%y %I:%M%p",
                                                       time.localtime(self._config_man.properties['last_updated'])))

        self._subreddit_add_btn.setIcon(QIcon("../resources/add_button.png"))
        self._subreddit_del_btn.setIcon(QIcon("../resources/del_button.png"))
        self._filter_add_btn.setIcon(QIcon("../resources/add_button.png"))
        self._filter_del_btn.setIcon(QIcon("../resources/del_button.png"))

        for i in range(1, 61):
            self._refresh_rate_select.addItem(str(i))
        self._refresh_rate_select.setCurrentText(str(self._config_man.properties['refresh_rate']//60))

    def update_reddit_posts(self):
        try:
            new_threads = self._updater.update()

            for thread in new_threads:
                item = ThreadItem(thread)
                self._thread_list.addItem(item.stub)
                self._thread_list.setItemWidget(item.stub, item.delegate)
            self._thread_list.scrollToBottom()

            if len(new_threads) != 0:
                for checkbox in self._notification_checkboxes:
                    checkbox.execute_if_checked()

            self._last_updated_label.setText("last updated: " + time.strftime("%d/%m/%y %I:%M%p", time.localtime()))
        except UpdaterException:
            pass

    def _add_subreddit(self):
        entry = self._subreddit_text_field.text().lower().replace(" ", "")
        if not self._config_man.properties['subreddits'].__contains__(entry) and entry != "":
            self._subreddit_list.addItem(QListWidgetItem(entry))
            self._config_man.properties['subreddits'].append(entry)
        self._subreddit_text_field.clear()

    def _add_filter_phrase(self):
        entry = self._filter_text_field.text().lower()
        if not self._config_man.properties['filter_phrases'].__contains__(entry) and entry != "":
            self._filter_phrase_list.addItem(QListWidgetItem(entry))
            self._config_man.properties['filter_phrases'].append(entry)
        self._filter_text_field.clear()

    def _del_subreddit(self):
        items = self._subreddit_list.selectedItems()
        for item in items:
            row = self._subreddit_list.row(item)
            self._subreddit_list.takeItem(row)
            try:
                self._config_man.properties['subreddits'].remove(item.text())
            except ValueError:
                pass

    def _del_filter_phrase(self):
        items = self._filter_phrase_list.selectedItems()
        for item in items:
            row = self._filter_phrase_list.row(item)
            self._filter_phrase_list.takeItem(row)
            try:
                self._config_man.properties['filter_phrases'].remove(item.text())
            except ValueError:
                pass

    def closeEvent(self, a0):
        self._config_man.save()

    def _sound_notify(self):
        if self._config_man.properties['notification_sound_path'] == "":
            winsound.MessageBeep()
        else:
            self._notification_sound.play()

    def _popup_notify(self):
        self._popup = QMessageBox(QMessageBox.NoIcon, "Reddit Monitor", "")
        self._popup.show()
        self._popup.setWindowState(self._popup.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self._popup.activateWindow()

    def _change_filter_mode(self):
        if self._filt_rb_exclude.isChecked():
            self._config_man.set('filter_mode', 'exclude')
        else:
            self._config_man.set('filter_mode', 'include')


class ThreadItem:

    _thread_count = 0

    def __init__(self, thread):
        super(ThreadItem, self).__init__()

        self.stub = QListWidgetItem()
        self.delegate = QWidget()

        self.stub.setSizeHint(QSize(0, 100))

        if ThreadItem._thread_count % 2 == 0:
            bg = QColor(0xffffff)
        else:
            bg = QColor(0xefefef)

        self.stub.setBackground(bg)

        layout = QVBoxLayout()
        title = QLabel(thread['title'])
        sub = QLabel(thread['subreddit_name_prefixed'])
        link = QLabel("<a href='https://reddit.com" + thread['permalink'] + "'>link</a>")

        title.setWordWrap(True)
        sub.setWordWrap(True)
        link.setOpenExternalLinks(True)

        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addWidget(link)

        self.delegate.setLayout(layout)

        ThreadItem._thread_count += 1


class CheckBox(QCheckBox):
    def __init__(self, title, func):
        super(CheckBox, self).__init__(title)
        self.func = func

    def execute_if_checked(self):
        if self.isChecked():
            self.func()
